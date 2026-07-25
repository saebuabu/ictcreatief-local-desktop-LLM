# n8n koppelen aan Ollama

n8n is een visuele workflow-builder (open source, zelf gehost) waarmee je Ollama als AI-stap
kunt aanroepen binnen een groter automatiseringsproces — bijvoorbeeld: "als er een webhook
binnenkomt met tekst, laat Ollama er een samenvatting van maken."

n8n draait als extra service naast Open WebUI, gedefinieerd in dezelfde `docker-compose.yml`.

---

## Starten en stoppen

n8n start automatisch mee met de rest van de stack:

```bash
docker compose up -d
```

Open daarna **http://localhost:5678** in de browser. Stoppen gaat via:

```bash
docker compose down
```

Workflows, credentials en instellingen blijven bewaard in het Docker-volume `n8n_data`
(gekoppeld aan `/home/node/.n8n` in de container), dus een herstart van de containers verliest
niets.

---

## Eerste keer inloggen

n8n heeft **geen** vaste inloggegevens via `.env` — de oude `N8N_BASIC_AUTH_*` omgevingsvariabelen
worden door recente n8n-versies genegeerd. In plaats daarvan vraagt n8n bij het **eerste bezoek**
aan `http://localhost:5678` om een eigen owner-account aan te maken (naam, e-mailadres,
wachtwoord). Doe dit direct na de eerste start — tot dat moment is de editor-UI in principe
onbeschermd bereikbaar voor iedereen die bij poort 5678 kan (op dit systeem alleen relevant als de
machine op een gedeeld netwerk hangt).

De REST API zelf (`/rest/...`) is altijd los beveiligd en geeft zonder geldige sessie een 401,
ongeacht de setup-status van de editor.

---

## Ollama aanroepen vanuit n8n

n8n draait in een container en bereikt de native Windows Ollama-service via:

```
http://host.docker.internal:11434
```

Dit werkt via de `HTTP Request`-node (aanroep naar `/api/generate` of `/api/chat`) of via een
ingebouwde Ollama-node/credential, afhankelijk van de n8n-versie. Gebruik bij het instellen van
een Ollama-credential in n8n dezelfde base URL hierboven — **niet** `localhost:11434`, want dat
verwijst binnen de container naar zichzelf, niet naar de Windows-host.

---

## Voorbeeldworkflow: webhook → Ollama-samenvatting

`n8n/workflows/samenvatten-webhook.json` bevat een kant-en-klare workflow (zelfde opzet als de
ComfyUI-workflows in `comfy-ui/workflows/`):

1. **Webhook** — luistert op `POST /webhook/samenvatten`, verwacht `{ "tekst": "..." }`
2. **HTTP Request** — stuurt de tekst naar `http://host.docker.internal:11434/api/generate`
   (model `llama3.1:8b`) met de prompt "Vat dit kort samen in het Nederlands: ..."
3. **Respond to Webhook** — geeft `{ "samenvatting": "..." }` terug

### Importeren via de UI

In de n8n-editor: **Workflows → Import from File** → selecteer
`n8n/workflows/samenvatten-webhook.json` → activeer de workflow met de toggle rechtsboven.

### Importeren via de CLI (headless)

```bash
docker cp n8n/workflows/samenvatten-webhook.json n8n:/tmp/samenvatten-webhook.json
docker exec n8n n8n import:workflow --input=/tmp/samenvatten-webhook.json
docker exec n8n n8n publish:workflow --id=sam3nvatt3nWebhook01
docker restart n8n
```

> **Let op:** `import:workflow --activeState=fromJson` activeert alléén in queue/multi-main mode.
> In de standaard single-main opstelling van dit project moet je de workflow apart publiceren met
> `n8n publish:workflow --id=<workflow-id>` en daarna de container herstarten — pas bij het
> opstarten leest n8n welke workflows gepubliceerd zijn en registreert het de webhook-trigger.

### Testen

```powershell
Invoke-RestMethod -Uri http://localhost:5678/webhook/samenvatten -Method Post `
  -ContentType "application/json" -Body '{"tekst": "lange tekst hier..."}'
```

Verwacht resultaat: een JSON-object met een `samenvatting`-veld.

---

## Eindresultaat

Docenten en studenten kunnen no-code AI-workflows bouwen bovenop de lokale Ollama-modellen —
triggers, webhooks of andere n8n-nodes gekoppeld aan een AI-stap — volledig lokaal en zonder
cloudverbinding.
