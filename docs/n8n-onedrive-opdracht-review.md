# OneDrive-opdrachten automatisch laten samenvatten en beoordelen door Ollama

## Wat dit doet

Leerlingen uploaden opdrachten in een OneDrive-map die zo is ingesteld dat ze wel bestanden
kunnen **toevoegen**, maar niet elkaars bestanden of de rest van de map kunnen zien. Een n8n-
workflow (`n8n/workflows/opdracht-review.json`) checkt die map periodiek op nieuwe uploads, laat
Ollama er een samenvatting + review van maken, en schrijft het resultaat als los Markdown-bestand
naar een **aparte map die alleen de docent kan zien**.

---

## Blokkade eerst wegnemen: IT navragen

Om n8n bij OneDrive te laten kunnen, is een app-registratie in Entra ID (Azure AD) van het
schooldomein nodig. Veel EDU/Microsoft 365-tenants staan gebruikers-zelfregistratie van apps en
het geven van eigen consent aan API-permissies standaard **niet** toe. Vraag dus eerst bij
school-IT na:

- Mag je zelf een app-registratie aanmaken in Entra ID, of moet IT dit doen?
- Is er tenant-admin goedkeuring nodig voor de Graph-permissies hieronder?

Pas als dat duidelijk is, heeft de rest van deze handleiding zin.

---

## Stap 1: Entra ID app-registratie

1. **Azure Portal → Microsoft Entra ID → App registrations → New registration**
   - Account types: *"Accounts in this organizational directory only"* (single-tenant)
   - Redirect URI: laat dit veld voorlopig leeg — je vult 'm in stap 3 in met de URL die n8n
     zelf toont. Dit is een lokale OAuth-handshake vanaf de PC van de docent; het hoeft **niet**
     publiek bereikbaar te zijn (in tegenstelling tot een Graph-webhook, die we hier bewust niet
     gebruiken — zie "Waarom polling" hieronder).
2. **API permissions → Add a permission → Microsoft Graph → Delegated permissions**:
   - `Files.ReadWrite`
   - `offline_access`
   - `User.Read`
   - `openid`
   - `profile`
   - Klik daarna op **Grant admin consent** (of vraag IT dit te doen als je zelf geen
     tenant-admin bent)
3. **Certificates & secrets → New client secret** — bewaar de waarde direct, hij is later niet
   meer zichtbaar
4. Noteer: **Application (client) ID**, **Directory (tenant) ID**, en de **client secret**

---

## Stap 2: n8n-credential aanmaken

1. Open n8n (`http://localhost:5678`) → **Credentials → New → Microsoft OneDrive OAuth2 API**
2. Vul client ID, client secret en tenant ID in
3. Kopieer de **OAuth Redirect URL** die n8n toont naar de app-registratie uit stap 1 (App
   registrations → je app → Authentication → Add a platform → Web → plak de URL)
4. Klik **Sign in with Microsoft OneDrive** en log in als de docent
5. Test de credential: open de workflow (zie stap 3) en voer de node **"Bestanden in uploadmap"**
   handmatig uit — je moet de inhoud van de map terugkrijgen

> Gebruik het **delegated** OAuth2-credential-type, niet "App-Only Service Principal" — de
> workflow werkt steeds met de eigen OneDrive-toegang van de docent, niet los van een gebruiker.

---

## Stap 3: workflow importeren en instellen

De workflow staat al klaar in n8n (headless geïmporteerd als **draft/inactief**), of importeer
'm zelf opnieuw:

```bash
docker cp n8n/workflows/opdracht-review.json n8n:/tmp/opdracht-review.json
docker exec n8n n8n import:workflow --input=/tmp/opdracht-review.json
```

Open de workflow in de n8n-editor (**"OneDrive opdrachten -> Ollama samenvatting + review"**) en
vul in:

1. **Bestanden in uploadmap** (Get Children) en **Upload naar docentmap** (Upload) → koppel de
   zojuist aangemaakte OneDrive-credential
2. **Bestanden in uploadmap** → veld `folderId`: vervang `VUL-IN: ID van de leerling-uploadmap`
   door het echte map-ID (te vinden via de OneDrive-URL, of laat de node eenmalig los draaien op
   de root en zoek de map in de resultaten)
3. **Upload naar docentmap** → veld `parentId`: zelfde voor de docent-only outputmap
4. Sla op en **publiceer** de workflow (zie hieronder) zodra de eerste test geslaagd is

### Publiceren (headless, via CLI)

Net als bij de eerdere voorbeeldworkflow gebruikt deze n8n-versie een publish-stap los van
"Active":

```bash
docker exec n8n n8n publish:workflow --id=opdr8chtReview01
docker restart n8n
```

---

## Waarom polling, geen live webhook

Deze n8n-instantie is alleen lokaal bereikbaar op `http://localhost:5678`, zonder publiek
HTTPS-endpoint. Microsoft Graph "change notifications" (echte push-webhooks bij nieuwe
bestanden) vereisen zo'n publiek endpoint. In plaats daarvan checkt een **Schedule Trigger** elke
10 minuten de uploadmap op nieuwe bestanden — voldoende voor dit gebruik en zonder extra
infrastructuur (geen tunnel/reverse proxy nodig).

---

## Wat de workflow wel en niet aankan

- **Wel:** PDF (met ingesloten/selecteerbare tekst), `.txt`, `.md`
- **Niet (nog):** `.docx` en gescande/afbeelding-PDF's (geen OCR). Zulke uploads worden niet
  overgeslagen zonder spoor — er verschijnt een `<bestandsnaam>__niet-verwerkt.md` in de
  docentmap met de reden, zodat de docent weet dat de leerling opnieuw moet uploaden als PDF,
  `.txt` of `.md`.
- **Dubbele verwerking:** wordt voorkomen via n8n's workflow static data (een lijst met al
  verwerkte bestands-ID's, opgeslagen in de n8n-database — geen extra bestand of volume nodig).
- **Eén Ollama-aanroep per bestand** — vraagt in één prompt om zowel een samenvatting als
  feedback, gescheiden door Markdown-koppen (`## Samenvatting` / `## Feedback`). Dit scheelt
  round-trips op een GPU die ook voor andere lokale taken wordt gebruikt. Blijkt de kwaliteit
  tegen te vallen, splits dan in twee losse HTTP Request-nodes met een scherpere prompt per stap.

---

## Testen

1. Upload een `.md`- of `.pdf`-testbestand in de leerlingmap
2. Wacht op de eerstvolgende poll (max. 10 minuten), of voer de workflow handmatig uit via
   **"Execute workflow"** in de editor
3. Controleer of `<bestandsnaam>__review.md` verschijnt in de docent-only outputmap, met een
   `## Samenvatting`- en `## Feedback`-sectie
4. Upload hetzelfde bestand nogmaals (of laat de workflow nogmaals pollen) → er mag **geen**
   tweede reviewbestand verschijnen (dedup-check)
5. Upload een `.docx`-bestand → er verschijnt een `__niet-verwerkt.md`-bestand, de workflow loopt
   niet vast

---

## Openstaande keuzes

- Ollama-model: standaard `llama3.1:8b` (in de "Ollama: samenvatting + review"-node) — pas aan
  voor langere opdrachten of een ander gewenst model
- Polling-interval: standaard 10 minuten (node "Elke 10 minuten")
- Beoordelingscriteria: de huidige prompt geeft algemene feedback (sterke/zwakke punten,
  duidelijkheid). Voor een vast rubric/beoordelingskader: pas de prompt aan in de node
  "Bouw prompt"
