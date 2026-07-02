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
- **Claude Code:** vanaf nu direct geïnstalleerd en in gebruik op deze LLM-machine zelf (niet op een aparte devmachine)

---

## Geïnstalleerde Ollama-modellen

| Model | Grootte | Gebruik |
|---|---|---|
| `qwen2.5-coder:14b` | 9.0 GB | Code-gerelateerde taken |
| `deepseek-r1:14b` | 9.0 GB | Redeneren en analyse |
| `llama3.1:8b` | 4.9 GB | Algemeen gebruik |
| `llama3.2-vision:11b` | 7.8 GB | Vision / multimodaal |
| `qwen3-vl:latest` | 6.1 GB | Vision / multimodaal |
| `qwen3.5:0.8b` | 1.0 GB | Klein/snel model |
| `lukey03/qwen3.5-9b-abliterated:latest` | 5.6 GB | Uncensored variant |
| `huggingface.co/unsloth/gpt-oss-20b-GGUF:latest` | 11 GB | Groot algemeen model |
| `huggingface.co/unsloth/gemma-3-12b-it-GGUF:latest` | 8.2 GB | Instruct-model |
| `huggingface.co/city96/FLUX.1-dev-gguf:latest` | 23 GB | Image generation |
| `huggingface.co/city96/stable-diffusion-3.5-large-turbo-gguf:latest` | 16 GB | Image generation |
| `huggingface.co/ChristianAzinn/gte-small-gguf:latest` | 25 MB | Embeddings |

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
