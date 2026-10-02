# Open dag-agent

Ollama-model `open-dag` ("AI-Buddy") voor bezoekers van de open dag, te gebruiken in Open WebUI.
Gebaseerd op `llama3.1:8b`; persona en regels staan in de `Modelfile`.

## Laden op de LLM-machine

```bash
ollama create open-dag -f docs/open-dag-agent/Modelfile
ollama list   # controleer of open-dag verschijnt
```

Aanpassen? Wijzig de `Modelfile` en voer `ollama create` opnieuw uit (overschrijft het model).

## Verder configureren in Open WebUI

Het model `open-dag` staat daarna in de modellenlijst. Via **Workspace → Models → open-dag**
kun je o.a. instellen:

- naam, beschrijving en profielafbeelding
- suggestie-prompts (klikbare startvragen voor bezoekers)
- toegang: alleen zichtbaar voor een gast-gebruiker/-groep
- kennisbank (RAG) met informatie over de opleiding

## Suggestie-prompts voor bezoekers

Klikbare startvragen onder het chatvenster. Instellen via **Workspace → Models → open-dag →
Prompt suggestions → +**. Elke suggestie heeft een korte titel, een optionele subtitel en de
prompt zelf (de tekst die wordt verstuurd).

| Titel | Subtitel | Prompt |
|---|---|---|
| Wordt IT overbodig? | Neemt AI het werk over? | Ik heb gehoord dat AI straks alle IT-ers vervangt. Is dat zo? |
| Moet ik nog leren programmeren? | Of doet AI dat voor me? | Als AI code kan schrijven, moet ik dan nog leren programmeren? |
| Zit er altijd een fout in? | Laat het me zien | Schrijf een kort stukje code en laat me zien hoe ik kan controleren of het klopt. |
| Is IT iets voor mij? | Ik weet er nog niks van | Ik weet bijna niks van computers. Is een IT-opleiding dan iets voor mij? |
| Alleen programmeren? | Wat is er nog meer? | Wat voor soorten werk zijn er in IT, behalve programmeren? |
| Hoe werkt AI? | Uitleg zonder moeilijke woorden | Hoe werkt AI eigenlijk? Leg het uit zonder moeilijke woorden. |
| Is dit veilig? | Waar blijft mijn gesprek? | Waar gaat mijn gesprek met jou naartoe? Is dit veilig? |
| Voor ouders | Mijn kind wil IT gaan doen | Mijn kind wil een IT-opleiding gaan doen. Wat moet ik hiervan weten? |

Open WebUI toont er een paar tegelijk, dus acht is ruim voldoende.

## Nog invullen

- Opleiding/school in de system prompt (nu: "MBO-opleiding ICT")
- Eventueel ander basismodel (`FROM` in de Modelfile)
