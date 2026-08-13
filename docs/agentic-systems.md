# Agentic systemen: agents die met elkaar communiceren

Vervolg op [`IDEEEN.md`](../IDEEEN.md) — punt 1 ("Agentic System") en punt 5 ("Workflow
Automation met n8n"). In plaats van een apart framework zoals AutoGen of CrewAI erbij te
zetten, gebruiken we de n8n-instantie die al draait: elke agent is een n8n-workflow met
een webhook, agents roepen elkaars webhook aan, en de "denkstap" van elke agent is een
aanroep naar Ollama (of later Claude, voor taken die meer redeneerkracht nodig hebben).

Het doel is niet in de eerste plaats een kant-en-klaar product, maar begrijpen hoe agents
onderling samenwerken: taken doorgeven, elkaars werk controleren, en gedeelde status
bijhouden — zichtbaar als losse stappen in n8n's uitvoeringslog, in plaats van verstopt
in één lange prompt.

---

## Architectuur

**1. Transport (n8n).** Elke agent is een n8n-workflow die start met een Webhook-node.
Een bericht komt binnen, de agent doet zijn werk, en stuurt daarna zelf een HTTP-verzoek
naar de webhook van de volgende agent. Zo is elke stap terug te zien in n8n's
Executions-tab.

**2. Berichtprotocol.** Alle agents spreken dezelfde kleine JSON-envelope (zie
[`agentic-systems-protocol.md`](agentic-systems-protocol.md)) — met een
`from`/`to`/`performative`/`content`/`conversation_id`-structuur, losjes gebaseerd op
FIPA ACL en Google's A2A. `performative` is het werkwoord van het bericht: `request`,
`inform`, `critique`, `propose`, `revise`.

**3. Modelkeuze per agent.** De "denkstap" van elke agent-workflow is één losse
HTTP Request-node: naar Ollama (`/api/generate`, zoals in
[`n8n-setup.md`](n8n-setup.md)) of naar Claude. Snelle/simpele agents → Ollama-model
zoals `llama3.1:8b`. Agents die de echte synthese doen → een sterker model. Dit is per
agent instelbaar, geen architectuurkeuze.

**4. Gedeeld geheugen & tools (latere fases).** Een blackboard (bijv. een simpele
SQLite-tabel of n8n Data Table) waar agents gedeelde context lezen/schrijven in plaats
van de volledige geschiedenis in elk bericht mee te sturen, plus tool-agents
(websearch, rekenmachine) die via hetzelfde protocol aangeroepen worden
(`performative: "tool-call"`).

---

## Stappenplan

In één keer doorbouwen naar het einddoel (geheugen + tools + dynamische routering) is
een goede manier om vier onbekenden tegelijk te moeten debuggen. Daarom in fases — elke
fase is een werkend, testbaar geheel:

- **Fase 1 (✅ getest).** Twee agents, één stap: een Coordinator ontvangt een taak,
  stuurt die door naar een Worker, de Worker vraagt het aan Ollama, antwoordt terug.
  Bewijst dat transport + protocol end-to-end werken.
- **Fase 2 (✅ deze levering).** Een Critic-agent erbij. Coordinator → Worker → Critic →
  (één keer terug naar Worker als de Critic afkeurt) → Coordinator. Introduceert
  *dynamische* routering: de Coordinator bepaalt de volgende stap op basis van de
  inhoud van een bericht (`performative`), niet op basis van een vaste pijplijn.
- **Fase 3.** Het blackboard erbij. Agents sturen niet meer de volledige geschiedenis
  mee, maar lezen/schrijven een gedeelde opslag op `conversation_id`.
- **Fase 4.** Een tool-gebruikende agent (bijv. websearch) die andere agents via
  hetzelfde protocol werk kunnen laten doen.
- **Fase 5.** Een concreet lesscenario bovenop de volledige stack — bijvoorbeeld een
  "Begrippen-uitlegger": jij geeft een onderwerp, een Onderzoeker verzamelt materiaal,
  een Uitlegger stelt een les op, een Criticus checkt die, en herhaalt tot die goedgekeurd
  is. Gemengde modellen, geheugen, tools en dynamische routering, allemaal in gebruik.

---

## Fase 1 + 2 — wat er nu is

- `n8n/workflows/agentic-worker.json` — ontvangt een bericht, vraagt Ollama
  (`llama3.1:8b`), stuurt het antwoord terug in de protocol-envelope. **Ongewijzigd
  sinds Fase 1** — de Worker weet niet of hij voor het eerst of voor een herziening
  wordt aangeroepen, hij verwerkt gewoon wat er in `content` staat.
- `n8n/workflows/agentic-coordinator.json` — ontvangt een taak, stuurt door naar de
  Worker, stuurt het antwoord door naar de Critic, en routeert op basis van diens
  oordeel: bij `"performative": "critique"` gaat het antwoord één keer terug naar de
  Worker voor herziening, bij `"inform"` (goedgekeurd) gaat het antwoord direct terug.
- `n8n/workflows/agentic-critic.json` — **nieuw.** Ontvangt de taak + het antwoord van
  de Worker, vraagt Ollama om te oordelen ("PASS" of "FAIL: reden"), en stuurt dat
  oordeel terug als `performative: inform` (goedgekeurd) of `critique` (afgekeurd).
- `docs/agentic-systems-protocol.md` — het berichtformaat; Fase 2 voegt er
  `meta.herzien` (boolean) en `meta.kritiek` aan toe in het eindantwoord.

De Ollama-URL (`http://host.docker.internal:11434`) en poort 5678 voor n8n zijn al
correct ingesteld in dit project — zie [`n8n-setup.md`](n8n-setup.md). Geen wijzigingen
nodig aan `docker-compose.yml` of `.env`.

**Bewuste beperking:** dit is één begrensde herzieningsronde, geen echte lus. Blijft de
Critic ook de tweede keer afkeuren, dan krijg je toch het herziene antwoord terug (niet
opnieuw beoordeeld) — anders zou je een echte cyclus in de n8n-graaf nodig hebben, wat
zonder een gedeeld geheugen (Fase 3) al snel foutgevoelig wordt. Een echte
herhaal-tot-goedgekeurd-lus is een logische vervolgstap zodra Fase 3 er is.

### Importeren

Via de UI: **Workflows → Import from File**, in deze volgorde (de Coordinator roept de
andere twee aan, dus die moeten al bestaan): eerst `agentic-worker.json`, dan
`agentic-critic.json`, dan `agentic-coordinator.json`. Publiceer/activeer alle drie.

Via de CLI (headless, zelfde patroon als `samenvatten-webhook.json`):

```bash
docker cp n8n/workflows/agentic-worker.json n8n:/tmp/agentic-worker.json
docker exec n8n n8n import:workflow --input=/tmp/agentic-worker.json
docker exec n8n n8n publish:workflow --id=w0rkerAgent01

docker cp n8n/workflows/agentic-critic.json n8n:/tmp/agentic-critic.json
docker exec n8n n8n import:workflow --input=/tmp/agentic-critic.json
docker exec n8n n8n publish:workflow --id=criticAgent01

docker cp n8n/workflows/agentic-coordinator.json n8n:/tmp/agentic-coordinator.json
docker exec n8n n8n import:workflow --input=/tmp/agentic-coordinator.json
docker exec n8n n8n publish:workflow --id=c00rdinatorAgent01

docker restart n8n
```

> Had je Fase 1 al geïmporteerd? Importeer `agentic-coordinator.json` opnieuw (zelfde
> `id`, dus dit overschrijft de oude versie) en importeer `agentic-critic.json` als
> nieuwe workflow — `agentic-worker.json` hoef je niet opnieuw te doen, die is niet
> gewijzigd.

### Testen

```powershell
Invoke-RestMethod -Uri http://localhost:5678/webhook/coordinator -Method Post `
  -ContentType "application/json" `
  -Body '{"task": "Leg in één alinea het verschil uit tussen een proces en een thread."}'
```

Verwacht resultaat: een JSON-envelope met `"from": "coordinator"`,
`"performative": "inform"`, het (eventueel herziene) antwoord in `"content"`, en
`"meta": { "herzien": true of false, ... }`. Bekijk de **Executions-tab** van de
Coordinator-workflow om te zien of de Critic goedkeurde (rechtstreeks pad) of afkeurde
(pad via "Bouw revise-verzoek" → Worker → "Bouw eindantwoord (herzien)").

Wil je de herzieningsroute bewust triggeren om te zien dat die werkt? Geef een taak op
die een lokaal model waarschijnlijk half goed doet, bijvoorbeeld een rekensom met een
addertje of een vraag met een strikte eis ("noem exact drie voorbeelden, niet meer en
niet minder").

### Problemen oplossen

- **Executions-tab** van elke workflow in n8n toont per node wat erin en eruit ging —
  snelste manier om te zien waar een stap misgaat.
- Coordinator time-out → check of Worker én Critic actief zijn en hun webhook-pad
  precies `worker` respectievelijk `critic` is.
- Ollama-aanroep faalt → controleer met `ollama list` of `llama3.1:8b` echt
  geïnstalleerd is.
- **Switch-node ("Beslissing: goedgekeurd of herzien?") importeert niet goed** — dit is
  het node-type dat het meest verschilt tussen n8n-versies. Lukt de JSON-import niet op
  dit specifieke onderdeel, bouw de node dan handmatig na: één regel, `{{ $json.performative }}`
  gelijk aan `critique`, output "herzien"; fallback-output hernoemen naar "goedgekeurd".
- Antwoord komt nooit als "herzien" terug, ook niet met een expres lastige taak → de
  Critic-prompt is vrij letterlijk ("PASS" moet exact als eerste woord terugkomen);
  bekijk in de Executions-tab van de Critic-workflow wat Ollama daadwerkelijk
  antwoordde op de beoordelingsvraag.

---

## Volgende stap

Fase 3: het blackboard. Agents sturen niet meer de volledige geschiedenis rond via
`$('NodeName')`-verwijzingen binnen één n8n-executie, maar lezen/schrijven gedeelde
status op `conversation_id`. Dat maakt ook een échte herhaal-lus (in plaats van de ene
begrensde herzieningsronde uit Fase 2) haalbaar.
