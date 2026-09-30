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

---

## Status en openstaande taken (stand 2026-09-30)

| # | Taak | Status |
|---|------|--------|
| 1 | **Herstarts opvangen:** automatisch inloggen voor `abusa` via Sysinternals *Autologon* (wachtwoord versleuteld), daarna vergrendelen; slaapstand uitzetten | Klaar |
| 2 | **Open WebUI bereikbaar in het netwerk** | Gekozen aanpak: eigen "AI-lokaal"-wifi (Plan B) — zie hieronder |
| 3 | **n8n (5678) en Qdrant (6333) alleen lokaal** (`127.0.0.1` in `docker-compose.yml`) | Klaar |
| 4 | **LM Studio uit autostart van `abusa`** (Run-key verwijderd en `enableLocalService` op `false` in `%USERPROFILE%\.lmstudio\settings.json`) | Klaar |
| 5 | **Gedeelde modelmap** (bijv. `C:\AIModels`) voor LM Studio en ComfyUI (`extra_model_paths.yaml`), om dubbele opslag te voorkomen | Open |

### Toelichting taak 2: netwerk

- Firewallregel is aangemaakt (als Administrator):
  ```powershell
  New-NetFirewallRule -DisplayName "Open WebUI (TCP 3000)" -Direction Inbound -Protocol TCP -LocalPort 3000 -RemoteAddress LocalSubnet -Action Allow -Profile Any
  ```
- De pc zit bekabeld op het gastnetwerk van school (netwerkprofiel "Guest", *Public*, IP via DHCP).
  Leerlingen zitten op een ander netwerk (bijv. eduroam): verkeer tussen deze netwerken wordt door
  het schoolnetwerk geblokkeerd.
- **Gekozen aanpak (stand 2026-09-30): Plan B — eigen "AI-lokaal"-wifi.** Eigen router aansluiten
  via een tweede netwerkadapter op de pc (bijv. USB-naar-ethernet), los van de bekabelde verbinding
  naar het schoolnetwerk. Leerlingen verbinden met het wifi van die router en bereiken de pc op
  `http://<ip-op-dat-netwerk>:3000`. De bestaande firewallregel (`RemoteAddress LocalSubnet`,
  `Profile Any`) dekt dit automatisch — `LocalSubnet` wordt per interface herberekend, geen
  aanpassing nodig. Voordeel: dit segment hoeft niet op internet aangesloten te zijn, dus geen
  lek naar buiten (past bij de no-cloud eis).
  - **Let op:** dit is nog niet uitgevoerd — eerst communiceren met de netwerkbeheerder (niet
    vanwege techniek, maar omdat een niet-goedgekeurde access point op schoolterrein tegen het
    beleid kan zijn en als rogue AP gedetecteerd kan worden).
- **Alternatief, niet gekozen:** netwerkbeheerder vragen om vast IP + toegang vanaf eduroam naar
  deze pc op TCP 3000 (of pc in ander VLAN); firewallregel dan uitbreiden met het IP-bereik van
  eduroam (`LocalSubnet` dekt dat niet).
- **Niet doen:** een publieke tunnel (bijv. Cloudflare) — zet de web UI op internet en botst met
  de privacy-eis. VPN-oplossingen (bijv. Tailscale) alleen in overleg met de netwerkbeheerder.

### Aandachtspunt: gedeelde GPU

Beide Windows-sessies delen dezelfde 16 GB VRAM. Als ComfyUI/LM Studio en Ollama tegelijk grote
modellen laden, crasht een van beide (out of memory) of valt Ollama terug op de CPU (veel trager).
Mogelijke maatregelen:
- Systeemvariabelen `OLLAMA_KEEP_ALIVE=1m` en `OLLAMA_MAX_LOADED_MODELS=1`
- ComfyUI starten met `--lowvram`
- Afspraken over zware image generation buiten drukke lesuren
