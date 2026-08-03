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

Lees deze dingen, in deze volgorde, en lees ze één keer voor de hele deck en niet per slide:

1. `reference/vormentaal.md` — de maatstaf. Wat een SFNL-slide goed maakt.
2. `reference/adviesvorm.md` — de laag erboven: antwoord voorop, exhibitcraft, de
   schetsplicht en de weigerlijst. Wat een deck beslisklaar maakt.
3. `assets/maatstaf/*.png` — tien slides uit decks die de vergelijking hebben gewonnen. Kijk
   ernaar. Ze zijn niet om na te tekenen maar om te weten waar de lat ligt.
4. `reference/sjabloon.md` — de feiten: welke layout waarvoor, welke placeholder waar, de
   kleurslots en het alpha-recept, de volgorde binnen de XML, en negen valkuilen die stil
   misgaan.
5. De docstring van `scripts/shapes.py` — de primitieven waarmee je tekent, en waarom die er zo
   uitzien.

Draai daarna `python "${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py"` — alle scriptpaden in
deze skill zijn relatief aan de plugin-map, dus aan `${CLAUDE_PLUGIN_ROOT}`, niet aan het
project. Preflight zegt of er een interpreter, de Python-afhankelijkheden, een renderer en
de huisstijlfonts zijn. Is er geen renderer, lees dan
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

### Eerst vijf besluiten voor de hele deck

Deze vijf staan bovenaan `outline.md` en gelden voor elke slide. Neem je ze niet vooraf, dan
neem je ze per slide opnieuw en dan verspringt de deck zonder dat iemand kan zien waarom.

1. **De vier maten.** Drager 28 tot 40pt in Montserrat Light, kop 18pt Montserrat SemiBold,
   body 16pt Lato Light, voetnoot 11pt. Eén maat per rol, deckbreed. Gotham Bold staat alleen
   in de titel en komt daar uit de layout; in de contentzone schrijf je hem nooit. En de grote
   drager is de uitzondering: ten hoogste één contentslide op drie draagt hem, want een
   aandachtstrekker op elke slide trekt niets meer.
2. **De kaarttaal.** Rechte hoeken of één absolute hoekradius, en welke vullingssoort de default
   is: container op alpha, wit met een haarlijn in de eigen hue, of vol. Halverwege wisselen is
   het defect dat het snelst opvalt.
3. **Het accent, en of er meer dan één is.** Eén accentkleur naast navy is de default, en die
   houd je de hele deck vast. Meer hues komen er alleen bij als kleur iets codeert wat de lezer
   apart moet houden: categorieën, werkstromen, processtappen, of twee kanten van een afweging.
   Schrijf dan hier per hue in één woord op wat hij betekent — grapefruit is kost of
   waarschuwing, emerald is baat, navy is structuur, oranje is het punt; sky en royal zijn vrij —
   en zet bij de slides waar kleur iets doet in de outline welke rol welke hue krijgt. Daarna
   beslis je er niet meer over. Twee categorieën in dezelfde set krijgen nooit dezelfde hue, en
   twee blokken die samen één werkstroom vormen krijgen nooit twee verschillende.
4. **De twee registers.** Wijs aan welke slide bíjna helemaal wit wordt en welke echt verzadigd.
   Een deck waarin elke slide in het middengrijs ligt, is de deck die de vergelijking verloor.
5. **De titelmodus** (`voice.md`, Titels). Modus A is de default: de titel is een volle zin die
   de boodschap draagt, en er komt géén subtitel — idx 1 blijft leeg. Modus B kies je alleen
   wanneer de deck echte hoofdstukken heeft die de lezer moet kunnen terugvinden: dan is de
   titel de hoofdstuknaam, blijft hij binnen dat hoofdstuk letterlijk gelijk, hoort er bij elk
   hoofdstuk een divider, en draagt de subtitel de leidende zin van de slide. De subtitel is
   dus vooral een modus-B-instrument. Bij twijfel modus A, en schrijf op waarom.

Daarboven staat de **storyline**: het hele verhaal als één doorlopende alinea, geen bullets. Als
je dit in een minuut aan de klant moet uitleggen, wat zeg je dan? Dat is drie regels werk en het
is de plek waar een slide sneuvelt voordat hij bestaat.

Ligt er een besluit op tafel, dan staat het antwoord voorop: direct na de cover de adviesslide
met het advies, de dragende argumenten en de besluitvraag, en aan het slot dezelfde besluitvraag
met de vervolgstappen (`adviesvorm.md` §1). Begint de titelrij met context in plaats van met het
advies, dan is dat een bewuste keuze die je in de outline motiveert.

### Dan per slide

