# Local LLM Environment Plan — Windows 11 + Ollama

## Hardware Summary

| Component | Spec | LLM Relevance |
|---|---|---|
| **GPU** | ASUS Prime GeForce RTX 5080 16GB GDDR7 | The main workhorse — 16GB VRAM is the key constraint |
| **CPU** | Intel Core i7-14700K (20 cores, 3.4 GHz) | Great for CPU offloading overflow layers |
| **RAM** | Kingston FURY Beast Black DDR5 (amount TBD) | Matters if models spill out of VRAM |
| **Storage** | Samsung 990 Pro 2TB NVMe M.2 | Plenty of fast storage for models (they're 4-50GB each) |
| **Motherboard** | ASROCK Z790M-ITX WiFi | - |
| **Cooler** | ARCTIC Liquid Freezer III Pro 240 | Good cooling for sustained inference workloads |
| **PSU** | Sharkoon Rebel P20 SFX 1000W | More than enough headroom |
| **Case** | Lian Li DAN Cases A3-mATX (SFF) | Compact build — monitor thermals under load |
| **OS** | Windows 11 Pro (Nederlands) | Fully supported by Ollama |
| **Network** | TP-Link Archer AX55 V1 WiFi 6 | Relevant if serving models over network |

---

## What You CAN Run (16GB VRAM)

These models fit comfortably in GPU memory:

| Model | Parameters | Quantization | ~VRAM Usage | Quality Notes |
|---|---|---|---|---|
| Llama 3.1 8B | 8B | Q8 | ~9GB | Very good general purpose |
| Llama 3.1 8B | 8B | Q4_K_M | ~5GB | Good, slight quality loss |
| Mistral 7B | 7B | Q8 | ~8GB | Excellent reasoning |
| Phi-3 Medium | 14B | Q4_K_M | ~9GB | Strong model from Microsoft |
| Gemma 2 9B | 9B | Q5_K_M | ~8GB | Strong Google model |
| Qwen 2.5 14B | 14B | Q4_K_M | ~10GB | Excellent multilingual |
| DeepSeek-R1 14B | 14B | Q4_K_M | ~10GB | Strong reasoning capabilities |
| CodeLlama 13B | 13B | Q4_K_M | ~9GB | Good for coding tasks |
| Llama 3.1 70B | 70B | Q4_K_M | ~40GB | Partial GPU offload — slow but possible |

**Sweet spot for this system: 7B–14B parameter models** — these run fully in VRAM with excellent speed.

---

## What You CANNOT Realistically Run

- **70B+ models at full speed** — they won't fit in 16GB VRAM; they'll spill to system RAM and be 5–10x slower
- **GPT-4 class models** (100B+) — not feasible locally on any consumer hardware
- **Large context windows** (128K+) on bigger models — context consumes VRAM too
- **Multiple models simultaneously** — 16GB limits you to one loaded model at a time

---

## Expected Performance

| Model Size | Quantization | Estimated Speed | Experience |
|---|---|---|---|
| 7B | Q4_K_M | ~80–120 tokens/sec | Very fast, near-instant responses |
| 14B | Q4_K_M | ~40–70 tokens/sec | Snappy, great experience |
| 70B (CPU offload) | Q4_K_M | ~5–15 tokens/sec | Usable but noticeably slow |

> **Note:** Actual performance depends on your system RAM amount and whether the model fits entirely in VRAM.

---

## Step-by-Step Installation Plan

### Phase 1: Prerequisites

1. **Update NVIDIA drivers** to the latest version (critical for RTX 5080 support)
   - Download from: https://www.nvidia.com/drivers
   - The RTX 5080 is new — ensure you have the latest Game Ready or Studio driver
2. **Verify GPU is recognized**: Open a terminal and run `nvidia-smi`
3. **Check RAM amount**: Open Task Manager > Performance > Memory

### Phase 2: Install Ollama

1. Download Ollama from **https://ollama.com** (Windows installer)
2. Run the installer — it installs as a Windows system service
3. Open a terminal (PowerShell or CMD) and verify:
   ```
   ollama --version
   ```
4. Ollama will auto-detect your RTX 5080 via CUDA

### Phase 3: Pull Your First Models

```bash
# General purpose — fast and capable
ollama pull llama3.1:8b

# Multilingual and smart
ollama pull qwen2.5:14b

# Reasoning tasks
ollama pull deepseek-r1:14b

# Coding assistant
ollama pull codellama:13b
```

### Phase 4: Test & Chat

```bash
# Start an interactive chat session
ollama run llama3.1:8b
```

Other useful commands:
```bash
# List downloaded models
ollama list

# Show model details
ollama show llama3.1:8b

# Remove a model
ollama rm <model-name>

# Run with a specific prompt
ollama run llama3.1:8b "Explain quantum computing in simple terms"
```

### Phase 5: Enable WSL2 & Install Docker Desktop (Needed for Phase 6)

> **Why?** Ollama zelf draait native op Windows en heeft dit NIET nodig.
> Maar Open WebUI (Phase 6) wordt het makkelijkst via Docker geïnstalleerd,
> en Docker Desktop op Windows vereist WSL2 of Hyper-V.

**Stap 5.1 — Schakel Windows-onderdelen in:**

Open PowerShell als Administrator:
```powershell
# Schakel WSL in
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Schakel Virtual Machine Platform in (nodig voor WSL2)
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Schakel Hyper-V in (nodig voor Docker Desktop)
dism.exe /online /enable-feature /featurename:Microsoft-Hyper-V-All /all /norestart
```

**Stap 5.2 — Herstart je PC**

**Stap 5.3 — Stel WSL2 in als standaard:**
```powershell
wsl --set-default-version 2
```

**Stap 5.4 — Installeer een Linux-distributie (optioneel maar aanbevolen):**
```powershell
wsl --install -d Ubuntu
```

**Stap 5.5 — Installeer Docker Desktop:**
1. Download Docker Desktop van https://www.docker.com/products/docker-desktop/
2. Tijdens installatie: vink **"Use WSL 2 based engine"** aan
3. Start Docker Desktop en wacht tot de engine draait
4. Verifieer in een terminal:
   ```bash
   docker --version
   docker run hello-world
   ```

> **Let op SFF build:** Docker Desktop verbruikt standaard RAM en CPU.
> Stel limieten in via Docker Desktop > Settings > Resources als dat nodig is.

### Phase 6: Add a Web UI (Optional but Recommended)

**Open WebUI** — a ChatGPT-like interface that connects to Ollama:
- Provides conversation history, model switching, file uploads
- Can be installed via Docker or standalone
- Connects to Ollama's API at `http://localhost:11434`

**Installation via Docker (recommended — requires Phase 5):**

Een `docker-compose.yml` staat in de root van dit project. Start Open WebUI met:
```bash
docker compose up -d
```

Stop met:
```bash
docker compose down
```

Open daarna http://localhost:3000 in je browser.

**Alternative zonder Docker (via pip/Python):**
```bash
pip install open-webui
open-webui serve
```
> Hiervoor heb je Python 3.11+ nodig, maar geen WSL2/Docker.

### Phase 7: Explore Integrations

| Integration | Description |
|---|---|
| **VS Code + Continue** | Local AI coding assistant inside your editor |
| **Ollama API** | OpenAI-compatible REST API at `localhost:11434` |
| **LangChain / Python** | Build custom apps and workflows against local models |
| **AutoGen / CrewAI** | Multi-agent frameworks using local models |

---

## Understanding Quantization

Quantization reduces model precision to save VRAM at some quality cost:

| Quantization | Bits | VRAM Savings | Quality Impact |
|---|---|---|---|
| FP16 | 16-bit | None (baseline) | Full quality |
| Q8 | 8-bit | ~50% | Negligible loss |
| Q6_K | 6-bit | ~62% | Very minor loss |
| Q5_K_M | 5-bit | ~69% | Minor loss |
| Q4_K_M | 4-bit | ~75% | Noticeable on complex tasks |
| Q3_K_M | 3-bit | ~81% | Significant loss |
| Q2_K | 2-bit | ~87% | Major quality degradation |

**Recommendation:** Use Q4_K_M or Q5_K_M for the best balance of quality and VRAM usage.

---

## Things to Verify Before Starting

- [ ] **How much RAM is installed?** (32GB vs 64GB matters for 70B model offloading)
- [ ] **Latest NVIDIA drivers installed?** (RTX 5080 is new — driver support is essential)
- [ ] **CUDA recognized?** Run `nvidia-smi` to confirm
- [ ] **Sufficient disk space?** Models range from 4GB to 50GB each

---

## SFF Build Considerations

Since this is a compact Lian Li DAN A3-mATX build:
- **Monitor GPU temperatures** during sustained inference — SFF cases have limited airflow
- The ARCTIC Liquid Freezer III Pro 240 handles CPU cooling well
- **GPU thermals** under sustained load may be the bottleneck — consider custom fan curves
- Ollama inference is a sustained workload, unlike gaming which has variable load

---

## Useful Resources

- Ollama official site: https://ollama.com
- Ollama model library: https://ollama.com/library
- Open WebUI: https://github.com/open-webui/open-webui
- Continue (VS Code extension): https://continue.dev
