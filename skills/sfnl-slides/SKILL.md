---
name: sfnl-slides
description: >
  Bouw een PowerPoint-deck in de huisstijl van Social Finance NL uit het officiële sjabloon,
  waarbij je de compositie per slide zelf ontwerpt in plaats van uit een patroonbibliotheek te
  kiezen. Gebruik deze skill wanneer de gebruiker een SFNL-presentatie, deck of pitch wil maken.
  Trigger op "SFNL deck", "SFNL presentatie", "maak een presentatie", "slides in onze huisstijl",
  "presentatie in SFNL-stijl", of elk verzoek dat SFNL of Social Finance NL combineert met
  slides, deck, presentatie of PowerPoint. Ook voor het uitbreiden van een bestaand SFNL-deck.
---

# SFNL-slides

Een deck bouwen uit het SFNL-sjabloon, waarbij de vorm van elke slide een ontwerpbeslissing is
en geen invuloefening.

De header erf je, de inhoud componeer je, en de render is je enige vormbeoordeling. Er is geen
patroonbibliotheek om uit te kiezen en geen validator die je compositie afkeurt voordat je hem
gezien hebt. Wat er wel is: een sjabloon dat de merkstijl draagt, een maatstaf om aan te
toetsen, en scripts die de OOXML-valkuilen voor je afhandelen.

## Voordat je begint

Lees drie dingen, in deze volgorde, en lees ze één keer voor de hele deck en niet per slide:

1. `reference/vormentaal.md` — de maatstaf. Wat een SFNL-slide goed maakt.
2. `assets/maatstaf/*.png` — tien slides uit decks die de vergelijking hebben gewonnen. Kijk
   ernaar. Ze zijn niet om na te tekenen maar om te weten waar de lat ligt.
3. `reference/sjabloon.md` — de feiten: welke layout waarvoor, welke placeholder waar, de
   kleurslots, en acht valkuilen die stil misgaan.

Draai daarna `python scripts/preflight.py`. Dat zegt of er een interpreter, de
Python-afhankelijkheden, een renderer en de huisstijlfonts zijn. Is er geen renderer, lees dan
eerst **Zonder renderer** onderaan; dat verandert hoe je bouwt en wat je bij oplevering zegt.

`reference/voice.md` gaat over de taal op de slide. Lees dat wanneer je de outline schrijft.

## Stap 1 — Intake

Vier vragen, en niet meer dan vier. Weet je een antwoord al uit de opdracht, sla hem over.

- **Wie leest dit, en wat moet die erna kunnen besluiten?** Dit bepaalt alles. Een deck voor
  een wethouder die moet besluiten is een ander deck dan een deck voor een projectgroep die
  moet meedenken.
- **Hoeveel slides, ongeveer?**
- **Heb je een deck of een document dat als voorbeeld dient?** Vraag dit actief. Krijg je er
  een, dan is dát de maatstaf: render het, kijk ernaar, en volg de vormentaal ervan in plaats
  van `assets/maatstaf/`.
- **Zijn er eigen foto's, cijfers of bronnen?**

## Stap 2 — Outline, en de enige poort

Schrijf één bestand `outline.md` met per slide:

- het slidenummer en de **action title**: de bewering, niet het onderwerp. "De doorlooptijd
  daalde met 39 dagen" en niet "Doorlooptijd".
- de **layout** uit `sjabloon.md`, met het nummer.
- de **boodschap** in één zin: wat moet de lezer hiervan overhouden.
- de **tekst letterlijk zoals hij op de slide komt**, inclusief cijfers en bronvermelding.

Wat je *niet* in de outline zet: de compositie. Geen patroonnaam, geen skelet, geen
kaartindeling. De vorm bepaal je tijdens het bouwen, met de render als correctie. Zet je hem
nu vast, dan ontwerp je blind.

Laat `sfnl-humanizer` over de teksten gaan vóórdat je de outline voorlegt. Tekst die ná de bouw
verandert, betekent slides opnieuw bouwen; het is dertien wijzigingen achteraf goedkoper om het
nu te doen.

**Leg de outline dan voor en wacht op goedkeuring.** Dit is de enige poort in deze skill. Ga
niet bouwen omdat de outline "duidelijk genoeg" lijkt.

## Stap 3 — Bouwen

Zes aanroepen. Alle paden hieronder zijn relatief aan de plugin-map; `$S` staat voor het pad
naar `scripts/`.

**Windows: houd de builddir kort.** De uitgepakte boom gaat 53 tekens diep, dus werk in
`C:/w/<naam>` en zet het eindbestand daarna op zijn plek. `prepare_template.py` rekent dit
vooraf na en zegt het als het niet past.

### 1. Sjabloon klaarzetten

```bash
python $S/prepare_template.py . --template <plugin>/assets/sfnl-sjabloon.potx
```

Dit pakt uit, zet het content-type van template naar presentation, gooit de meegeleverde
placeholderslide eruit en verwijdert `ppt/authors.xml`. Zonder deze stap opent PowerPoint het
resultaat in sjabloonmodus.

