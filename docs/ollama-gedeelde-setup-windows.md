# Ollama en Open WebUI: gedeelde setup voor meerdere Windows-accounts

## Probleemstelling

Andere Windows-accounts op deze pc (bijv. `StudentenSoftware`) moeten de lokale LLM-omgeving
kunnen gebruiken: de Ollama-modellen, Open WebUI, n8n en de RAG-kennisbank in Qdrant.

## Huidige situatie op deze pc

| Onderdeel | Hoe het draait | Gevolg |
|---|---|---|
| Ollama | Per-gebruiker installatie in `C:\Users\abusa\AppData\Local\Programs\Ollama`, start via de opstartmap (tray-app) | **Géén Windows-service** — `sc query ollama` geeft "geen geïnstalleerde service". Draait alleen zolang `abusa` is ingelogd |
| Modellen | `C:\Users\abusa\.ollama\models` (~110 GB) | In het profiel van `abusa` |
| Docker Desktop | Start bij inloggen van `abusa`; `com.docker.service` staat op *Handmatig* | Open WebUI, n8n en Qdrant draaien alleen zolang `abusa` is ingelogd |

Alle diensten luisteren op `localhost`. Op Windows delen alle ingelogde sessies dezelfde
`localhost`, dus een ander account kan ze gebruiken zolang de sessie van `abusa` actief is.

> Let op: de officiële Ollama-installer voor Windows installeert **per gebruiker** en registreert
> **geen** Windows-service. Docker Desktop heeft altijd een ingelogde gebruiker nodig.

---

## Aanbevolen: gebruik via de browser, beheerder blijft ingelogd

Geen extra installatie nodig.

1. **Niet afmelden, maar wisselen.** De beheerder (`abusa`) gebruikt **Win+L → Andere gebruiker**
   (snelle gebruikerswisseling). De sessie blijft op de achtergrond draaien, inclusief Ollama en Docker.
2. **Open WebUI-account aanmaken.** Open WebUI heeft een eigen accountsysteem, los van Windows.
   Als admin: *Admin Panel → Users* → gebruiker toevoegen met rol `user` (of registratie openstellen).
3. **Tweede account opent `http://localhost:3000`** en logt in met het Open WebUI-account.
   Alle modellen, RAG (Qdrant) en image generation zijn beschikbaar.
4. **Optioneel n8n:** nodig extra gebruikers uit via *Settings → Users* op `http://localhost:5678`.

Het tweede account heeft zo geen toegang tot het Windows-profiel, de bestanden of de Claude-login
van `abusa` — alleen tot de webdiensten.

### Niet doen

- **Docker Desktop ook op het tweede account starten.** Docker Desktop is per gebruiker: het tweede
  account krijgt eigen, lege volumes (geen Open WebUI-accounts, n8n-workflows of Qdrant-data) en
  botst op dezelfde poorten.
- **Ollama apart installeren op het tweede account.** Dat betekent ~110 GB aan modellen dubbel op
  schijf, of gedoe met een gedeelde `OLLAMA_MODELS`-map. Voor browsergebruik is dat niet nodig.

---

## Optioneel: onafhankelijk van ingelogde gebruiker

Alleen nodig als de pc onbeheerd moet draaien zonder dat `abusa` is ingelogd. Dit is een flinke
verbouwing.

### Ollama bij opstarten via Taakplanner

1. Taakplanner → *Taak maken*:
   - *Uitvoeren ongeacht of gebruiker is aangemeld*, als account `abusa` (modellen blijven dan in
     het bestaande profiel)
   - Trigger: *Bij opstarten*
   - Actie: `C:\Users\abusa\AppData\Local\Programs\Ollama\ollama.exe` met argument `serve`
2. Verwijder de snelkoppeling `Ollama.lnk` uit de opstartmap van `abusa`, anders botsen de
   tray-app en de taak op poort `11434`.

### Docker zonder Docker Desktop

Docker Desktop kan niet draaien zonder ingelogde gebruiker. Alternatief is Docker Engine direct in
een WSL2-distributie (met systemd) te installeren en `docker-compose.yml` daar te draaien. Bestaande
volumes (Open WebUI, n8n, Qdrant) moeten dan gemigreerd worden.

---

## Samenvatting

| Stap | Actie |
|------|-------|
| 1 | Beheerder (`abusa`) blijft ingelogd; wisselen via Win+L → Andere gebruiker |
| 2 | Open WebUI-account aanmaken voor het tweede account (Admin Panel → Users) |
| 3 | Tweede account gebruikt `http://localhost:3000` in de browser |
| 4 | Optioneel: n8n-gebruiker uitnodigen; optioneel: Ollama via Taakplanner bij opstarten |
