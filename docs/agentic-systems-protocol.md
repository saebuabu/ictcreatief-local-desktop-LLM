# Berichtprotocol tussen agents

Elke agent-workflow accepteert en levert deze envelope. Eén vast formaat betekent dat
agents verwisseld, aan elkaar geketend, of van nieuwe buren voorzien kunnen worden
zonder het protocol te wijzigen.

```json
{
  "conversation_id": "string — groepeert alle berichten van één taak/gesprek",
  "message_id": "string — uniek id voor dit specifieke bericht",
  "from": "string — naam van de verzendende agent, bijv. \"coordinator\"",
  "to": "string — naam van de ontvangende agent, bijv. \"worker\"",
  "performative": "request | inform | critique | propose | revise | tool-call | tool-result",
  "content": "string of object — de inhoud (taaktekst, antwoord, kritiek, enz.)",
  "meta": {
    "model": "optioneel — welk model dit bericht produceerde (bijv. \"ollama:llama3.1:8b\")",
    "timestamp": "ISO 8601"
  }
}
```

## Performatieven (de werkwoorden)

- **request** — "doe dit alsjeblieft." Coordinator → Worker: hier is een taak.
- **inform** — "hier is het resultaat." Worker → Coordinator: hier is het antwoord.
- **critique** — "dit klopt niet." Critic → Worker (vanaf Fase 2).
- **propose** — "dit stel ik voor als vervolgstap," gebruikt wanneer een agent over
  routering beslist in plaats van de taak zelf uit te voeren.
- **revise** — "probeer het opnieuw, met deze kritiek erbij." Coordinator/Critic →
  Worker (vanaf Fase 2).
- **tool-call** / **tool-result** — een agent die werk uitbesteedt aan een tool-agent
  (bijv. websearch) en het resultaat terugkrijgt (vanaf Fase 4).

## Fase 2-toevoeging: eindantwoord-velden

Het bericht dat de Coordinator uiteindelijk teruggeeft aan de aanvrager bevat twee
extra `meta`-velden, gezet nadat de Critic heeft geoordeeld:

- `meta.herzien` (boolean) — `true` als het antwoord één keer is teruggestuurd naar de
  Worker na kritiek, `false` als de Critic het antwoord direct goedkeurde.
- `meta.kritiek` (string, alleen aanwezig als `herzien: true`) — de reden die de
  Critic gaf voor de afkeuring, ter referentie.

## Afspraken

- `conversation_id` wordt één keer per taak aangemaakt en door elke stap heen
  meegegeven — dit is de sleutel voor het blackboard in Fase 3.
- Een agent gaat er nooit vanuit wie er verder nog meedoet in het gesprek; hij weet
  alleen van wie hij een bericht kreeg en waar het antwoord heen moet (`to`-veld, of een
  expliciete `reply_to` zodra driehoeksverkeer nodig is).
- Houd `content` in Fase 1 platte tekst — gestructureerde objecten (bijv. een kritiek
  met een `pass: true/false`-veld) komen erbij zodra de Critic-agent in Fase 2 bestaat.
