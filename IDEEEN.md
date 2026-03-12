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

## 5. Workflow Automation met n8n

**Wat is het?**
n8n is een visuele workflow builder (open source, zelf te hosten) waarmee je Ollama
als AI-stap kunt aanroepen binnen een groter automatiseringsproces.

**Waarom interessant?**
AI koppelen aan triggers, webhooks, e-mail, databases en externe APIs — zonder code.
Denk aan: "Als er een nieuw formulier binnenkomt, laat Ollama een samenvatting maken."

**Mogelijke aanpak:**
- n8n via Docker toevoegen aan de `docker-compose.yml`
- Ollama aanroepen via de ingebouwde Ollama-node of een HTTP Request node naar `localhost:11434`
- Zie: [n8n Ollama integratie](https://n8n.io/integrations/ollama/)

---

## 6. OpenClaw als communicatie wrapper

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
