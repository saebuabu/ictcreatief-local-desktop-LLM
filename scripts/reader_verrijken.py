#!/usr/bin/env python3
"""Verrijk PDF-readers met beschrijvingen van afbeeldingen en schema's.

Per pdf wordt de tekst per pagina uitgelezen. Afbeeldingen en schema's laat
een lokaal vision-model (via Ollama) beschrijven; de beschrijving wordt op de
plek van het plaatje in de tekst gezet. Resultaat: een markdown-bestand per
reader met "Pagina N"-kopjes, klaar voor scripts/upload_readers.py.

- Ingesloten afbeeldingen (foto's, plaatjes) worden los beschreven.
- Schema's zijn vaak vectortekeningen en geen afbeelding: bevat een pagina veel
  tekenelementen en geen ingesloten afbeelding, dan wordt de hele pagina
  gerenderd en beschreven (--min-tekeningen, 0 = uit).
- Beschrijvingen worden gecachet (naast de uitvoer), dus stoppen en hervatten
  kan, en opnieuw draaien is goedkoop.

Vereist: pip install pymupdf   (Ollama met een vision-model, bv. qwen3-vl)

Voorbeelden:
    python scripts/reader_verrijken.py C:\readers C:\readers_md --dry-run
    python scripts/reader_verrijken.py C:\readers C:\readers_md
    python scripts/reader_verrijken.py C:\readers C:\readers_md --model llama3.2-vision:11b
"""
import argparse
import base64
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF ontbreekt: pip install pymupdf")

PROMPT = (
    "Beschrijf deze afbeelding voor een MBO-student die zich voorbereidt op een examen. "
    "Is het een schema, diagram, tabel of grafiek: noem alle stappen, onderdelen, labels, "
    "pijlen/verbanden en getallen precies zoals ze er staan. Is het een foto of illustratie: "
    "beschrijf kort wat er te zien is. Verzin niets en gok niet. Is er alleen decoratie "
    "(logo, lijn, achtergrond), antwoord dan alleen met: GEEN. Antwoord in het Nederlands."
)


def beschrijf(args, png_bytes):
    body = json.dumps({
        "model": args.model,
        "messages": [{"role": "user", "content": PROMPT,
                      "images": [base64.b64encode(png_bytes).decode()]}],
        "stream": False,
        "keep_alive": args.keep_alive,
        "options": {"temperature": 0.1, "num_predict": args.num_predict},
    }).encode()
    req = urllib.request.Request(f"{args.host}/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=args.timeout) as r:
        tekst = json.loads(r.read())["message"]["content"]
    return re.sub(r"<think>.*?</think>", "", tekst, flags=re.S).strip()


def beschrijf_gecachet(args, cache, cache_pad, png_bytes):
    sleutel = hashlib.sha1(png_bytes + args.model.encode()).hexdigest()
    if sleutel not in cache:
        cache[sleutel] = beschrijf(args, png_bytes)
        cache_pad.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return cache[sleutel]


def afbeeldingen_van_pagina(args, doc, pagina):
    """Geeft lijst (soort, png_bytes) voor deze pagina."""
    resultaat = []
    gezien = set()
    for img in pagina.get_images(full=True):
        xref = img[0]
        if xref in gezien:
            continue
        gezien.add(xref)
        try:
            pix = fitz.Pixmap(doc, xref)
            if pix.width < args.min_px or pix.height < args.min_px:
                continue
            if pix.n - pix.alpha >= 4:  # CMYK -> RGB
                pix = fitz.Pixmap(fitz.csRGB, pix)
            resultaat.append(("afbeelding", pix.tobytes("png")))
        except Exception as e:  # kapotte of exotische afbeelding
            print(f"   waarschuwing: afbeelding {xref} overgeslagen ({e})")
    if not resultaat and args.min_tekeningen and len(pagina.get_drawings()) >= args.min_tekeningen:
        pix = pagina.get_pixmap(dpi=args.dpi)
        resultaat.append(("schema (hele pagina)", pix.tobytes("png")))
    return resultaat


def verwerk_pdf(args, pdf, uit_map, dry):
    doc = fitz.open(pdf)
    cache_pad = uit_map / f"{pdf.stem}.beschrijvingen.json"
    cache = json.loads(cache_pad.read_text(encoding="utf-8")) if cache_pad.exists() else {}
    delen = [f"# {pdf.stem}\n"]
    totaal = fouten = 0
    for nr, pagina in enumerate(doc, 1):
        delen.append(f"\n## Pagina {nr}\n\n{pagina.get_text().strip()}\n")
        for soort, png in afbeeldingen_van_pagina(args, doc, pagina):
            totaal += 1
            if dry:
                continue
            print(f"   p.{nr}: {soort} beschrijven...")
            try:
                tekst = beschrijf_gecachet(args, cache, cache_pad, png)
            except (urllib.error.URLError, OSError, KeyError) as e:
                print(f"   FOUT bij beschrijven p.{nr}: {e}")
                fouten += 1
                continue
            if tekst and tekst.strip().upper().rstrip(".") != "GEEN":
                delen.append(f"\n[Beschrijving van {soort} op pagina {nr} van {pdf.stem}: {tekst}]\n")
    if fouten:
        print(f"   {fouten} fout(en): geen uitvoer geschreven, draai opnieuw om te hervatten")
    elif not dry:
        (uit_map / f"{pdf.stem}.md").write_text("\n".join(delen), encoding="utf-8")
    return len(doc), totaal


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("invoer", type=Path, help="map met pdf-readers (recursief)")
    p.add_argument("uitvoer", type=Path, help="map voor de verrijkte markdown-bestanden")
    p.add_argument("--model", default="qwen3-vl:latest")
    p.add_argument("--host", default="http://localhost:11434")
    p.add_argument("--min-px", type=int, default=150, help="kleinere afbeeldingen (iconen) overslaan")
    p.add_argument("--min-tekeningen", type=int, default=30,
                   help="vectorelementen waarboven een pagina als schema telt (0 = uit)")
    p.add_argument("--dpi", type=int, default=130, help="resolutie bij renderen van schema-pagina's")
    p.add_argument("--num-predict", type=int, default=700)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--keep-alive", default="10m")
    p.add_argument("--opnieuw", action="store_true", help="ook bestaande uitvoer opnieuw maken")
    p.add_argument("--dry-run", action="store_true", help="alleen tellen hoeveel plaatjes er zijn")
    args = p.parse_args()

    if not args.invoer.is_dir():
        sys.exit(f"Map niet gevonden: {args.invoer}")
    args.uitvoer.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(args.invoer.rglob("*.pdf"))
    print(f"{len(pdfs)} pdf's gevonden")
    for i, pdf in enumerate(pdfs, 1):
        if (args.uitvoer / f"{pdf.stem}.md").exists() and not args.opnieuw and not args.dry_run:
            print(f"[{i}/{len(pdfs)}] overgeslagen (bestaat al): {pdf.name}")
            continue
        print(f"[{i}/{len(pdfs)}] {pdf.name}")
        paginas, plaatjes = verwerk_pdf(args, pdf, args.uitvoer, args.dry_run)
        print(f"   {paginas} pagina's, {plaatjes} afbeeldingen/schema's")
    print("Klaar. Upload daarna met: python scripts/upload_readers.py", args.uitvoer)


if __name__ == "__main__":
    main()