- **Titel** — de action title: de bewering, niet het onderwerp. "De doorlooptijd daalde met 39
  dagen", niet "Doorlooptijd". Vier dingen die het niet zijn: een label ("POSITIEF:"), een
  onderwerp zonder bewering, twee boodschappen in één titel, en een uitroepteken. ALL CAPS,
  maximaal twee regels en in de praktijk één — op 24pt Gotham Bold over 12,52 in gaat er
  ongeveer 48 tekens op een regel. Past hij niet, dan schrijf je hem korter; het font gaat nooit
  omlaag. En houd het over de deck consistent: titels die op de ene slide één en op de andere
  twee regels beslaan laten de contentzone per slide op een andere hoogte beginnen. In modus B
  is de titel geen bewering maar de hoofdstuknaam, staat hij op één regel, en is hij letterlijk
  gelijk op elke slide van dat hoofdstuk én op de divider ervoor — de bewering verhuist dan naar
  de subtitel en naar de drager in de contentzone.
- **Subtitel** — in modus A schrijf je er geen. Dat is de regel, niet een voorkeur: de titel
  zegt het al, en een tweede regel eronder herhaalt hem of kondigt de slide aan. De ene
  uitzondering is een feit dat nergens anders op de slide past — de periode, de afbakening,
  het scenario, de bron — en dan alleen bij een titel van één regel. In modus B is de subtitel
  het instrument dat de leidende zin draagt, en ook daar per slide optioneel: is er geen
  leidende zin, dan blijft de hoofdstuktitel alleen staan.
  Schrijf je er een, dan is het één zin van maximaal ongeveer 120 tekens, het liefst op één
  regel; twee is het maximum en drie lopen door de oranje dash op 1,72 in. De toets: kun je de
  subregel vervangen door "hieronder staat het", dan schrap je hem. Een ontbrekende subtitel is
  nooit een bevinding — niet in de QA en niet in een review.
- **Layout** — met het nummer, en kies niet standaard 19. Een tweeluik is 22, waar de
  kolomkoppen geërfde placeholders zijn die je mag herkleuren. Doorlopende tekst is 20. Een
  schema over de volle hoogte zonder titel is 17. Vier contentslides op 19 achter elkaar is de
  eenvormigheid waarop de vergelijking verloren is.
- **Boodschap** — in één zin: wat moet de lezer hiervan overhouden.
- **Drager** — welk element de boodschap draagt, gekozen uit vier: een getal, de compositie
  zelf, een kop of kernbegrip in de hue van zijn categorie, of een sluitregel. Een slide zonder
  drager gaat niet naar de bouwstap. Grote letter is daarbij de uitzondering: wijs in de outline
  aan welke slides de dragermaat van 28 tot 40pt krijgen — ten hoogste één op drie, en dat zijn
  de slides waar de boodschap werkelijk een getal of een verhouding is. Op de rest draagt
  gewicht en kleur.
- **Plattegrond in vier woorden** — "drie kaarten, open onderkant", "tabel plus conclusie",
  "vier rijen". Zet ze onder elkaar en tel ze: komt één plattegrond meer dan twee keer voor, of
  staan er twee gelijke naast elkaar, dan herschik je hier. Na het bouwen kost dat een herbouw
  van de contentzone.
- **Vorm die de inhoud vraagt** — in één woord: getal, grafiek, tabel, proces, verdeling,
  proza. Vraagt de brief "hoe werkt het" of "in welke stappen", dan is het geen lijst. Draagt de
  deck cijfers, dan zit er minstens één grafiek, tabel, schema of verdeling in.
- **Tekst** — letterlijk zoals hij op de slide komt, inclusief cijfers, eenheid en bron.
- **Herkomst** — achter elke inhoudelijke regel `[brief]`, `[dossier]` of `[aanname]`. Een
  aanname mag nooit als vaststelling op de slide; die gaat er alleen op als open vraag of als
  expliciete aanname. Zet alle aannames als lijstje onder de outline.

**Wat je niet in de outline zet: maten.** Geen inches, geen kolombreedtes, geen kaartindeling,
geen patroonnaam. De plattegrond en de drager horen er wél in — dat is de reden waarom de tekst
deze lengte heeft, en het is het enige stuk vorm dat vóór het bouwen te beoordelen is. De
uitvoering ontdek je op de render.

**Dividers.** Vanaf twee inhoudelijke hoofdstukken én zeven contentslides zijn sectiedividers
verplicht, één per hoofdstuk, uit de fotolayouts 6 t/m 16. Bij vijf of zes contentslides met
duidelijke blokken mag het. Onder vijf niet. Nooit twee achter elkaar en nooit als laatste
slide. Een foto mag het onderwerp niet tegenspreken; past er voor geen enkel hoofdstuk een
passende foto, kies dan één neutrale voor allemaal — consistentie boven variatie.

