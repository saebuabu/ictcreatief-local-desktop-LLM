# Open dag-agent

Ollama-model `opendag-keuze-voor-IT` ("AI-Buddy") voor bezoekers van de open dag, te gebruiken in Open WebUI.
Gebaseerd op `llama3.1:8b`; persona en regels staan in de `Modelfile`.

## Laden op de LLM-machine

```bash
ollama create opendag-keuze-voor-IT -f docs/opendag-keuze-voor-IT/Modelfile
ollama list   # controleer of opendag-keuze-voor-IT verschijnt
```

Aanpassen? Wijzig de `Modelfile` en voer `ollama create` opnieuw uit (overschrijft het model).

## Verder configureren in Open WebUI

Het ruwe Ollama-model `opendag-keuze-voor-IT` staat als basismodel in de keuzelijst van de chat,
maar verschijnt in deze Open WebUI-versie niet vanzelf onder **Workspace → Models** — daar staan
alleen expliciet aangemaakte "workspace models" (wrappers om een basismodel heen met eigen naam,
avatar, suggestie-prompts etc.).

Voor de open dag is zo'n wrapper al aangemaakt: **AI-Buddy (Open dag)** (model-ID `ai-buddy-open-dag`,
basismodel `opendag-keuze-voor-IT:latest`). Aanpassen kan via **Workspace → Models → AI-Buddy (Open dag)**:

- naam, beschrijving en profielafbeelding
- suggestie-prompts (klikbare startvragen voor bezoekers)
- toegang: alleen zichtbaar voor een gast-gebruiker/-groep
- kennisbank (RAG) met informatie over de opleiding

Zelf opnieuw aanmaken (bijv. op een andere machine): **Workspace → Models → + Nieuwe model**,
kies basismodel `opendag-keuze-voor-IT:latest`, en vul de suggestie-prompts hieronder in.

## Suggestie-prompts voor bezoekers

Klikbare startvragen onder het chatvenster, al ingevuld in **AI-Buddy (Open dag)**. Aanpassen via
**Workspace → Models → AI-Buddy (Open dag) → Prompts → Aangepast → +**. Elke suggestie heeft een
korte titel, een optionele subtitel en de prompt zelf (de tekst die wordt verstuurd).

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

Open WebUI toont er een paar tegelijk (willekeurig gekozen uit de acht), dus acht is ruim voldoende.

## Nog invullen

- Opleiding/school in de system prompt (nu: "MBO-opleiding ICT")
- Eventueel ander basismodel (`FROM` in de Modelfile)
