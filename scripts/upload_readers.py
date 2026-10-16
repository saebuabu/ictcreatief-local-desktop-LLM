#!/usr/bin/env python3
"""Upload readers (PDF/DOCX/TXT/MD) naar een Open WebUI Knowledge-collectie.

Maakt de collectie aan als die nog niet bestaat en slaat bestanden over die
er al in staan (op bestandsnaam), zodat je elk jaar alleen nieuwe readers
hoeft toe te voegen. Alleen standaardbibliotheek, geen installatie nodig.

API-key aanmaken: Open WebUI -> Instellingen -> Account -> API-sleutels.

Voorbeelden:
    set OPENWEBUI_API_KEY=sk-...
    python scripts/upload_readers.py C:\readers --collectie "Examenreaders"
    python scripts/upload_readers.py C:\readers --dry-run
"""
import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

EXTENSIES = {".pdf", ".docx", ".txt", ".md"}


def api(args, method, pad, data=None, headers=None, raw=None):
    h = {"Authorization": f"Bearer {args.api_key}", "Accept": "application/json"}
    body = raw
    if data is not None:
        body = json.dumps(data).encode()
        h["Content-Type"] = "application/json"
    h.update(headers or {})
    req = urllib.request.Request(f"{args.host}{pad}", data=body, headers=h, method=method)
    with urllib.request.urlopen(req, timeout=args.timeout) as r:
        return json.loads(r.read() or b"null")


def upload_bestand(args, pad):
    grens = uuid.uuid4().hex
    naam = pad.name
    mime = mimetypes.guess_type(naam)[0] or "application/octet-stream"
    kop = (f"--{grens}\r\nContent-Disposition: form-data; name=\"file\"; "
           f"filename=\"{naam}\"\r\nContent-Type: {mime}\r\n\r\n").encode()
    body = kop + pad.read_bytes() + f"\r\n--{grens}--\r\n".encode()
    return api(args, "POST", "/api/v1/files/", raw=body,
               headers={"Content-Type": f"multipart/form-data; boundary={grens}"})


def zoek_of_maak_collectie(args):
    lijst = api(args, "GET", "/api/v1/knowledge/")
    items = lijst.get("items", lijst) if isinstance(lijst, dict) else lijst
    for k in items:
        if k["name"] == args.collectie:
            return k["id"]
    if args.dry_run:
        return None
    k = api(args, "POST", "/api/v1/knowledge/create",
            data={"name": args.collectie, "description": args.beschrijving})
    print(f"Collectie '{args.collectie}' aangemaakt ({k['id']})")
    return k["id"]


def bestaande_namen(args, kid):
    if not kid:
        return set()
    k = api(args, "GET", f"/api/v1/knowledge/{kid}")
    return {f.get("meta", {}).get("name") for f in k.get("files", [])}


def toevoegen(args, kid, file_id):
    # Verwerking (tekst -> embeddings) kan even duren; probeer opnieuw bij fout.
    for poging in range(args.retries):
        try:
            api(args, "POST", f"/api/v1/knowledge/{kid}/file/add", data={"file_id": file_id})
            return True
        except urllib.error.HTTPError as e:
            if poging == args.retries - 1:
                print(f"   FOUT {e.code}: {e.read().decode(errors='replace')[:200]}")
                return False
            time.sleep(3)
    return False


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("map", type=Path, help="map met readers (wordt recursief doorzocht)")
    p.add_argument("--collectie", default="Examenreaders")
    p.add_argument("--beschrijving", default="Readers van alle jaren voor examenkandidaten")
    p.add_argument("--host", default="http://localhost:3000")
    p.add_argument("--api-key", default=os.environ.get("OPENWEBUI_API_KEY"))
    p.add_argument("--timeout", type=int, default=600, help="seconden per request (grote PDF's)")
    p.add_argument("--retries", type=int, default=5)
    p.add_argument("--dry-run", action="store_true", help="alleen tonen wat er zou gebeuren")
    args = p.parse_args()

    if not args.api_key:
        sys.exit("Geen API-key: zet OPENWEBUI_API_KEY of gebruik --api-key")
    if not args.map.is_dir():
        sys.exit(f"Map niet gevonden: {args.map}")

    bestanden = sorted(f for f in args.map.rglob("*") if f.suffix.lower() in EXTENSIES)
    print(f"{len(bestanden)} bestanden gevonden in {args.map}")

    kid = zoek_of_maak_collectie(args)
    reeds = bestaande_namen(args, kid)
    ok = overgeslagen = fout = 0
    for i, f in enumerate(bestanden, 1):
        if f.name in reeds:
            print(f"[{i}/{len(bestanden)}] overgeslagen (bestaat al): {f.name}")
            overgeslagen += 1
            continue
        print(f"[{i}/{len(bestanden)}] {'zou uploaden' if args.dry_run else 'uploaden'}: {f.name}")
        if args.dry_run:
            continue
        try:
            file_id = upload_bestand(args, f)["id"]
            if toevoegen(args, kid, file_id):
                ok += 1
            else:
                fout += 1
        except (urllib.error.URLError, OSError) as e:
            print(f"   FOUT: {e}")
            fout += 1
    print(f"Klaar: {ok} toegevoegd, {overgeslagen} overgeslagen, {fout} mislukt")
    sys.exit(1 if fout else 0)


if __name__ == "__main__":
    main()
