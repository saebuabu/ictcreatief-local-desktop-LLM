# Ollama en Open WebUI: gedeelde setup voor meerdere Windows-accounts

## Probleemstelling

Ollama draait standaard onder een specifiek Windows-account. Studenten die inloggen met een ander account hebben daardoor geen toegang tot:
- De Ollama-modellen die zijn gepulled
- De Open WebUI-instantie en accounts

De oplossing is Ollama en Open WebUI los te koppelen van een persoonlijk Windows-account door ze als gedeelde services te draaien.

---

## Probleem 1: Ollama-modellen niet zichtbaar voor andere accounts

Standaard slaat Ollama modellen op in `%USERPROFILE%\.ollama\models` — alleen zichtbaar voor het account dat ze heeft gepulled.

### Oplossing: gedeelde modellenmap instellen

1. Maak een gedeelde map aan, bijv. `C:\OllamaShared\models`
2. Stel een **systeem-brede** omgevingsvariabele in:
   - Zoek op "omgevingsvariabelen" → *Systeemeigenschappen* → *Omgevingsvariabelen*
   - Onder **Systeemvariabelen** (niet gebruikersvariabelen): voeg toe:
     - Naam: `OLLAMA_MODELS`
     - Waarde: `C:\OllamaShared\models`
3. Kopieer de bestaande modellen naar die map:
   ```
   %USERPROFILE%\.ollama\models  →  C:\OllamaShared\models
   ```
4. Geef alle studentaccounts (of "Gebruikers") leesrechten op de map

---

## Probleem 2: Ollama draait alleen als de primaire gebruiker is ingelogd

### Oplossing: Ollama als Windows-service

De officiële Ollama-installer registreert Ollama automatisch als Windows-service. Controleer of dit actief is:

```powershell
sc query ollama
```

Als de service actief is (`RUNNING`), draait Ollama altijd op de achtergrond — ook als niemand is ingelogd.

Zo niet, herinstalleer Ollama via de officiële installer op [ollama.com](https://ollama.com).

---

## Probleem 3: Open WebUI niet bereikbaar voor andere accounts

### Optie A: via Docker (aanbevolen)

Als Open WebUI via Docker Compose draait, is het al een systeemdienst. Docker zelf draait als Windows-service, waardoor Open WebUI altijd beschikbaar is via de browser — ongeacht welk Windows-account is ingelogd.

Controleer of Docker automatisch start:
- Docker Desktop → Settings → General → **Start Docker Desktop when you sign in** (voor systeemdienst werkt dit ook zonder inloggen als Docker Engine als service is ingesteld)

### Optie B: zonder Docker, via NSSM

Gebruik [NSSM (Non-Sucking Service Manager)](https://nssm.cc) om Open WebUI als Windows-service te registreren:

```bash
nssm install OpenWebUI "python" "-m open_webui serve"
nssm start OpenWebUI
```

---

## Probleem 4: Open WebUI-accounts

Open WebUI heeft een **eigen accountsysteem**, los van Windows-accounts. Studenten loggen in via de browser met een Open WebUI-account.

Als admin kun je:
- Zelf studentaccounts aanmaken via het admin-panel
- Registratie openstellen zodat studenten zelf een account aanmaken
- Rollen toewijzen: `user` of `admin`

---

## Samenvatting

| Stap | Actie |
|------|-------|
| 1 | Systeemomgevingsvariabele `OLLAMA_MODELS` instellen op `C:\OllamaShared\models` |
| 2 | Bestaande modellen kopiëren naar de gedeelde map |
| 3 | Controleren dat Ollama als Windows-service draait (`sc query ollama`) |
| 4 | Open WebUI via Docker (al een service) of via NSSM als service instellen |
| 5 | Studentaccounts aanmaken in Open WebUI via het admin-panel |

## Eindresultaat

Studenten loggen in op hun eigen Windows-account, openen de browser, navigeren naar `http://localhost:3000` (of de geconfigureerde poort), en loggen in met hun Open WebUI-account. Ze hebben toegang tot alle modellen die zijn gepulled.