### 2. Slides aanmaken, in volgorde

```bash
python $S/add_slide.py unpacked slideLayout19.xml
```

Eén aanroep per slide, in de volgorde van de outline. De JSON die terugkomt vertelt je welk
bestand het werd (`slide7.xml`), welke placeholders erop staan met hun idx, hun doos in inch,
en waar ze voor zijn. Lees die JSON; dan hoef je `sjabloon.md` niet open te hebben voor de
idx-nummers.

De slide erft hiermee titel, subregel, oranje dash, logo en paginanummer uit de layout. Je
tekent die nooit zelf na.

### 3. Placeholders vullen

```bash
python $S/set_text.py unpacked/ppt/slides/slide7.xml --json '{"0":"DE TITEL IN CAPS","1":"DE SUBREGEL IN CAPS"}'
```

Een string wordt één alinea, een lijst van strings wordt een alinea per item. Titels en
subregels in kapitalen, bodytekst in normale zetting. Rechte apostrofs worden onderweg
rechtgezet.

### 4. Zelf componeren in de contentzone

Dit is het werk. De zone is `x 0.48, y 1.93, b 12.52, h 5.00`, dus rechts 13,00 en onder 6,93.
Daarbinnen ben je vrij.

Voeg je vormen toe als `<p:sp>` vóór `</p:spTree>` in de slide-XML. Een vorm heeft een
`<a:prstGeom>` (`rect`, `roundRect`, `ellipse`, `rightArrow`, `chevron`, wat je nodig hebt),
een `<a:xfrm>` met offset en extent in EMU, een vulling met `schemeClr`, en optioneel een
`<p:txBody>`. Groepeer wat bij elkaar hoort met `<p:grpSp>`. Geef elke vorm een sprekende
`name`, want `place_shapes.py` en `inspect_deck.py` werken op naam.

Eén inch is 914400 EMU. Voor *n* elementen over de volle breedte met goot *g* is de breedte
`(12.52 - g × (n - 1)) / n` en staat element *i* op `0.48 + i × (breedte + g)`.

**Benoem in delen wat later los moet kunnen bewegen.** Een kaart als één vorm met drie alinea's
erin is het snelst te schrijven, maar dan overschrijft `retext_slide.py` later label, getal en
toelichting in één keer, en kun je het getal niet apart uitlijnen. Zet je ze als `Kaart 1 label`,
`Kaart 1 getal` en `Kaart 1 toelichting` neer, dan is een latere wijziging chirurgisch en
verplaatst `place_shapes.py "Kaart 1*"` de hele kaart in één aanroep. Dat is ook de enige manier
om drie getallen naast elkaar op één baseline te houden als de labels niet even lang zijn.

Vier dingen die je bij élke eigen vorm doet, en waarom staat in `sjabloon.md` onder Valkuilen:

- een expliciete `<a:latin typeface="..."/>` op elke run, anders staat er Calibri
- `schemeClr` en nooit `srgbClr`
- een eigen `<a:p>` per lijstitem
- insets 0,2/0,2/0,15/0,15 op een vak met vulling, insets 0 op een los label of getal

Moet een rij elementen na het schrijven herverdeeld worden — drie kaarten waar er twee stonden
— dan is dat `place_shapes.py` en niet met de hand:

```bash
python $S/place_shapes.py unpacked/ppt/slides/slide7.xml --json '{"Kaart 2*": {"dx": -2.1}}'
```

### 5. Opruimen en inpakken

```bash
python $S/clean.py unpacked
python $S/office/pack.py unpacked deck.pptx --original <plugin>/assets/sfnl-sjabloon.potx
```

`clean.py` haalt lege placeholders eruit en normaliseert de XML. `pack.py` valideert tegen de
OOXML-schema's; komt daar iets uit, dan repareer je dat vóór je verder gaat.

### 6. Grafieken en tabellen, ná het inpakken

```bash
python $S/add_chart.py deck.pptx --slide 4 --data chart4.json
python $S/add_table.py deck.pptx --slide 7 --box 0.48,2.4,12.52,3.2 --data tabel7.json
```

`chart4.json` is `{"categories": [...], "series": {"Naam": [...]}}`; de reekskleuren komen uit
het thema, dus ze zijn de SFNL-kleuren. `tabel7.json` is `{"columns": [...], "rows": [...]}`.
Zonder `--box` landt een grafiek in een placeholder; met `--box x,y,b,h` zet je hem waar je
hem wil.

Deze twee gaan over de ingepakte deck en dus ná stap 5. `python-pptx` herschrijft het bestand
bij opslaan, en een `pack` daarna sloopt de grafieken die je net hebt toegevoegd.

Een echte reeks over tijd, een verdeling of een vergelijking van meer dan zes categorieën is
een native grafiek. Handgetekende staafjes zijn dat niet.

## Stap 4 — De visuele loop

Dit is niet overslaanbaar. Het is de enige plek waar de vorm beoordeeld wordt.

```bash
python $S/render.py deck.pptx png
python $S/thumbnail.py png raster-1 --cols 4
```

