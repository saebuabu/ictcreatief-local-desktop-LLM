# Lokale LLM met Ollama — Windows 11

Een lokale AI-omgeving op basis van [Ollama](https://ollama.com) en [Open WebUI](https://github.com/open-webui/open-webui), draaiend op Windows 11.
Geen cloudverbinding nodig — alle data blijft lokaal.

---

## Inhoud

| Bestand | Beschrijving |
|---|---|
| [`LOCAL_LLM_PLAN.md`](LOCAL_LLM_PLAN.md) | Volledig installatieplan: hardware, modellen, Ollama, Docker en Open WebUI |
| [`MBO_Experimenten_Ollama.md`](MBO_Experimenten_Ollama.md) | Praktische experimenten voor MBO-studenten en docenten |
| [`docker-compose.yml`](docker-compose.yml) | Docker Compose configuratie voor Open WebUI |
| [`.env`](.env) | Configuratievariabelen (poort, Ollama URL, image tag) |

---

## Snel starten

### 1. Installeer Ollama

Download en installeer Ollama via [ollama.com](https://ollama.com). Ollama draait als Windows-service en detecteert automatisch je GPU.

### 2. Download een model

```bash
ollama pull llama3.1:8b
```

### 3. Start Open WebUI

Zorg dat Docker Desktop actief is, dan:

```bash
docker compose up -d
```

Open daarna **http://localhost:3000** in je browser.

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

## Voor het MBO

[`MBO_Experimenten_Ollama.md`](MBO_Experimenten_Ollama.md) bevat kant-en-klare experimenten per afdeling:
- Software Development
- Media & Communicatie
- Zorg & Welzijn
- Handel & Ondernemen
- Techniek & Elektrotechniek

Alle experimenten draaien volledig lokaal — privacy-proof voor gebruik met leerlingdata.
