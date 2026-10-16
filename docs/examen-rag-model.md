# Examenkandidaat-model met RAG (Open WebUI)

Doel: een apart model "Examencoach" waarvan de readers uit alle jaren de
belangrijkste bron zijn. Opbouw: een **Knowledge-collectie** (de readers) plus
een **eigen Model** (basismodel + systeemprompt + gekoppelde collectie).
ChromaDB zit al in Open WebUI; Qdrant is hiervoor niet nodig.

## 1. Readers voorbereiden

- Eén map, duidelijke bestandsnamen met vak en jaar: `Reader_Zorg_2023.pdf`.
  De bestandsnaam verschijnt als bronvermelding.
- Controleer dat PDF's echte tekst bevatten (tekst selecteerbaar). Gescande
  PDF's eerst door OCR halen, anders zijn ze leeg voor het model.
- Verouderde readers verwijderen of het jaar in de naam laten staan.

## 1b. Afbeeldingen en schema's meenemen

Open WebUI leest standaard alleen de tekstlaag van een pdf; afbeeldingen en
schema's zijn dan onzichtbaar voor de RAG. Oplossing: eerst verrijken met een
lokaal vision-model (geen cloud, past bij de privacy-eis).

```
pip install pymupdf
python scripts/reader_verrijken.py C:eaders C:eaders_md --dry-run   # telt plaatjes
python scripts/reader_verrijken.py C:eaders C:eaders_md             # beschrijven
python scripts/upload_readers.py   C:eaders_md                         # uploaden
```

Het script maakt per reader een markdown-bestand met "Pagina N"-kopjes. Elke
afbeelding of elk schema wordt vervangen/aangevuld met een tekstbeschrijving
van `qwen3-vl` (of `--model llama3.2-vision:11b`). Details:

- Ingesloten afbeeldingen worden los beschreven; kleine iconen
  (`--min-px`) worden overgeslagen.
- Schema's zijn vaak vectortekeningen. Pagina's met veel tekenelementen
  (`--min-tekeningen`, standaard 30) en zonder ingesloten afbeelding worden
  als geheel gerenderd en beschreven. Zet op 0 om dit uit te schakelen.
- Beschrijvingen worden gecachet; onderbreken en hervatten kan. Bij een fout
  (bijv. Ollama niet actief) wordt voor die reader niets geschreven.
- Het kost rekentijd (één vision-aanroep per plaatje): draai het eenmalig,
  eventueel 's nachts. Zorg dat er VRAM vrij is (LM Studio sluiten).

Beperkingen: een beschrijving is een samenvatting en kan details missen, dus
controleer een steekproef per reader. De coach kan het plaatje niet tonen,
alleen uitleggen en het paginanummer noemen; vraag daarom in de systeemprompt
om paginanummers in de bronvermelding (zie stap 4).

## 2. Embedding en RAG-instellingen

Admin Panel → Settings → Documents:

| Instelling | Waarde |
|---|---|
| Embedding Model Engine | Ollama |
| Embedding model | `nomic-embed-text:latest` |
| Chunk size / overlap | ~800–1000 / 100–150 |
| Top K | 5–8 |
| Hybrid Search | aan (helpt bij exacte termen/codes) |
| Full Context Mode | uit (alle jaren passen niet in de context) |

Wijzig je het embedding-model nadat er al documenten zijn geüpload, dan moet
alles opnieuw worden geïndexeerd.

## 3. Knowledge-collectie vullen

Handmatig: Workspace → Knowledge → + New Knowledge → "Examenreaders" → uploaden.

Of met het script (aanbevolen, ook voor nieuwe jaren). Gebruik de map met
verrijkte bestanden uit stap 1b als je afbeeldingen meeneemt:

```
# API-key: Open WebUI → Instellingen → Account → API-sleutels
set OPENWEBUI_API_KEY=sk-...
python scripts/upload_readers.py C:\pad\naar\readers --dry-run
python scripts/upload_readers.py C:\pad\naar\readers --collectie "Examenreaders"
```

Het script maakt de collectie aan indien nodig en slaat bestanden over die er
al in staan (op bestandsnaam). Opnieuw draaien met alleen een nieuwe reader is
dus veilig.

## 4. Model aanmaken

Workspace → Models → + New Model:

- **Naam:** Examencoach
- **Basismodel:** `huggingface.co/unsloth/gemma-3-12b-it-GGUF:latest` (goed
  Nederlands) of `llama3.1:8b`. Liever niet `deepseek-r1:14b` (traag, houdt
  zich minder strak aan de bron).
- **Knowledge:** koppel "Examenreaders".
- **Advanced Params:** `temperature` 0.1–0.3; `num_ctx` minimaal **8192**.
  Met de Ollama-standaard wordt de context afgekapt en werkt RAG slecht.
- **Systeemprompt:**

```
Je bent een studiecoach voor examenkandidaten.
Beantwoord vragen UITSLUITEND op basis van de meegeleverde readers.
- Staat het antwoord niet in de readers? Zeg dan duidelijk: "Dit staat niet in de readers" en verzin niets.
- Vermeld altijd uit welke reader (naam, jaar en paginanummer) je informatie komt.
- Wijkt de informatie tussen jaren af, benoem dan het verschil en noem de nieuwste versie.
- Antwoord in het Nederlands, in eenvoudige taal.
```

## 5. Toegang

Zet model en collectie op **Private** of op een specifieke groep
(Admin Panel → Users → Groups), zodat kandidaten wel kunnen chatten maar de
bronnen niet kunnen wijzigen.

## 6. Testen

- Vraag met een bekend antwoord uit een reader: klopt de bronvermelding?
- Vraag waarvan het antwoord *niet* in de readers staat: het model moet dat
  zeggen in plaats van te verzinnen.
- Slechte antwoorden: verhoog Top K, verklein chunks, of controleer of de
  PDF echt tekst bevat.

## Aandachtspunten

- "Alleen uit de bron" is via een prompt sterk waarschijnlijk, geen garantie.
  Laat kandidaten de bronvermelding controleren.
- Veel gelijktijdige kandidaten: stel `OLLAMA_NUM_PARALLEL` af met
  `scripts/belastingtest.py`.
- Let op het openstaande LM Studio-conflict (VRAM/poort) met Open WebUI.