**Cover en slot.** Slide 1 is layout 1, het 2×2 kleurraster met de foto en de witte logokaart.
Past de dektitel niet op de layoutmaat, dan groeit het vak naar boven; kies niet layout 4 omdat
de titel niet past, want dat levert de vlakkere cover op. Nooit de organisatienaam als kop. De
klant-en-datumregel (idx 13) vul je als lijst van twee: de klant op regel één, de datum op
regel twee — als één regel breekt hij op de smalle placeholdermaat midden in de datum. Een
extern deck eindigt op layout 2 of 3, de oranje outro zonder tekstplaceholders. Een intern deck
eindigt op de beslis- of adviesslide.

Laat `sfnl-humanizer` over de teksten gaan vóórdat je de outline voorlegt. Tekst die ná de bouw
verandert, betekent slides opnieuw bouwen.

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

Vul per slide in **één** aanroep. Wat je niet vult haalt `clean.py` er later uit, dus een
tweede aanroep om iets weg te halen is nooit nodig — en `--drop-empty` verwijdert alles
wat je in díé aanroep niet noemt, inclusief de titel die je in de eerste al vulde. Zo
zijn hier een keer drie titels verdwenen.

### 4. Zelf componeren in de contentzone

Dit is het werk. De zone is `x 0.48, y 1.93, b 12.52, h 5.00`, dus rechts 13,00 en onder 6,93.
Daarbinnen ben je vrij.

**Eerst schetsen, dan bouwen.** Per contentslide noem je twee wezenlijk verschillende
composities voor dezelfde boodschap en kies je met een reden die over de boodschap gaat
(`adviesvorm.md` §3). Twee regels denkwerk; het voorkomt dat elke slide de eerste inval is.

**Gebruik `scripts/shapes.py`.** Dat is de primitievenlaag: vlakken, lijnen, tekstruns,
kolomrasters en — belangrijk — een hoogtemeting. Het is géén patroonbibliotheek; er zit geen
kaartenrij en geen stroomschema in. Wat je ermee bouwt is elke slide opnieuw jouw beslissing.

Waarom je hem gebruikt in plaats van zelf XML te typen: de eerste deck die met deze skill werd
gebouwd had een ad-hoc bouwlaag die `<a:ln><a:noFill/>` op elke vorm hardcodeerde en zijn lichte
vullingen met `lumMod` maakte. Daarmee waren de twee mooiste referentieslides — witte kolommen
met een haarlijn in de eigen hue, en een verzadigde kop boven een nauwelijks getint paneel —
structureel onbouwbaar, en de bouwer merkte dat niet.

```python
import sys; sys.path.insert(0, "<plugin>/scripts")
from shapes import (ZONE, Deck, aanhef, cols, drager, hoogte_van, label, para, run, streep,
                    tekst, tekst_op, vlak, vulgraad, write)

D = Deck(body=16, label=14, sluit=16, display=32)     # de vier maten, één keer
xs, w = cols(3, 0.24)                                 # raster
h = hoogte_van([(kop, 18, "Montserrat SemiBold"),     # hoe hoog moet dit blok zijn
                (txt, D.body, "Lato Light")], w)
vormen = [
    vlak("Kop 62", xs[0], ZONE["y"], w, 1.35, vulling="emerald",
         tekst=[para(drager("62", D.display,           # Montserrat Light, nooit Gotham
                            tekst_op("emerald", D.display)), algn="ctr")], anchor="ctr"),
    vlak("Kaart A", xs[0], 3.28, w, h, vulling="container:emerald", lijn=("emerald", 1),
         tekst=[para(label(kop)), para(run(txt, "Lato Light", D.body), spc_voor=600)]),
]
write("unpacked/ppt/slides/slide3.xml", vormen)
```

Wat de laag voor je regelt: alpha in plaats van `lumMod`, de `adj` van een `roundRect` uit een
absolute radius, een lijn in dezelfde hue als de vulling, de expliciete `<a:latin/>` op elke run,
`noAutofit`, de juiste elementvolgorde, `lnSpc` op 112 procent, en de tekstkleur die bij een
vulling en een puntgrootte hoort. `Deck(display=...)` weigert een drager buiten 28 tot 40pt, en
`run()` weigert Gotham Bold: die letter staat in de titel en komt uit de layout.

`hoogte_van` en `vulgraad` zijn er om de val uit `vormentaal.md` §6 te vermijden: eerst meten hoe
hoog de inhoud is, dan pas beslissen hoe je de restruimte verdeelt. Ruimte tussen de blokken is
compositie, ruimte ónderin een blok is een gat.

