# Ideeën & Toekomstige Uitbreidingen

Een verzameling ideeën voor verdere uitbreiding van de lokale LLM-omgeving.
Nog niet uitgewerkt — vastgelegd om later op terug te komen.

---

## 1. Agentic System

**Wat is het?**
Meerdere AI-agents die samenwerken aan een taak: de ene agent plant, de andere voert uit,
een derde controleert het resultaat.

**Waarom interessant?**
Complexere taken die een enkele LLM niet aankan, zoals zelfstandig code schrijven, testen
en debuggen, of meerstaps onderzoek uitvoeren.

**Mogelijke aanpak:**
- [AutoGen](https://github.com/microsoft/autogen) — Microsoft's multi-agent framework
- [CrewAI](https://github.com/crewAIInc/crewAI) — rollen-gebaseerde agent orkestratie
- Beide ondersteunen Ollama als lokale backend

**Status:** 🚧 in ontwikkeling, gebouwd bovenop de al draaiende n8n-instantie (punt 5)
in plaats van een apart framework: elke agent is een n8n-workflow met een webhook,
agents roepen elkaars webhook aan met een gedeeld JSON-berichtprotocol. Fase 1
(Coordinator + Worker) is getest. Fase 2 (Critic-agent + dynamische routering: de
Coordinator stuurt een afgekeurd antwoord één keer terug voor herziening) is getest —
zowel het direct-goedgekeurd-pad als de herzieningsroute zijn bevestigd werkend. Fase 3
(gedeelde blackboard — een n8n Data Table `agentic-blackboard` waarop agents taak,
antwoord en kritiek op `conversation_id` lezen/schrijven in plaats van de volledige
geschiedenis rond te sturen) is gebouwd, nog te testen — vereist wel dat de
`agentic-blackboard`-tabel eerst handmatig in n8n wordt aangemaakt. Fase 4 (tool-agent —
bewust een **lokale kennisbank (RAG)** in plaats van websearch, om geen externe
verbinding nodig te hebben) heeft nu zowel de ingestion-workflow
(`n8n/workflows/rag-ingest.json`, documenten → Qdrant-vectordatabase via Ollama-
embeddings) als de query-tool-agent (`rag-query.json`, vraag → embedden → top-k
fragmenten uit Qdrant → `tool-result`) gebouwd én getest. De koppeling aan de Worker
(zodat de Worker zelf beslist de kennisbank te raadplegen) volgt later. Workflows:
`n8n/workflows/agentic-coordinator.json`, `agentic-worker.json`, `agentic-critic.json`,
`rag-ingest.json`, `rag-query.json`.
Zie [`docs/agentic-systems.md`](docs/agentic-systems.md) voor de architectuur en het
stappenplan.

---

## 2. MCP Servers aanspreken

**Wat is het?**
Model Context Protocol (MCP) — een standaard interface om LLM's toegang te geven tot
tools en databronnen (filesystem, browser, database, APIs).

**Waarom interessant?**
Gestructureerde en veilige manier om Ollama te koppelen aan externe tools, zonder
losse integraties per tool te bouwen.

**Mogelijke aanpak:**
- Lokale MCP servers draaien (bijv. filesystem-server, browser-server)
- Open WebUI ondersteunt MCP via plugin-systeem
- Zie ook: [MCP specificatie](https://modelcontextprotocol.io)

---

## 3. RAG (Retrieval Augmented Generation)

**Wat is het?**
Eigen documenten (PDF's, notities, handleidingen) indexeren in een vector database,
zodat het model er vragen over kan beantwoorden op basis van de actuele inhoud.

**Waarom interessant?**
Het model "weet" iets over jouw eigen data zonder fine-tuning. Ideaal voor
schooldocumenten, handleidingen of interne kennisbanken.

**Mogelijke aanpak:**
- Vector database: [ChromaDB](https://www.trychroma.com/) of [Qdrant](https://qdrant.tech/)
- Embedding model: `nomic-embed-text` via Ollama
- Open WebUI heeft ingebouwde RAG-ondersteuning (documenten uploaden in de chat)

**Status:** ✅ ingestion + query getest, als Fase 4 tool-agent van punt 1 (Agentic
System) — Qdrant + `nomic-embed-text` via Ollama, precies zoals hierboven beschreven.
Zowel de ingestion-workflow (`n8n/workflows/rag-ingest.json`) als de query-tool-agent
(`rag-query.json`) werken end-to-end; koppeling aan de Worker volgt nog. Zie
[`docs/agentic-systems.md`](docs/agentic-systems.md#fase-4--lokale-kennisbank-rag).

---

## 4. Skills toevoegen aan model

**Wat is het?**
Gespecialiseerde modellen aanmaken via Ollama Modelfiles met een vaste system prompt,
temperatuur en contextgrootte — afgestemd op een specifieke taak of persona.

**Waarom interessant?**
Eén basismodel, meerdere gespecialiseerde varianten: een MBO-docent assistent,
een code reviewer, een Nederlandstalige schrijfhulp, enzovoort.

**Mogelijke aanpak:**
```
FROM llama3.1:8b
SYSTEM "Jij bent een ..."
PARAMETER temperature 0.5
```
```bash
ollama create mijn-skill -f Modelfile
```
Zie ook het voorbeeld in `MBO_Experimenten_Ollama.md`.

---

## 5. Workflow Automation met n8n — ✅ geïmplementeerd

**Wat is het?**
n8n is een visuele workflow builder (open source, zelf te hosten) waarmee je Ollama
als AI-stap kunt aanroepen binnen een groter automatiseringsproces.

**Waarom interessant?**
AI koppelen aan triggers, webhooks, e-mail, databases en externe APIs — zonder code.
Denk aan: "Als er een nieuw formulier binnenkomt, laat Ollama een samenvatting maken."

**Status:** n8n draait als service naast Open WebUI in `docker-compose.yml`, bereikt Ollama via
`http://host.docker.internal:11434`, en er is een werkende voorbeeldworkflow
(`n8n/workflows/samenvatten-webhook.json`: webhook → Ollama-samenvatting → response).
Zie [`docs/n8n-setup.md`](docs/n8n-setup.md) voor setup, eerste login en de voorbeeldworkflow.

---

## 7. Open WebUI-agent die een n8n-workflow aanroept (tool-calling)

**Wat is het?**
Studenten krijgen in Open WebUI een specifieke, aan hen toegewezen chatbot (model +
system prompt) tot hun beschikking. Via Open WebUI's **Tools**-functie (Workspace →
Tools, Python-functies gekoppeld aan dat model) kan die chatbot tijdens het gesprek een
n8n-webhook aanroepen en het resultaat terugkrijgen in de conversatie — zelfde
synchrone webhook-patroon (`responseMode: responseNode`) als de agentic-systemen in
punt 1, alleen nu aangeroepen vanuit Open WebUI in plaats van vanuit een andere
n8n-workflow.

**Waarom interessant?**
Studenten hoeven niet te weten dat er n8n achter zit — ze chatten gewoon, en de agent
besluit zelf (via tool-calling) wanneer hij bijvoorbeeld de RAG-kennisbank (`rag-query`,
punt 3) raadpleegt of een ander n8n-proces start.

**Hoe tool-calling werkt:** het model krijgt een lijst tools (naam, beschrijving,
verwachte parameters). Beslist het model dat een tool nodig is, dan genereert het een
gestructureerd JSON-blokje in plaats van antwoordtekst; Open WebUI voert de echte
aanroep uit (de HTTP-call naar n8n) en geeft het resultaat terug aan het model voor het
uiteindelijke antwoord.

**Welke lokale modellen dit ondersteunen** (op basis van Ollama's `capabilities`-veld):

| Model | Tools? | Opmerking |
|---|---|---|
| `llama3.1:8b` | ✅ | beste startpunt — snel, betrouwbaar formaat, al het algemene model |
| `qwen2.5-coder:14b` | ✅ | prima, maar coding-georiënteerd |
| `qwen3.5:0.8b` / `qwen3.5-9b-abliterated` | ✅ | Qwen-familie staat bekend als sterk in function calling |
| `qwen3-vl` / `llama3.2-vision:11b` | ✅ | ook vision, zwaarder voor alleen tool-calling |
| `huggingface.co/unsloth/gpt-oss-20b-GGUF` | ✅ | groot, dus trager |
| `deepseek-r1:14b` | ✅ maar minder voorspelbaar — redeneermodel, genereert eerst een lange `<think>`-redenering vóór het (soms) het tool-JSON-formaat netjes volgt |
| `huggingface.co/unsloth/gemma-3-12b-it-GGUF` | ❌ | geen tools-support |

**Belangrijkste afweging:** dit is synchroon — de student wacht in de chat tot de
n8n-workflow klaar is. Prima voor iets kort als `rag-query` (paar seconden), maar voor
een langlopend n8n-proces zou een async ontwerp nodig zijn (trigger + apart ophalen van
het resultaat in plaats van direct wachten).

**Status:** 💡 idee, nog niet uitgewerkt. Bouwt voort op punt 1 (Agentic System) en punt 3
(RAG) — met name geschikt als vervolg zodra de query-tool-agent aan de Worker gekoppeld
is.

---

## 8. OpenClaw als communicatie wrapper

**Wat is het?**
Een communicatielaag bovenop Ollama die gestructureerde input/output afhandelt
voor meerdere applicaties tegelijk.

**Waarom interessant?**
Consistente interface voor verschillende clients (web, CLI, scripts) naar hetzelfde
lokale model — met mogelijke logging, rate limiting en foutafhandeling.

**Mogelijke aanpak:**
- Nader te onderzoeken: documentatie en voorbeelden bekijken
- Alternatieven vergelijken met Ollama's ingebouwde OpenAI-compatibele API

---

*Ideeën zijn nog niet uitgewerkt. Sommige bouwen op elkaar voort (bijv. RAG + Agentic + n8n).*
