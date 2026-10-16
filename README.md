# Lokale LLM met Ollama — Windows 11

Een lokale AI-omgeving op basis van [Ollama](https://ollama.com) en [Open WebUI](https://github.com/open-webui/open-webui), draaiend op Windows 11.
Geen cloudverbinding nodig — alle data blijft lokaal....

---

## Inhoud

| Bestand | Beschrijving |
|---|---|
| [`LOCAL_LLM_PLAN.md`](LOCAL_LLM_PLAN.md) | Volledig installatieplan: hardware, modellen, Ollama, Docker en Open WebUI |
| [`MBO_Experimenten_Ollama.md`](MBO_Experimenten_Ollama.md) | Praktische experimenten voor MBO-studenten en docenten |
| [`docker-compose.yml`](docker-compose.yml) | Docker Compose configuratie voor Open WebUI en n8n |
| [`.env`](.env) | Configuratievariabelen (poort, Ollama URL, image tag) |
| [`docs/n8n-setup.md`](docs/n8n-setup.md) | n8n koppelen aan Ollama: setup, voorbeeldworkflow, troubleshooting |
| [`docs/n8n-onedrive-opdracht-review.md`](docs/n8n-onedrive-opdracht-review.md) | OneDrive-opdrachten automatisch laten samenvatten en beoordelen |
| [`docs/agentic-systems.md`](docs/agentic-systems.md) | Agents die via n8n met elkaar communiceren: architectuur, stappenplan, Fase 1-4 |
| [`docs/examen-rag-model.md`](docs/examen-rag-model.md) | Examencoach: eigen Open WebUI-model met de readers van alle jaren als RAG-bron |
| [`scripts/reader_verrijken.py`](scripts/reader_verrijken.py) | PDF-readers verrijken: afbeeldingen/schema's laten beschrijven door een lokaal vision-model |
| [`scripts/upload_readers.py`](scripts/upload_readers.py) | Readers in bulk uploaden naar een Open WebUI Knowledge-collectie |
| [`scripts/belastingtest.py`](scripts/belastingtest.py) | Belastingtest: N gelijktijdige leerlingen op één model, meet snelheid en wachttijd |
| [`rag-documents/`](rag-documents/) | Brondocumenten voor de lokale kennisbank (RAG, Fase 4) — niet in git |
| [`IDEEEN.md`](IDEEEN.md) | Uitbreidingsideeën: agentic system, MCP, RAG, en meer |

---

## Snel starten

### 1. Installeer Ollama

Download en installeer Ollama via [ollama.com](https://ollama.com). Ollama is een per-gebruiker installatie (tray-app via de opstartmap), geen Windows-service: het draait alleen zolang dat account is ingelogd. Het detecteert automatisch je GPU.

### 2. Download een model

```bash
ollama pull llama3.1:8b
```

### 3. Start Open WebUI en n8n

Zorg dat Docker Desktop actief is, dan:

```bash
docker compose up -d
```

Open daarna **http://localhost:3000** (Open WebUI) of **http://localhost:5678** (n8n) in je
browser. Bij het eerste bezoek aan n8n vraagt het om een eigen owner-account (naam, e-mail,
wachtwoord) — er zijn geen vaste inloggegevens via `.env`.

Test of n8n Ollama kan aanroepen met de voorbeeldworkflow (`n8n/workflows/samenvatten-webhook.json`):
importeer die via **Workflows → Import from File** in de editor, activeer hem, en roep 'm aan:

```powershell
Invoke-RestMethod -Uri http://localhost:5678/webhook/samenvatten -Method Post `
  -ContentType "application/json" -Body '{"tekst": "lange tekst hier..."}'
```

Verwacht resultaat: een JSON-object met een `samenvatting`-veld. Zie
[`docs/n8n-setup.md`](docs/n8n-setup.md) voor de volledige eerste-keer-setup, CLI-import en
troubleshooting.

### 4. Stoppen

```bash
docker compose down
```

---

## Configuratie

Pas `.env` aan om de standaardinstellingen te wijzigen:

```env
WEBUI_PORT=3000                                          # Poort in de browser
OLLAMA_BASE_URL=http://host.docker.internal:11434        # URL naar Ollama
WEBUI_IMAGE_TAG=main                                     # Image versie

N8N_PORT=5678                                            # Poort voor de n8n-editor
N8N_IMAGE_TAG=latest                                     # Image versie

QDRANT_PORT=6333                                         # Poort voor Qdrant (RAG, zie docs/agentic-systems.md)
```

---

## Hardware

Geoptimaliseerd voor:
- **GPU:** ASUS Prime GeForce RTX 5080 16GB GDDR7
- **CPU:** Intel Core i7-14700K
- **OS:** Windows 11

Aanbevolen modellen voor deze hardware: `7B–14B` parameter modellen (Q4_K_M of Q5_K_M quantisatie).
Zie [`LOCAL_LLM_PLAN.md`](LOCAL_LLM_PLAN.md) voor een volledig overzicht.

---

## Belastingtest (klas)

Test hoeveel gelijktijdige leerlingen Ollama aankan op hetzelfde model. Het script
`scripts/belastingtest.py` stuurt N gelijktijdige aanvragen rechtstreeks naar Ollama en meet per
leerling de tijd tot de eerste token en de tokens per seconde. Het gebruikt alleen de
standaardbibliotheek van Python.

```bash
python scripts/belastingtest.py                               # 25 leerlingen, llama3.1:8b
python scripts/belastingtest.py --model llama3.1:8b --users 25
python scripts/belastingtest.py --users 25 --stagger 5        # starts gespreid over 5 seconden
```

Draai tijdens de test `ollama ps` in een tweede venster: staat er CPU bij, dan is het VRAM vol.
Stel `OLLAMA_NUM_PARALLEL` (begin met `6`) zo in dat de traagste leerling nog circa 5 tok/s haalt
en de eerste token binnen circa 10 seconden komt. Zet daarbij ook `OLLAMA_CONTEXT_LENGTH=4096`.
Open WebUI voegt achtergrondtaken toe (titels, tags); zet die uit voor een realistische meting.

---

## Claude Code CLI

[Claude Code](https://claude.ai/code) is Anthropic's AI-assistent in de terminal. Vanuit deze projectmap kun je Claude inzetten om configuraties aan te passen, scripts te schrijven of problemen te debuggen — zonder browser.

### Installatie

**Vereiste:** Node.js 18+ via [nodejs.org](https://nodejs.org) (LTS)

```powershell
npm install -g @anthropic-ai/claude-code
```

### Gebruik

Start Claude vanuit de projectmap:

```powershell
cd C:\Users\P99900086\source\repos\OllamaLLM
claude
```

Bij de eerste keer opstarten word je gevraagd in te loggen via je Anthropic-account.

### Wat je ermee kunt doen

- Docker Compose configuratie aanpassen of debuggen
- Nieuwe Ollama Modelfiles schrijven
- Experimenten uitwerken voor MBO-studenten
- Vragen stellen over de projectbestanden

> Claude Code heeft geen internetverbinding nodig voor het lezen van lokale bestanden — alleen voor de API-aanroepen naar Anthropic.

---

## Voor het MBO

[`MBO_Experimenten_Ollama.md`](MBO_Experimenten_Ollama.md) bevat kant-en-klare experimenten per afdeling:
- Software Development
- Media & Communicatie
- Zorg & Welzijn
- Handel & Ondernemen
- Techniek & Elektrotechniek

Alle experimenten draaien volledig lokaal — privacy-proof voor gebruik met leerlingdata.