Kijk eerst naar het contactblad. Open op volle grootte alleen wat er verkeerd uitziet. Zet
daarna de `deck-visual-reviewer` op de renders; die kijkt met een frisse blik naar overloop,
overlap, uitlijning, halflege zones, kleur die niets zegt, en eenvormigheid over de deck.

Repareer alle bevindingen van een ronde in één keer en render opnieuw met een nieuw prefix
(`raster-2`). Doorgaan tot er niets meer te melden is.

Wat je in de eerste ronde zelf al gaat zien, en wat geen regel voor je oplost:

- Een label dat over twee regels loopt terwijl de andere labels dat niet doen. Dan staan de
  getallen eronder niet meer op één lijn, en dat leest als slordig. Kort het label in, of geef
  de labels een eigen vorm met een vaste hoogte zodat de getallen wel uitlijnen.
- Tekst die net buiten zijn vak valt. Het vak wordt kleiner of de tekst korter, niet het
  lettertype.
- Een compositie die op 4,5 in ophoudt. Maak de elementen groter, niet het gat.

## Stap 5 — Opleveren

Controleer de hygiëne:

```bash
python $S/qa_text.py deck.pptx
```

`critical` blokkeert de oplevering. `warn` is een aanwijzing: kijk ernaar en beslis.

Geef het bestand een naam zonder apostrofs of andere tekens die een browser bij downloaden
verhaspelt.

Gaat het deck als leave-behind de mail in, lever dan ook een lichte kopie. Elk gebouwd deck
weegt ruwweg 5,5 MB, want het draagt de foto's van alle 27 layouts mee, ook bij acht slides. De
lichte versie rendert pixelidentiek en scheelt ongeveer een factor vier:

```bash
python $S/office/unpack.py deck.pptx slim
python $S/clean.py slim --drop-unused-layouts
python $S/office/pack.py slim deck-licht.pptx --original <plugin>/assets/sfnl-sjabloon.potx
```

Zeg erbij wat de gebruiker opgeeft: in de lichte versie kan een collega alleen nog de layouts
kiezen die erin zitten. Het volle `deck.pptx` blijft het werkbestand.

Zeg bij oplevering welke slides je in de loop hebt aangepast en wat er open staat. Een cijfer
dat je niet hebt kunnen verifiëren noem je expliciet.

## Wat blokkeert

Vier dingen, allemaal van de soort "het bestand is stuk". Geen van de vier gaat over
vormgeving.

1. Het content-type staat niet op `presentation.main`. PowerPoint opent de deck dan in
   sjabloonmodus.
2. `pack.py` meldt een schemafout.
3. De grafieken zijn verdwenen na de laatste `pack`. Vergelijk `charts` in de JSON van
   `qa_text.py` met wat je hebt toegevoegd.
4. `qa_text.py` meldt een `critical`: een restplaceholder, een `{{MARKER}}` uit het concept,
   een sjabloonprompt, of een slide zonder inhoud.

## Zonder renderer

Meldt `preflight.py` geen renderer, dan bouw je blind. Dat verandert twee dingen.

Bouw conservatiever: minder elementen per slide, ruimere marges tussen vormen, en kort de tekst
in tot ruim binnen zijn vak in plaats van precies. Meet wat je kunt meten:

```bash
python $S/fit_title.py unpacked       # passen de titels op één regel, met het echte font
python $S/inspect_deck.py deck.pptx   # wat staat er werkelijk op elke slide
```

En zeg het bij oplevering, met zoveel woorden: dit deck is niet visueel geverifieerd. Dat is
geen formaliteit — het is het verschil tussen een deck dat gecontroleerd is en een deck waarvan
alleen de XML klopt.

## Een bestaand deck uitbreiden

Gaat het om een paar slides bij een deck dat er al is, dan is de snelle route: kijk wat de deck
doet, dupliceer de slide die al doet wat je wil, en hertekstueer hem. Dit werkt op de uitgepakte
boom, want `retext_slide.py` bewerkt slide-XML.

```bash
python $S/inspect_deck.py bestaand.pptx          # wat doet de deck, welke vormen heten hoe
python $S/office/unpack.py bestaand.pptx werk
python $S/duplicate_slide.py werk slide7.xml --after slide11.xml
python $S/retext_slide.py werk/ppt/slides/slide12.xml --list
python $S/retext_slide.py werk/ppt/slides/slide12.xml --json '{"Kaart 1 getal": "128"}'
python $S/office/pack.py werk uit.pptx --original bestaand.pptx
```

`retext_slide.py` werkt op vormnamen en houdt de runopmaak intact, dus de nieuwe tekst erft de
vormgeving van de oude. `--list` laat zien welke namen er te vullen zijn. Een `null` als waarde
verwijdert een vorm; dat is de derde kaart in een rij waar de nieuwe slide er twee nodig heeft.
Verandert daardoor het aantal elementen, herverdeel dan met `place_shapes.py`, anders blijft er
een gat aan de rechterkant staan.

Renderen en beoordelen doe je daarna net zo goed als bij een nieuwe deck.
