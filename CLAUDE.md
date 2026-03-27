# CLAUDE.md — OllamaLLM project

## Projectdoel

Lokale AI-omgeving op basis van Ollama + Open WebUI, draaiend op Windows 11.
Gericht op gebruik binnen MBO-onderwijs — privacy-proof, geen cloudverbinding.

---

## Hardware & omgeving

- **GPU:** RTX 5080, 16GB VRAM
- **OS:** Windows 11 Enterprise (geen winget beschikbaar)
- **Python:** Miniconda
- **Shell:** bash (via Claude Code)
- **Ollama:** actief als Windows-service op poort `11434`
- **Open WebUI:** draait via Docker op poort `3000`

---

## Geïnstalleerde Ollama-modellen

| Model | Gebruik |
|---|---|
| `qwen2.5-coder:14b` | Code-gerelateerde taken |
| `deepseek-r1:14b` | Redeneren en analyse |

Sweet spot voor dit systeem: **7B–14B parameter modellen** (Q4_K_M of Q5_K_M quantisatie).

---

## Projectstructuur

```
OllamaLLM/
├── docker-compose.yml        # Open WebUI service definitie
├── .env                      # Poort, Ollama URL, image tag
├── README.md                 # Overzicht en snelstartgids
├── LOCAL_LLM_PLAN.md         # Volledig installatieplan
├── MBO_Experimenten_Ollama.md # Kant-en-klare experimenten per MBO-sector
├── IDEEEN.md                 # Uitbreidingsideeën (nog niet uitgewerkt)
└── docs/                     # Aanvullende documentatie
```

---

## Werkwijze

- Antwoord in het **Nederlands**, tenzij expliciet anders gevraagd
- Houd wijzigingen minimaal en gericht — geen onnodige refactors
- Voeg geen features toe die niet gevraagd zijn
- Docker-commando's werken via Docker Desktop op Windows
- Gebruik `docker compose` (v2 syntax, zonder koppelteken)

---

## Uitbreidingsrichtingen (zie IDEEEN.md)

1. Agentic systems (AutoGen, CrewAI)
2. MCP servers
3. RAG met ChromaDB/Qdrant + `nomic-embed-text`
4. Ollama Modelfiles voor gespecialiseerde persona's
5. Workflow automation met n8n
6. OpenClaw als communicatiewrapper
