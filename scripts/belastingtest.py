#!/usr/bin/env python3
"""Belastingtest voor Ollama: N gelijktijdige leerlingen op hetzelfde model.

Stuurt N gelijktijdige streaming-aanvragen naar /api/chat en meet per
"leerling" de tijd tot de eerste token en de generatiesnelheid.
Alleen standaardbibliotheek, geen installatie nodig.

Voorbeelden:
    python scripts/belastingtest.py
    python scripts/belastingtest.py --model llama3.1:8b --users 25
    python scripts/belastingtest.py --users 10 --stagger 2     # rustiger opbouw
"""
import argparse
import json
import statistics
import threading
import time
import urllib.request

PROMPTS = [
    "Leg in eenvoudige woorden uit wat een netwerk is.",
    "Geef drie tips om beter te leren voor een toets.",
    "Wat is het verschil tussen een CPU en een GPU?",
    "Schrijf een korte sollicitatiebrief voor een bijbaan in de horeca.",
    "Hoe werkt een wachtwoordmanager en waarom is dat veilig?",
    "Leg uit wat fotosynthese is aan een brugklasser.",
]


def een_leerling(nr, args, resultaten):
    prompt = PROMPTS[nr % len(PROMPTS)]
    body = json.dumps({
        "model": args.model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "keep_alive": -1,
        "options": {"num_predict": args.num_predict},
    }).encode()
    req = urllib.request.Request(
        f"{args.host}/api/chat", data=body,
        headers={"Content-Type": "application/json"},
    )
    res = {"nr": nr, "fout": None, "ttft": None, "totaal": None,
           "tokens": 0, "tps": None}
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as r:
            for regel in r:
                if not regel.strip():
                    continue
                chunk = json.loads(regel)
                if res["ttft"] is None and chunk.get("message", {}).get("content"):
                    res["ttft"] = time.perf_counter() - start
                if chunk.get("done"):
                    res["tokens"] = chunk.get("eval_count", 0)
                    dur = chunk.get("eval_duration", 0) / 1e9
                    if dur > 0:
                        res["tps"] = res["tokens"] / dur
    except Exception as e:  # noqa: BLE001 - elke fout telt als mislukte aanvraag
        res["fout"] = f"{type(e).__name__}: {e}"
    res["totaal"] = time.perf_counter() - start
    resultaten.append(res)


def pct(waarden, p):
    if not waarden:
        return float("nan")
    s = sorted(waarden)
    return s[min(len(s) - 1, int(round(p / 100 * (len(s) - 1))))]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="http://localhost:11434")
    ap.add_argument("--model", default="llama3.1:8b")
    ap.add_argument("--users", type=int, default=25)
    ap.add_argument("--num-predict", type=int, default=200,
                    help="max. tokens per antwoord (default 200)")
    ap.add_argument("--stagger", type=float, default=0.0,
                    help="seconden totaal waarover de starts worden gespreid (0 = allemaal tegelijk)")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--no-warmup", action="store_true",
                    help="sla de opwarmaanvraag over")
    args = ap.parse_args()

    if not args.no_warmup:
        print(f"Model {args.model} opwarmen (laden in VRAM)...")
        w = []
        een_leerling(0, argparse.Namespace(**{**vars(args), "num_predict": 5}), w)
        if w[0]["fout"]:
            raise SystemExit(f"Opwarmen mislukt: {w[0]['fout']}")

    print(f"{args.users} gelijktijdige aanvragen, max {args.num_predict} tokens elk"
          + (f", gespreid over {args.stagger}s" if args.stagger else "") + "...")
    resultaten, threads = [], []
    t0 = time.perf_counter()
    for i in range(args.users):
        t = threading.Thread(target=een_leerling, args=(i, args, resultaten))
        threads.append(t)
        t.start()
        if args.stagger and args.users > 1:
            time.sleep(args.stagger / (args.users - 1))
    for t in threads:
        t.join()
    wand = time.perf_counter() - t0

    goed = [r for r in resultaten if not r["fout"]]
    fout = [r for r in resultaten if r["fout"]]
    ttfts = [r["ttft"] for r in goed if r["ttft"] is not None]
    tps = [r["tps"] for r in goed if r["tps"]]
    totaal_tokens = sum(r["tokens"] for r in goed)

    print("\n nr | eerste token | totaal | tokens | tok/s")
    print("----+--------------+--------+--------+-------")
    for r in sorted(resultaten, key=lambda x: x["nr"]):
        if r["fout"]:
            print(f"{r['nr']:>3} | FOUT: {r['fout'][:60]}")
        else:
            print(f"{r['nr']:>3} | {r['ttft'] or 0:>10.1f}s | {r['totaal']:>5.1f}s | "
                  f"{r['tokens']:>6} | {r['tps'] or 0:>5.1f}")

    print("\n== Samenvatting ==")
    print(f"Geslaagd / mislukt      : {len(goed)} / {len(fout)}")
    print(f"Totale looptijd         : {wand:.1f}s")
    if ttfts:
        print(f"Eerste token  mediaan   : {statistics.median(ttfts):.1f}s")
        print(f"Eerste token  p95 / max : {pct(ttfts, 95):.1f}s / {max(ttfts):.1f}s")
    if tps:
        print(f"Snelheid per leerling   : mediaan {statistics.median(tps):.1f} tok/s, "
              f"traagste {min(tps):.1f} tok/s")
    print(f"Totale doorvoer         : {totaal_tokens / wand:.1f} tok/s over alle leerlingen")
    print("\nTip: draai tijdens de test 'ollama ps' in een tweede venster; "
          "staat er CPU bij, dan is het VRAM vol.")
    print("Richtlijn: ~5 tok/s per leerling leest nog prettig; eerste token < 10s is acceptabel.")


if __name__ == "__main__":
    main()
