# Examencoach delen met collega's via ngrok (tijdelijke test)

Doel: collega's laten testen en feedback laten geven op de Examencoach
(ontbrekende functies, finetunen van de systeemprompt). Het gaat om een
**tijdelijke** test, geen permanente voorziening.

## Uitgangspunten

- **Studenten** krijgen alleen toegang via het lokale netwerk met een lokaal
  IP (zie `docs/ollama-gedeelde-setup-windows.md`). Nooit via ngrok.
- **Collega's** krijgen alleen toegang via een tijdelijke ngrok-tunnel naar
  Open WebUI (poort 3000).
- Studenten en collega's zitten in dezelfde Open WebUI-instantie. De scheiding
  zit in de manier van toegang (lokaal IP versus tunnel) en in aparte accounts
  en groepen, niet in aparte installaties.
- Er mogen geen persoonsgegevens of echte studentdata in de test worden
  gebruikt. Verkeer loopt via de servers van ngrok (versleuteld, maar extern).
  Dit past binnen de no-cloud-eis, die alleen geldt voor privacygevoelige data.

## Voorbereiding (eenmalig)

1. **Registratie uitzetten** zolang de tunnel openstaat:
   Admin Panel → Settings → General → "Enable New Sign Ups" uit.
2. **Accounts voor collega's** zelf aanmaken (Admin Panel → Users) met rol
   `user`, nooit `admin`.
3. **Aparte groep** "Collega's testers" maken (Admin Panel → Users → Groups) en
   daar de collega's in zetten.
4. **Rechten** voor die groep op alleen wat nodig is:
   - model `Examencoach model`: Read
   - collectie `Examen readers`: Read (zodat de readers niet gewijzigd kunnen
     worden)
   - Controleer dat collega's de overige modellen niet zien (o.a. de
     "abliterated"-variant en de "KW1C Software Developer"-varianten).
5. **CORS** vastzetten op de ngrok-URL in plaats van `*`
   (`CORS_ALLOW_ORIGIN` in `.env` / docker-compose; daarna
   `docker compose up -d`). De URL is pas bekend nadat de tunnel draait, dus
   dit is een aandachtspunt per sessie.

## Tunnel starten

```
ngrok http 3000 --url <vast-domein>.ngrok-free.dev
```

Gekozen: **geen extra slot op de tunnel**, alleen de Open WebUI-login.
Redenen waarom de alternatieven afvielen:

- **`--basic-auth`** werkt niet. Open WebUI stuurt bij zijn eigen API-aanroepen
  een `Authorization: Bearer`-header mee die de `Basic`-header van de browser
  vervangt. ngrok weigert dat met een 401, waardoor de popup steeds terugkomt,
  ook met de juiste gegevens (getest op 2026-11-02).
- **`--oauth microsoft`** kan niet: inloggen met externe apps op het
  kw1c-account loopt via de schoolbeheerder.
- **`--oauth google`** werkt niet met de kw1c-adressen: de mail draait op
  Microsoft 365, dus er bestaat geen Google-account bij die adressen. Het kan
  wel met privé-Gmailadressen van collega's (`--oauth-allow-email`), maar daar
  is niet voor gekozen.

Omdat de loginpagina van Open WebUI daarmee publiek bereikbaar is, gelden extra
maatregelen:

- Registratie blijft uit; accounts maak je zelf aan.
- Sterke, unieke wachtwoorden voor `a.saebu`, `student`, `bezoeker` en de
  collega-accounts.
- Zet `student` en `bezoeker` tijdelijk uit zolang de tunnel openstaat (of
  zorg dat hun wachtwoord niet bij studenten bekend is).
- Tunnel alleen open zolang er getest wordt.
- Deel de link alleen met de testgroep.

## Feedback verzamelen

- Vraag collega's de duimpjes en reacties onder antwoorden te gebruiken
  (Open WebUI bewaart die als feedback).
- Vraag ze de bronvermelding (reader, jaar, paginanummer) te controleren.
- Laat ze concreet noteren: welke vraag, welk antwoord, wat ontbrak of klopte
  niet. Dit is de input voor de systeemprompt (`docs/examen-rag-model.md`,
  stap 4).
- Spreek af waar extra feedback (bijvoorbeeld een gedeeld document of
  formulier) naartoe gaat, zodat het niet alleen in de chats staat.

## Capaciteit

Eén RTX 5080 (16 GB VRAM) wordt gedeeld. Veel gelijktijdige testers geeft
wachttijden. Stel zo nodig `OLLAMA_NUM_PARALLEL` af met
`scripts/belastingtest.py`.

## Afronden

1. Tunnel stoppen (Ctrl+C in het ngrok-venster).
2. Testaccounts van collega's verwijderen of deactiveren.
3. Testchats opruimen als die niet bewaard moeten blijven voordat studenten
   het model gebruiken.
4. Feedback verwerken in de systeemprompt van het model.
5. `student` en `bezoeker` weer aanzetten als je ze had uitgezet, en
   wachtwoorden wijzigen als die tijdens de test zijn gedeeld.

## Gecontroleerde stand (2026-11-02)

Alleen gelezen, niets gewijzigd.

| Punt | Stand |
|---|---|
| Registratie | Uit (`enable_signup: False`) |
| Accounts | 1 admin (`a.saebu`), 2 gebruikers (`student`, `bezoeker`); nog geen collega-accounts |
| Modeltoegang | Alleen `examencoach-model` (studentengroep) en `ai-buddy-open-dag` (Open Dag-groep) hebben groepsrechten; overige modellen zijn niet zichtbaar voor gewone gebruikers |
| Groepen | "Studenten software development leerjaar 1" en "Open Dag Bezoekers"; "Collega's testers" bestaat nog niet |
| Standaardrechten gebruikers | Workspace, API-sleutels, web search, afbeeldingen genereren en publiek delen staan uit |
| Code interpreter | Staat **aan** voor gebruikers |
| CORS | Niet ingesteld, dus standaard `*` |
| Oude toegangsregels | `lukey03/qwen3.5-9b-abliterated` en `deepseek-r1:14b` hebben leesrechten voor een niet-bestaand gebruikers-ID (onschadelijk) |

## Controlelijst voor een sessie

- [x] Registratie uit
- [ ] Groep "Collega's testers" aangemaakt (bestaat nog niet)
- [ ] Alleen collega-accounts met rol `user`, in groep "Collega's testers"
- [ ] Groep heeft Read op `Examencoach model` én op de collectie `Examen readers`
- [ ] Collega's zitten niet in de studentengroep
- [ ] Code interpreter uitgezet voor gebruikers, indien gewenst (Admin Panel →
      Settings → Users → Default Permissions → Features)
- [ ] CORS vastgezet op de ngrok-URL (kan pas als de tunnel draait)
- [ ] Tunnel gestart zonder `--basic-auth` of `--oauth` (alleen Open WebUI-login)
- [ ] Link alleen met collega's gedeeld
- [ ] Wachtwoorden van `a.saebu`, `student` en `bezoeker` sterk (of de laatste
      twee tijdelijk uitgezet)
- [ ] Optioneel: oude toegangsregels van het niet-bestaande gebruikers-ID opruimen
- [ ] Na afloop: tunnel gestopt, accounts opgeruimd