Wil je toch met de hand schrijven: een vorm is een `<p:sp>` vóór `</p:spTree>`, met
`<a:prstGeom>`, een `<a:xfrm>` in EMU (één inch is 914400), een vulling met `schemeClr` en
optioneel een `<p:txBody>`. Groepeer met `<p:grpSp>`, en geef elke vorm een sprekende `name`,
want `place_shapes.py` en `inspect_deck.py` werken op naam.

**Benoem in delen wat later los moet kunnen bewegen.** Een kaart als één vorm met drie alinea's
erin is het snelst te schrijven, maar dan overschrijft `retext_slide.py` later label, getal en
toelichting in één keer, en kun je het getal niet apart uitlijnen. Zet je ze als `Kaart 1 label`,
`Kaart 1 getal` en `Kaart 1 toelichting` neer, dan is een latere wijziging chirurgisch en
verplaatst `place_shapes.py "Kaart 1*"` de hele kaart in één aanroep. Dat is ook de enige manier
om drie getallen naast elkaar op één baseline te houden als de labels niet even lang zijn.

Doe je het met de hand, dan doe je deze vijf zelf, en waarom staat in `sjabloon.md` onder
Valkuilen: een expliciete `<a:latin/>` op elke run, `schemeClr` en nooit `srgbClr`, een eigen
`<a:p>` per lijstitem, `<a:noAutofit/>` in elke `bodyPr`, en insets 0,2/0,2/0,15/0,15 op een vak
met vulling tegen insets 0 op een los label of getal.

Moet een rij elementen na het schrijven herverdeeld worden — drie kaarten waar er twee stonden
— dan is dat `place_shapes.py` en niet met de hand:

```bash
python $S/place_shapes.py unpacked/ppt/slides/slide7.xml --json '{"Kaart 2*": {"dx": -2.1}}'
```

### 5. Opruimen en inpakken

```bash
python $S/fit_title.py unpacked --mode a          # of --mode b, naar besluit 5
python $S/clean.py unpacked
python $S/office/pack.py unpacked deck.pptx --original <plugin>/assets/sfnl-sjabloon.potx
```

`fit_title.py` meet de titels met het echte Gotham Bold, laat de titelbox naar boven groeien
waar hij twee regels nodig heeft, en toetst de titelmodus die je in besluit 5 koos: titels in
onderkast, in modus B een titel over twee regels, en in modus A een gevulde subtitel. Die
laatste is een `critical` zodra de titel twee regels beslaat — de gegroeide titelbox loopt er
dan over — en verder een `warn`, want in modus A schrijf je geen subtitel tenzij er een feit
staat dat nergens anders past. Een lége subtitel is nooit een melding.

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

De hoogte van een tabelbox volgt uit de rijen — ongeveer 0,36 in voor de kop plus 0,45 per
rij — en niet uit de restruimte van de zone. `add_table.py` verdeelt de gevraagde hoogte over
de rijen, dus een te hoge box levert zwevende scheidingslijnen met lucht ertussen op: dezelfde
fout als een blok oprekken tot de zone vol is (`vormentaal.md` §6), maar dan voor een tabel.

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

Als de loop schoon is, doe je één keer de beslistoets uit `adviesvorm.md` §5: de titelrij
hardop, de kneep per slide, en de vraag of de ontvanger met alleen deze deck het besluit kan
nemen. Wat daar sneuvelt is een contentfout en gaat terug naar de outline, niet naar de opmaak.

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

Vijf dingen. De eerste drie zijn van de soort "het bestand is stuk". De twee daarna gaan over
de letter, en ze staan hier alleen omdat ze te tellen zijn: Gotham Bold hoort niet in de
contentzone, en een titel die over de subtitel heen groeit laat tekst verdwijnen. Verder blokkeert
er niets op vormgeving; dat oordeel komt van de render.

1. Het content-type staat niet op `presentation.main`. PowerPoint opent de deck dan in
   sjabloonmodus.
2. `pack.py` meldt een schemafout.
3. De grafieken zijn verdwenen na de laatste `pack`. Vergelijk `charts` in de JSON van
   `qa_text.py` met wat je hebt toegevoegd.
4. `qa_text.py` meldt een `critical`: een restplaceholder, een `{{MARKER}}` uit het concept,
   een sjabloonprompt, een slide zonder inhoud, of Gotham Bold in de contentzone.
5. `fit_title.py` meldt een `critical`: een titel van twee regels boven een gevulde subtitel,
   waar de gegroeide titelbox over de subregel heen loopt.

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
