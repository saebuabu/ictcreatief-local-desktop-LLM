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

## Nog invullen

- Opleiding/school in de system prompt (nu: "MBO-opleiding ICT")
- Eventueel ander basismodel (`FROM` in de Modelfile)
