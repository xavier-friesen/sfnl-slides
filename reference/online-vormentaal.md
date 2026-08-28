# De vormentaal van een SFNL-scherm

Wat een SFNL-scherm goed maakt, en waaraan je ziet dat er een model achter zat. De feiten —
kleuren, letters, het logo — staan in `merk.md`; de klassen en de maten staan in
`assets/online/stijl.css`. Dit gaat over de beslissingen.

De zusterroute is `documenten-vormentaal.md`. Die beschrijft een vast blad met een snijrand en
zegt over zichzelf: *wat er niet op past, past niet, en dat hoort te blijken.* Hier is het
omgekeerde waar. Een scherm groeit mee, dus er blijkt niets, en daarom moet je hier vastleggen
wát er niet meegroeit. Dat is het hele onderwerp van dit bestand.

De metingen komen uit twee bronnen. De contrastverhoudingen zijn gerekend met
`contrast()`, `tint()` en `inkt_op_tint()` uit `scripts/gedeeld/merk.py`, dus ze zijn navertelbaar
met één opdracht. De paletmetingen op de grafiek komen uit `scripts/validate_palette.js` van de
`dataviz`-skill, met het SFNL-palet erin. En de vormbevindingen komen uit twee gebouwde dashboards:
de maatstaf in `assets/online/maatstaf/`, en een proefdashboard uit een echte opdracht — dat laatste
leverde §6 op, want daar bleek dat een pagina die alleen uit kaarten bestaat ook geen structuur
heeft.

---

## 1. Wat er wegvalt en wat erbij komt

Drie dingen uit het drukwerk bestaan hier niet, en het loont om ze bij naam te noemen, want ze
zitten in elke regel van de zusterroute verweven.

- **Er is geen snijrand.** `overflow: hidden` op een blad is aflopend werk; op een scherm is het
  tekst die weg is en die niemand kan terugscrollen. Wat op een scherm "tot de rand" betekent, is
  tot de rand van het vénster, en dat is `.volbreed` en niet `.aflopend`.
- **Er is geen folio en geen katernsom.** Geen paginanummer, geen kopregel, geen spread, geen
  deelbaar-door-vier. Eén pagina, en de lengte is wat de inhoud is.
- **Er is geen vaste zetspiegel.** Het blad is 794 px breed en dat verandert nooit; een venster is
  320 px of 2560 px en dat verandert terwijl je kijkt.

En vier dingen bestaan hier die op papier niet bestaan. Ze zijn geen extra maar onderdeel van de
vorm, en ze staan in `stijl.css` §4:

- **Focus.** Waar de toetsenbordcursor staat. Onzichtbaar op elke render, want een render heeft
  geen toetsenbord.
- **Hover.** Een toevoeging en nooit de enige drager van informatie: op een aanraakscherm bestaat
  hij niet.
- **Toetsenbordnavigatie.** De volgorde waarin je met Tab door de pagina komt, en of je overal
  komt. Een gebied dat schuift en geen `tabindex` heeft, is voor iemand zonder muis afgesloten.
- **`prefers-reduced-motion`.** Een systeeminstelling. Wie hem negeert, doet iets ergers dan wie
  geen animatie had gemaakt.

---

## 2. Donkere modus is een vormbesluit en geen instelling

Dit is het gat dat deze route bestaansrecht geeft. Navy `#21145F` is de inkt van SFNL, en op een
donkere achtergrond is navy op navy niets. "Kies een donkere variant" is daar geen antwoord op,
want de vraag is de verkeerde. De goede vraag is welke *rollen* wisselen.

### Navy wordt de grond, wit wordt de inkt

Dat is het besluit, en de meting eronder is dat het gratis is:

| | grond | inkt | verhouding |
|---|---|---|---|
| licht | wit | navy | **15,79** |
| donker | navy | wit | **15,79** |

Het is exact hetzelfde getal, want het is hetzelfde paar omgekeerd. Er komt dus geen kleur bij en
er gaat geen leesbaarheid af. Wat er wél verandert is alles wat aan navy hing.

### De rangorde klapt om, en dat is het echte gevolg

Elke merkkleur gemeten tegen zijn eigen grond:

| kleur | op wit | op navy | mag een regel dragen |
|---|---|---|---|
| navy | **15,79** | 1,00 | alleen licht |
| wit | 1,00 | **15,79** | alleen donker |
| emerald | 1,98 | **7,99** | alleen donker |
| sky | 2,32 | **6,80** | alleen donker |
| oranje | 2,51 | **6,29** | alleen donker |
| grapefruit | 3,08 | **5,13** | alleen donker |
| violet | **5,52** | 2,86 | alleen licht |
| royal | **5,85** | 2,70 | alleen licht |

Lees die tabel twee keer. **De twee kleuren die op papier een alinea mogen dragen — royal en
violet — zijn precies de twee die op donker onder de drempel zakken. En de drie die op papier
geen letter mogen dragen — emerald, sky en oranje — zijn precies de drie die op donker ruim boven
4,5 komen.** De reden is dat royal en violet dicht bij navy liggen in luminantie (0,129 en 0,140
tegen 0,017), en emerald, sky en oranje er ver boven (0,481, 0,402, 0,368).

Daaruit volgt de regel die dit hele hoofdstuk samenvat:

> **Behalve navy en wit is er geen merkkleur die in béide thema's een regel kan dragen. Een accent
> dat maar in één thema werkt, is geen accent.**

Dus: **oranje draagt op een scherm nooit een gelezen regel.** Niet op wit, want daar haalt hij
2,51; en niet op navy, want dan zou hij op licht 2,51 halen en heb je twee pagina's in plaats van
één. Dit is de fout die deze skill in zijn eigen primitievenlaag maakte: `.kicker` stond in
`var(--accent)` en `qa_online.py` meldde hem als eerste bevinding op de maatstaf. Wat er nu staat
is het merkvierkant vóór de regel en de tekst op de stille inkt — het oranje is er, het draagt
geen letter.

### De volle merkvlakken wisselen níet mee, en dat is de anker

Oranje, emerald, sky en grapefruit zijn lichte kleuren in béide thema's. Dus op een vol oranje
vlak is de inkt navy, in beide thema's, en de meting is 6,29 in beide thema's. Alleen de neutrale
laag klapt om.

Dat is geen detail maar een compositiebesluit: het geeft de pagina één element dat identiek is in
licht en donker, en dat is waaraan iemand herkent dat het twee standen van hetzelfde ding zijn en
niet twee ontwerpen. Op de maatstaf is dat de koprand.

Eén gevolg dat je moet weten: **op een vol merkvlak is het logo éénkleurig.** Het oranje "NL"
haalt op een oranje band precies 1,00 tegen zijn eigen grond. Op de eerste render van de maatstaf
was "NL" onzichtbaar en niemand zag dat het weg was — de band leek gewoon "SOCIAL FINANCE" te
dragen. `qa_online.py` meldde het als contrast 1,00; de render deed dat niet. Dat is precies
waarom die meting blokkeert.

### De neutralen zijn alpha op een merkkleur

Er komt geen grijs bij. Elke neutraal is een percentage van navy in wit (licht) of van wit in
navy (donker), geschreven als `rgba(var(--navy-rgb), .14)` — de drieling die `merk.py` daarvoor
levert. Dat is de bestaande huisrecept: `vormentaal.md` §3 zet een stille regel al op navy
alpha 70.

Alpha en niet een vaste tint, en dat is een besluit met een reden: een haarlijn ín een paneel
composeert dan over dát paneel en niet over de pagina.

| rol | licht | verhouding | donker | verhouding |
|---|---|---|---|---|
| `--grond` | wit | — | navy | — |
| `--grond-op` | navy-tint (gemeten) | 1,10 | wit .10 | 1,32 |
| `--inkt` | navy | 15,79 | wit | 15,79 |
| `--inkt-stil` | navy .70 | **6,11** | wit .70 | **8,19** |
| `--lijn` | navy .14 | 1,33 | wit .26 | 2,24 |
| `--rasterlijn` | navy .08 | 1,17 | wit .13 | 1,45 |
| `--rand` | navy .60 | **4,43** | wit .42 | **3,80** |
| `--focus` | navy | 15,79 | wit | 15,79 |

Vier dingen daaraan zijn een besluit en geen tabel.

**De haarlijn is op donker bijna twee keer zo sterk als op licht** — 2,24 tegen 1,33 — en dat is
geen inconsistentie. Dezelfde verhouding is bij lage luminantie minder goed te zien, dus een lijn
die op wit precies recessief is, verdwijnt op navy. Nagemeten op de maatstaf: op 30 procent was de
rasterlijn van de grafiek op donker luider dan de tabelregel op licht, en dáárom zijn het twee
tokens geworden. `--lijn` is voor een tabelregel en een kaartrand, `--rasterlijn` alleen voor het
raster van een grafiek.

**De besturingsrand haalt in beide thema's boven 3,0**, en dat moet ook: WCAG vraagt 3,0 voor de
rand van iets wat je kunt aanwijzen. Navy .60 op wit levert `#7A729F` en wit .42 op navy levert
`#7E77A2` — vrijwel hetzelfde punt op de lijn tussen navy en wit, van twee kanten benaderd.

**De focusring is de inkt en niet het accent.** Oranje haalt 2,51 en een focusindicator moet 3,0
halen tegen wat eromheen staat. Navy en wit halen 15,79. Op een vol merkvlak wordt de ring navy,
ook in het donkere thema, want wit op oranje is 2,51.

**Op donker is een tintpaneel 32 procent en niet 16.** De vier lichte tinten zijn uit het drukwerk
gemeten en scheiden zich van wit met 1,10 tot 1,26 — laag, en toch duidelijk te zien, want het
verschil zit in de hue. Op navy werkt dat niet: het navy domineert de mix, dus een tint van 16
procent kwam op de maatstaf uit op 1,25 tot 1,33 tegen de grond en dat was onzichtbaar. Op 32
procent is het 1,69 tot 1,91 en dan is het een paneel:

| paneel | licht | tegen de grond | donker | tegen de grond | wit erop |
|---|---|---|---|---|---|
| oranje | oranje-tint | 1,26 | oranje .32 | 1,69 | 9,34 |
| mint | mint-tint | 1,14 | emerald .32 | 1,91 | 8,26 |
| navy | navy-tint | 1,10 | wit .16 | 1,60 | 9,84 |
| royal | periwinkel | 2,19 | **periwinkel** .32 | 1,88 | 8,39 |

Let op de laatste rij. **Royal kan op donker geen tintpaneel dragen**: hij is dezelfde hue als de
grond, dus zelfs op 40 procent komt hij niet verder dan 1,44. Wat zijn plaats inneemt is
periwinkel — de gemeten tint van royal zelf, dus geen nieuwe kleur.

En wat er níet gebeurt: de lichte tinten op een donkere grond zetten. Mint-tint haalt 13,82 tegen
navy, dus het zou "werken", maar een lichtgroen paneel op een donkere pagina is een gat van licht,
en de meting die daar telt is niet contrast maar adaptatie.

### De body draagt zijn eigen grond, en dat is geen netheid

Een pagina met een doorzichtige body leent zijn grond van wat erachter staat — in een
artifactviewer is dat het thema van de host. Dan klapt de tekst om en de grond niet.

Maar het is erger dan dat, en dat is op de maatstaf nagemeten met een opzettelijk stukgemaakte
kopie. **Zonder dekkende grond composeert élke alpha-neutraal over wit in plaats van over navy.**
De donkere stand kreeg toen een wit paneel met witte tekst erin en `qa_online.py` meldde 32
contrastfouten uit één ontbrekende regel. Eén `background` op de body is dus geen hygiëne maar de
regel waar de hele donkere laag op staat.

### Drie scopes, en ze zijn er allemaal nodig

```css
:root { /* het volledige lichte palet */ }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { /* donker */ } }
:root[data-theme="dark"] { /* donker, nog een keer */ }
```

Elk token staat op de kale `:root`. Een token dat alleen in een donkerblok staat, bestaat in de
ongestempelde stand niet, en dat ziet niemand: de pagina rendert, de eigenschap valt stil terug.
`qa_online.py` meet dit in vier standen en het blokkeert.

De twee donkerblokken horen woordelijk gelijk te zijn. Lopen ze uit de pas, dan ziet iemand met een
donker systeem iets anders dan iemand die de schakelaar heeft gebruikt, en dat is een verschil dat
geen enkele render vindt omdat je nooit in beide standen tegelijk kijkt. `qa_online.py` vergelijkt
de twee blokken en meldt elk verschil.

### Wie de schakelaar heeft, en wie niet

Op de losse HTML-route draagt de pagina een themaschakelaar: twintig regels JavaScript, geen
afhankelijkheid, en de keuze in `localStorage` binnen een `try`/`catch` — want in een privévenster
en in een thumbnailrender gooit de accessor zelf.

In een artifact draagt hij er géén. Daar stempelt de viewer zelf `data-theme` op de root, en twee
schakelaars op één pagina is er één te veel. `bouw.py --artifact` haalt hem eruit.

---

## 3. De breedte groeit, de maatladder niet

Op een blad is de zetspiegel vast en de maat vast. Op een scherm groeit de breedte. De vraag is
dan wat er meegroeit, en het antwoord is smaller dan je verwacht.

### Wat vast staat

**De maatladder, in px, in beide thema's, op elke breedte.** Zes maten:

| rol | maat | regelafstand | waarvoor |
|---|---|---|---|
| `--m-mini` | 12 px | 1,4 | het label: kapitaal, gespatieerd, nooit een zin |
| `--m-klein` | 13 px | 20 px | bijschrift, bron, tabelcel |
| `--m-body` | 16 px | 26 px | lopende tekst |
| `--m-kop` | 20 px | 1,25 | sectiekop |
| `--m-titel` | 30 px | 1,14 | paginatitel, uitspraak |
| `--m-display` | 46 px | 1,02 | een kerncijfer |

Dat is een andere ladder dan het drukwerk (10/13 pt = 13,33/17,33 px) en dat hoort ook: een blad
ligt op 35 cm en een scherm op 50 tot 70.

**Geen `clamp()` op de viewport voor tekst.** Dat is het scherpste besluit hier, en het gaat tegen
de gewoonte in. De reden is meetbaarheid: een maat die van de vensterbreedte afhangt, geeft op
1440 px een andere verhouding tussen titel en body dan op 600 px, dus de hiërarchie die je op de
ene breedte hebt ontworpen bestaat op de andere niet — en `qa_online.py` kan de maten niet meer
tellen, want er zijn er dan geen zes maar oneindig veel. Wil je een kop op een smal scherm kleiner,
dan zet je hem op een lagere trede van de ladder in een mediaquery. Dan is het nog steeds de
ladder.

**De leesmaat, in tekens.** `--maat` is 34em, dus 544 px bij 16 px, en dat is ongeveer 70 tekens.
Gerekend met 0,485 px per teken per px lettergrootte — hetzelfde getal dat `qa_document.py` voor
Lato Light gebruikt. Alles wat werkelijk gelezen wordt staat binnen die breedte, ook als het dek
1200 px is: een regel van 1120 px zet 144 tekens en dan raakt het oog de volgende regel kwijt.
`qa_online.py` meldt onder 30 en boven 90.

**De verticale sprongen.** 13, 26 en 52 px, alle drie een veelvoud van de regelafstand. Dat is de
schermversie van het basisraster en het doet hetzelfde werk: twee kolommen naast elkaar blijven op
dezelfde lijnen zitten.

### Wat meebeweegt

- **Het aantal kolommen.** Eén raster, `repeat(auto-fit, minmax(var(--kolom-min), 1fr))`, en je
  kiest de mínimumbreedte en niet het aantal. Dat is de goede kant om het te kiezen: een kaart van
  250 px is een kaart, en of er drie of vier naast elkaar staan hangt van het venster af.
- **De marge.** 20 px, 40 px boven 720 en 56 px boven 1080. Ruimte mag meebewegen; letters niet.
- **De bovengrens van de pagina.** `--kader` is 1200 px. Daarboven groeit de marge en niet de
  inhoud.
- **De hoogte van de pagina.** Er is geen vulgraad en geen dood wit onderin. Een scherm houdt op
  waar de inhoud ophoudt, en dat is geen defect zoals op een blad.

### Uitvullen doet een scherm niet

Het drukwerk zet zijn lopende tekst uitgevuld met afbreking, en dat is daar de juiste keuze omdat
de kolombreedte vast is. Hier is hij dat niet: de gaten in een uitgevulde regel verschuiven per
venster en je kunt ze niet nameten. Dus vlaggend rechts, altijd, en `hyphens: none`.

---

## 4. Toegankelijkheid is hier een harde grens en geen aanwijzing

Op papier kun je 2,51 als merkteken verdedigen: er is geen schermlezer, geen toetsenbord, geen
zoomstand, en de lezer houdt het blad zelf in het licht. Op een scherm kan dat niet. Wat hieronder
staat, blokkeert.

**Contrast onder de drempel, in één van de twee thema's.** 4,5 voor lopende tekst, 3,0 voor tekst
vanaf 24 px of vanaf 18,66 px bij gewicht 700. Één thema is niet genoeg: de helft van de
contrastfouten op een scherm bestaat in precies één stand.

### De ene uitzondering uit het drukwerk erven we niet: wit op oranje

Dit is de regel die iemand later per ongeluk uit de zusterroute overneemt, dus hij staat hier
apart. `merk.md` §4 laat **wit op oranje in drukwerk toe.** Niet omdat het contrast klopt, maar
omdat het gedrukte werk het doet: de lessentekst in de lessenband van de casespread staat wit op
oranje. Daar is het een merkbesluit, gebonden aan korte tekst op display- of leadmaat in een band
of paneel, en nooit voor een getal of een bronregel.

De drie getallen die er bij horen, en let op dat het er drie zijn en niet twee:

| | verhouding | op een scherm |
|---|---|---|
| oranje als inkt op wit | **2,51** | nooit goed, in geen enkel medium |
| navy op een oranje vlak | **6,29** | de gewone route |
| wit op een oranje vlak | **2,51** | **niet toegestaan** — in drukwerk wél |

De verhouding is symmetrisch: wit op oranje is precies zo zwak als oranje op wit. Op papier kun je
dat verdedigen als merkteken, want de lezer houdt het blad zelf schuiner, groter of dichterbij. In
een browser met een screenreader en een toetsenbord is het een toegankelijkheidsfout die niemand
voor je opvangt.

**Dus: op een oranje vlak is de inkt navy, ook op display- en leadmaat, ook in een band, en ook in
het donkere thema** — want een vol merkvlak wisselt niet mee met het thema (§2). `qa_online.py`
heeft er een eigen bevinding voor, `wit-op-oranje`, die blokkeert en de reden meegeeft. Zonder die
eigen naam zou er alleen een getal staan, en dan is de eerste reactie "maar in het rapport mag het
wel".

**Tekst die door `overflow: hidden` of `clip` wegvalt.** Er is dus tekst verdwenen en niemand kan
hem terugscrollen. `overflow-x: auto` is de reparatie en niet het defect — daar kan de lezer wél
bij, en dan hoort er `tabindex="0"` op, anders kan iemand zonder muis er niet bij.

**Een token dat in één van de vier standen niet resolveert.** Zie §2.

En dit zijn de aanwijzingen die je met een reden mag negeren, maar niet zonder erin te kijken:

- **De focusring weggehaald zonder vervanging.** `outline: none` is de meest voorkomende manier om
  een pagina onbruikbaar te maken met een toetsenbord, en je ziet het op geen enkele render.
- **Een aanraakdoel onder 24 × 24 px.** WCAG 2.2, SC 2.5.8.
- **`lang` ontbreekt op `<html>`.** Een schermlezer kiest dan de verkeerde stem.
- **Geen koppenrij, of een die van h2 naar h4 springt.** Een schermlezer navigeert op koppen; een
  pagina zonder koppen is één blok.
- **Een `<img>` zonder `alt`, of een `<svg>` zonder naam.** `alt=""` is een geldig antwoord voor
  een beeld dat niets zegt; `aria-hidden="true"` is het antwoord voor een icoon naast tekst.
- **Een `<table>` zonder `<th>`, of een `<th>` zonder `scope`.** Zonder kopcellen leest een
  schermlezer een raster losse getallen.
- **Kleur als enige codering.** Zie §5.

---

## 5. Een grafiek op een scherm

**De vormmethode is die van de `dataviz`-skill en die wordt hier niet herhaald.** Welke vorm bij
welke taak hoort, hoe een mark eruitziet, hoe de hover werkt, wanneer het geen grafiek is maar een
kerncijfer: dat staat daar. Wat hier staat zijn de párameters — het SFNL-palet, gemeten met de
validator van die skill.

### Het palet draagt drie categorieën, en niet vier

Gemeten met `node scripts/validate_palette.js` uit de `dataviz`-skill, oppervlak wit voor licht en
navy voor donker.

Zes slots (royal, oranje, emerald, sky, violet, grapefruit) valt in beide thema's af op de
normale-zichtvloer: het slechtste paar is sky ↔ emerald met ΔE 9,4, en de vloer is 15. Elke vierde
merkkleur brengt zo'n paar mee:

| paar | ΔE, normaal zicht | vloer |
|---|---|---|
| royal ↔ violet | 6,9 | 15 |
| oranje ↔ grapefruit | 8,7 | 15 |
| sky ↔ emerald | 9,4 | 15 |

**Drie slots halen het wel, en het zijn royal, oranje en emerald.** Alle paren:
CVD-scheiding het slechtst op emerald ↔ oranje met ΔE 14,5 (deutan) — boven het doel van 8 — en
op normaal zicht 25,6, ruim boven 15.

**Dat geldt in beide thema's, en alleen voor de onderlinge scheiding.** De ΔE tussen twee reeksen
hangt aan hun eigen hexwaarden en die veranderen niet met het thema. Het contrast van elke reeks
tégen de grond doet dat wél, en dat klapt om: royal haalt 5,85 op wit en 2,70 op navy, emerald
1,98 op wit en 7,99 op navy. Een set van drie die onderling even goed scheidt, oogt daarom in de
twee thema's ongelijk — en in tegengestelde richting. Wie de reeksen even luid wil hebben, moet
per thema iets anders doen: op licht is emerald de zwakste van de drie en op donker is royal het.
Dit is precies de fout die je maakt als je "dezelfde hexwaarden" als antwoord op de hele vraag
leest. Zie §2 voor de omgeklapte rangorde.

> **Een vierde categorie is geen vierde kleur.** Hij valt in "overig", of het worden kleine
> veelvouden, of het is een andere vorm. Dat is niet een SFNL-beperking die je omzeilt maar een
> eigenschap van een palet met vier blauwen en twee warme kleuren.

**En vier ítems is een andere vraag dan vier categorieën.** Dit is de vraag die een echte opdracht
oplevert en die hier eerst niet stond. Vier uitvoerders, zes gemeenten, vijf gemeenten met een
score: dat zijn geen categorieën maar waarden op één as, en ze dragen allemaal dezelfde grootheid.
Dan heb je geen vier kleuren nodig maar **één**, want de kleur codeert niets — de lengte doet dat.

De toets is één vraag: **codeert de kleur iets wat de vorm niet al zegt?** Zo nee, dan is het één
hue met een direct label per spoor, en gaat het derde slot naar iets waar er werkelijk drie zijn.
Nagemeten op een dashboard met vier uitvoerders: vier hues gaven vier keer hetzelfde te lezen, en
één hue met de doellijn erdoor gaf de vergelijking die de lezer zocht.

Een categorie is het pas als de kleur op meer dan één plek dezelfde betekenis draagt — drie
standpunten die ook in de tekst en in een tabel terugkomen, drie fasen die door de hele pagina
lopen. Dat rechtvaardigt een slot; vier balken naast elkaar niet.

### Wat er blijft staan als WARN, en wat dat verplicht

Twee dingen halen de validator niet en zijn niet op te lossen, want het zijn merkwaarden:

- **Emerald ligt buiten de lichtheidsband en onder de chromavloer** (OKLCH L 0,772, C 0,096). Op
  donker liggen oranje (0,733), sky (0,731) en grapefruit (0,687) ook boven de band.
- **Het contrast tegen het oppervlak blijft onder 3,0**: op licht oranje 2,51, emerald 1,98 en
  sky 2,32; op donker royal 2,70 en violet 2,86.

De `dataviz`-skill zegt wat een contrast-WARN verplicht, en dat is geen keuze: zichtbare labels of
een tabelweergave. Daaruit volgt de regel voor elke SFNL-grafiek:

> **Elke reeks draagt een direct label, een stip vóór zijn naam in de legenda, of staat in de
> tabel eronder. Kleur is nooit de enige codering.**

### De ordinale trap, en waar hij op donker anders loopt

Voor een grootheid — één hue, licht naar donker. Beide gevalideerd, alle vier de checks PASS:

| | trap 1 | trap 2 | trap 3 | lichte eind tegen het oppervlak | hue-spreiding |
|---|---|---|---|---|---|
| licht | periwinkel | royal | navy | 2,19 | 13° |
| donker | wit .45 in periwinkel | periwinkel | royal | 2,70 | 4° |

Op donker loopt de trap dus de andere kant op en hij is één merkwaarde korter. De reden staat in
de meting: navy ís de grond, dus het donkere eind van een blauwe trap valt ermee samen — royal
komt niet verder dan 2,70 boven navy en de eerstvolgende trede in dezelfde hue is periwinkel op
7,20. Er is geen derde, dus de derde is `color-mix` van wit in periwinkel.

En één ding dat níet in de trap mag: navy-tint als lichtste trede. Hij haalt 1,10 tegen wit en de
vloer voor het lichte eind is 2,0. Dat viel op de validator door.

### De tinttrap: vier treden van één hue, en waarvoor hij er is

De ordinale trap hierboven codeert een **grootheid** en heeft drie treden. Wat er niet was, is het
geval dat een echte opdracht bijna altijd oplevert: **verschillen binnen één categorie.** Vier
uitvoerders, zes gemeenten, vijf fasen. Het palet draagt drie categorieën en geen vier, maar dat is
hier de verkeerde meting, want dit zijn helemaal geen categorieën. Het zijn items van dezelfde
soort, en dan codeert de hue de soort en de trede de plaats.

De trap staat in `merk.TINTTRAP`: vier stappen, `vol` 100, `sterk` 70, `half` 45 en `licht` 25
procent. In `stijl.css` §7.18 zijn dat de klassen `.trap-vol` tot `.trap-licht`, en ze mengen met
de **grond** en niet met een vaste kleur — dus dezelfde declaratie geeft op licht een menging met
wit en op donker een menging met navy.

#### De trap is in de twee thema's niet dezelfde trap

Dit is het gevolg dat je niet kunt wegontwerpen, en het is de omgeklapte rangorde van §2 in zijn
scherpste vorm. Gemeten tegen de eigen grond, met tussen elke twee treden de onderlinge
verhouding:

| | `vol` | | `sterk` | | `half` | | `licht` |
|---|---|---|---|---|---|---|---|
| **licht** — royal over wit | **5,85** | 1,85 | **3,16** | 1,59 | **1,99** | 1,38 | **1,44** |
| **donker** — periwinkel over navy | **7,20** | 1,71 | **4,20** | 1,68 | **2,50** | 1,55 | **1,61** |

En dezelfde hue in het verkeerde thema, ter vergelijking:

| | `vol` | `sterk` | `half` | `licht` | kleinste sprong |
|---|---|---|---|---|---|
| royal over **navy** | 2,70 | 1,96 | 1,51 | 1,24 | **1,22** |
| emerald over **wit** | 1,98 | 1,60 | 1,35 | 1,17 | **1,15** |

**Een donkere hue draagt op licht een trap en op donker niet; een lichte hue precies andersom.**
Royal over navy komt niet verder dan 1,22 tussen twee treden en emerald over wit niet verder dan
1,15 — en dat is de band waarin een tintpaneel op de maatstaf onzichtbaar bleek (§2). Daarom staat
`--trap-rgb` per thema anders: royal op licht, periwinkel op donker. Blauw blijft blauw, de trap
blijft een trap, en de hue verschuift binnen zijn eigen familie — precies zoals `--tint-royal` dat
al deed.

> **De hue van een trap is een themabesluit en geen ontwerpbesluit.** Wie één hue voor beide
> thema's kiest, kiest er een die in één van de twee geen trap is.

#### De dode band: één trede draagt geen tekst

Op donker haalt de trede `sterk` navy 4,20 en wit 3,76. **Geen van beide inkten haalt 4,5**, en dat
is geen slecht gekozen percentage maar een eigenschap van elke trap die van de grond naar de inkt
loopt: ergens halverwege ligt een band waar beide uiteinden te ver weg zijn. Tegen een navygrond
is die band precies 3,51 tot 4,50 — het product van de twee contrasten is daar 15,79, want dat is
het contrast tussen navy en wit.

Op licht komt hij niet voor, en ook dat is een meting en geen geluk: royal haalt zelf maar 5,85
tegen wit, dus de trap is te kort om het midden te bereiken. Elke trede draagt daar navy (5,00 ·
7,93 · 10,96), behalve `vol`, die wit draagt (5,85, want navy haalt er 2,70).

Daaruit volgt de enige regel die je moet onthouden:

> **Op een trede staat alleen tekst als je hem hebt nagemeten, en op `sterk` staat op donker geen
> tekst.** Een balk, een blok of een vlakje heeft dat niet nodig: het label staat ernaast, en dat
> was toch al verplicht (§5, kleur is nooit de enige codering).

Gebruik `merk.inkt_op_tint()` voor een hue die hier niet staat en gok het niet. `stijl.css` zet de
inkt mee met de klasse, inclusief `--inkt-stil` — want navy .70 over de trede `half` haalt 4,00, en
dat is dezelfde blokkade die `.paneel--royal` op een echt dashboard opleverde.

#### Wanneer een trap en wanneer een tweede hue

Drie gevallen, en ze zijn uit elkaar te houden met één vraag: **wijst de kleur op meer dan één plek
hetzelfde ding aan?**

- **De kleur codeert iets wat de vorm niet zegt, en dat op meer dan één plek** — drie standpunten
  die in de tekst, in een tabel en in een grafiek terugkomen. Dan is het een categorie en dan is
  het een tweede hue. Er zijn er drie.
- **Items van dezelfde soort, en de vorm zegt al hoeveel** — vier balken naast elkaar, elk met een
  eigen lengte. Dan is het één hue en één tint. De trede zou een tweede ordening naast de lengte
  suggereren en er is er maar één. Dit is het geval dat op een proefdashboard voorkwam en het
  antwoord daar was één hue met de doellijn erdoor.
- **Items van dezelfde soort zónder eigen lengte, of dezelfde items op twee plekken** — de
  segmenten van een gestapelde balk, een rij vlakjes, een kolom in een tabel. Dan is het de trap.

De maatstaf doet het derde geval: vier gemeenten als vier segmenten van één balk, en dezelfde vier
treden als vlakje vóór de naam in de tabel eronder. **Een trede die maar op één plek voorkomt, is
versiering.**

En de bovengrens is vier. Onder `licht` (25 procent) wordt de sprong naar de volgende trede kleiner
dan 1,38 op licht en 1,55 op donker, en dat loopt de band in waarin je twee treden als één vlak
leest. Zijn er vijf items, dan is het geen trap maar een tabel, of het zijn er vier plus "overig".

`qa_online.py` meet dit als `trapstap`: twee opeenvolgende treden onder 1,30 zijn een bevinding, in
de stand waarin het misgaat.

### De rolverdeling, en die is niet van deze route

Grapefruit is kost of waarschuwing, emerald is baat, navy is structuur en totaal, sky en royal zijn
vrij voor categorieën zonder eigen lading, en oranje codeert buiten een set niets — daar ís hij het
accent. Dat staat in `vormentaal.md` §3, het geldt in elk medium, en het wordt hier niet opnieuw
bedacht. De statuskleuren (`--goed`, `--let-op`, `--slecht`) zijn daarmee gereserveerd en worden
nooit reeks 4.

### Een SVG schaalt zijn letters mee, en op een scherm is dat een probleem

Op een blad ken je de kaderbreedte, dus teken je 1:1 (`documenten-vormentaal.md` §11). Op een
scherm ken je hem niet. Een as-label van 13 px in een beeld dat op 720 px is getekend, staat in een
venster van 420 px op 7,6 px, en er staat niets fout in de markup.

Het antwoord staat in `stijl.css` §7.15 en het is een merkteken dat alleen hier bestaat: **de plot
is SVG en de tekst is HTML.** De SVG draagt alleen wat geen maat heeft — rasterlijnen en
polylijnen, op `preserveAspectRatio="none"` met `vector-effect="non-scaling-stroke"` zodat de
lijndikte niet meerekt. De as-labels, de punten en de legenda staan er in HTML rond en over heen,
en die houden de maatladder. Op de maatstaf staan de labels daardoor op 13 px, op 1440 px én op
420 px.

Het alternatief is de grafiek 1:1 houden en hem in een `.tabelhouder` laten schuiven. Dat mag,
en dan zeg je in de bronregel dat hij schuift.

**En een vaste kleur in een SVG is de klassieke donkeremodusfout.** `fill="#21145F"` blijft navy
terwijl de grond navy wórdt. Alles in een SVG staat op `currentColor` of op een
`var(--reeks-n)`; `qa_online.py` meldt elk `fill`- en `stroke`-attribuut dat een literale kleur
draagt.

---

## 6. Structuur: hoe een dashboard één ding wordt en geen stapel losse kaarten

Dit hoofdstuk komt uit één waarneming op vier renders. Een dashboard dat alleen uit `.kaart` en
`.paneel` bestaat, is precies wat het is: een verzameling losse kaarten met koppen ertussen.

De maatstaf zelf was daar het bewijs van, en een proefdashboard uit een echte opdracht ook. Beide
hadden vijf secties onder elkaar met niets tussen zich in dan witruimte en een `h2`. Op 1440 px
was dat 2029 en 2630 px pagina; op 420 px 3800 en 4284 px. Op die lengte is een kop van vier
woorden geen grens: je scrollt eraan voorbij en je weet niet of het volgende blok bij het vorige
hoort. En op donker is het erger dan op licht, want de kaartranden zijn er de enige lijnen en die
zijn recessief.

**De oplossing is niet meer kaarten maar minder: één ding waar de kaarten in liggen.** Vier
middelen, alle vier geoogst uit het drukwerk, en per stuk staat erbij wat het scherm er anders aan
doet. Ze staan in `stijl.css` §7.17.

### Het vlak — een sectie die als één ding leest

Uit merkteken 2 van `merktekens.md`, de kolomkopband: *twee kolommen die samen één ding zijn*. Op
een blad is dat een band bóven de kolommen, en dat kan daar, want de paginagrens sluit het blok
toch al af. Op een scherm is er geen paginagrens, dus wordt het een veld eróm heen: `.vlak`.

De vulling is dezelfde tint als `.paneel` — 1,10 op licht en 1,32 op donker — en dat is genoeg,
want het is een groot oppervlak. Wat erin ligt moet dan wél een niveau opschuiven, en dat gaat met
één regel: **binnen een vlak is de grond van een paneel de grond van de pagina.** Een `.paneel` in
een vlak keert dus terug naar wit (1,10) of naar navy (1,32), en een `.kaart` heeft niets nodig
want die draagt zijn haarlijn: navy .14 over het vlak is 1,32, wit .26 over het vlak is 2,19.

Twee dingen die je moet weten voordat je er drie neerzet:

- **Twee velden op één pagina, hooguit drie.** Drie tintvlakken onder elkaar zijn geen structuur
  meer maar een streepjespatroon, en dan is elk vlak weer even luid als de andere. Voor de derde
  sectie is er `.vlak--kaal`: alleen een haarlijn erboven en de ruimte eronder.
- **Een vlak is geen kaart die groter is geworden.** Er hoort meer dan één ding in. Eén paneel in
  een vlak is twee randen om dezelfde inhoud.

### De scheiding — de sectiekop met een lijn die doorloopt

Uit de kopregel van het blad (`documenten/stijl.css` §8.1), waar een haarlijn vanaf de tekst naar
links doorloopt tot de marge. Hier loopt hij naar rechts en draagt hij de sectiekop in plaats van
het paginanummer, want er is geen pagina om in te staan.

Dit is het goedkoopste structuurmiddel dat er is: het kost geen vlak, geen kleur en geen verticale
ruimte behalve de lijn zelf, en het bindt een kop van vier woorden aan de volle breedte van het
dek. De lijn is `--lijn` — 1,33 op licht en 2,24 op donker, dezelfde twee waarden als de tabelregel
en om dezelfde reden twee waarden (§2).

En één ding dat alleen op een scherm bestaat en dat de eerste render meteen liet zien: **op een
smal scherm past er naast de kop geen lijn meer.** Op 420 px vulde `Bevestigde uitstroom tegen het
streefpad` de hele regel en verdween de lijn — precies op de breedte waar de pagina 3900 px lang is
en de scheiding het hardst nodig is. Onder 560 px gaat de lijn daarom ónder de kop staan.

### De rail — een streep langs een blok in plaats van eronder

Uit merkteken 3, de gedraaide zijrail: *waar dit hele blok over gaat, zonder er een titelregel aan
te kosten.* De draaiing komt niet mee. Gedraaide tekst herflowt niet, een schermlezer maakt er een
losse regel op de verkeerde plek van, en op 420 px past hij niet. Wat wél meekomt is de streep:
3 px, dezelfde als `.streep`, langs de linkerkant.

`.uitspraak` doet dit al voor één alinea; `.rail` is hetzelfde merkteken voor een heel blok. Het
proefdashboard bouwde er een met de hand omdat de primitief niet bestond — dat is de betrouwbaarste
aanwijzing dat er een gat zat.

**De rail is het werk dat oranje op een scherm wél mag doen.** Hij haalt 2,51 tegen wit en 6,29
tegen navy, dus onder 3,0 in het lichte thema, en dat mag omdat hij een begin markeert en niets
codeert wat de tekst niet zegt. Draagt de rail wél informatie — deze drie blokken horen bij elkaar
en die andere niet — dan is oranje de verkeerde drager en gaat hij op `.rail--inkt`: 15,79 in beide
thema's.

Waarvoor de rail beter is dan een paneel: een toelichting náást of ónder iets waar hij bij hoort.
Op de maatstaf stond die toelichting eerst in een paneel van 400 px naast een plot van 330 px hoog,
en dan is de onderste 200 px van die kolom leeg — op licht is dat wit en op donker een gat. Een
rail bindt zonder een tweede vlak te kosten.

### De lijn ertussen — en de enige regel die het scherm hier toevoegt

Uit merkteken 12, waar vier kolommen door verticale lijnen zijn gescheiden. Op een scherm zit hier
één ding aan vast dat op een blad niet bestaat:

> **Een verticale lijn tussen twee kolommen moet horizontaal worden zodra de kolommen stapelen, en
> dat kan alleen als de kantelbreedte bekend is.**

Daarom staat `.gescheiden` op `.stapel` en op `.tweeluik` en **niet** op `.raster`. Een `.raster` is
`auto-fit` met een minimumbreedte, dus niemand — ook `stijl.css` niet — weet bij welke
vensterbreedte hij van drie naar twee naar één kolom valt. Een lijn die daar niet mee omslaat,
staat de helft van de tijd verkeerd, en op de brede render zie je dat niet.

Dit is ook het middel voor het kopblok: op de maatstaf staat de aanhef links en het paspoort rechts
met een lijn ertussen. Zonder die lijn stond het paspoort ver rechts in een leeg veld en las het
als een tweede blok.

### De sectiekoprij in een tabel

Uit merkteken 14 en 30: één volle rij tussen de gewone rijen, en daarmee worden twee tabellen één
tabel zonder een tweede kop en zonder een tweede blok. Dat is geen bijzonderheid maar een
standaardvorm — drie van de elf geoogste decks doen het, in één deck op zes slides.

Wat het scherm eraan verandert is de vulling. In het drukwerk is die rij een volle hue; hier is hij
`--grond-op` (1,10 en 1,32). Een tabel staat op een dashboard vaak in een vlak of naast een kaart,
en een verzadigde rij trekt daar de hele aandacht uit de getallen. De `th` draagt `colspan` over
alle kolommen en `scope="colgroup"`, anders leest een schermlezer hem als een gewone cel.

### Wat hiervan gemeten wordt, en wat niet

`qa_online.py` meet sinds deze ronde twee dingen die er niet waren, en beide om dezelfde reden: een
vlak draagt geen tekst van zichzelf, dus de contrasttoets ziet het niet, en of het zichtbaar is
hangt aan een grond die met het thema omklapt.

- **`vlak-thema`** — een vlak dat zich in het ene thema van zijn grond scheidt en in het andere
  niet. De vloeren zijn níet gelijk: 1,07 op licht en 1,25 op donker, en dat verschil komt recht uit
  §2. Dezelfde verhouding is bij lage luminantie minder waard.
- **`vlak-stil`** — een vlak dat zich in geen van beide thema's scheidt. Dan staat er een veld in de
  markup dat op de pagina niet bestaat.

Wat er niet gemeten wordt en dus op de render moet: hoevéél velden er staan, en of het vlak om de
goede dingen heen staat. Drie vlakken op rij haalt elke toets.

## 7. Eén drager per scherm, en de eenheid is het scherm en niet de spread

De regel uit het drukwerk houdt: elk blok heeft één element dat de boodschap draagt en de rest is
er om dat element te laten staan. Wat verandert is de eenheid waarop je beoordeelt. Op papier is
dat de spread, want de lezer ziet twee pagina's tegelijk. Hier is dat **het venster**: wat er
zichtbaar is zonder scrollen, en dat is op 1440 px iets anders dan op 420 px.

Daaruit volgen twee dingen die je alleen op de smalle render ziet:

- **Een tweeluik dat stapelt, verdubbelt de leeslengte.** Twee kolommen naast elkaar lezen als één
  blik; onder elkaar lezen ze als twee blokken, en dan is de tweede kolom vaak een herhaling van de
  eerste geworden.
- **Een kaartenrij die op één kolom valt, houdt zijn binnenmarge.** Drie kaarten van 26 px padding
  naast elkaar zijn drie kaarten; onder elkaar is het 156 px lucht in een kolom van 380.

En één ding dat op een scherm het equivalent is van de kopregel: **de titel staat in het
`<title>`-element**, want dat is wat er in de tab staat en wat iemand terugvindt in zijn
geschiedenis. `bouw.py` neemt hem uit de `<h1>` als je hem niet meegeeft.

---

## 8. De merktekens, en wat er van het drukwerk overblijft

`assets/documenten/stijl.css` heeft twintig merktekens voor een blad, en `merktekens.md` er dertig
uit elf decks. Per stuk nagegaan of hij op een scherm nog klopt.

**Wat ongewijzigd meekomt.** De streep, de haarlijn, het label, de kop, de lichte kop, de badge,
het paneel, de kaart, de uitspraak, de bronregel, de chapeau, de aanhef in plaats van een
opsomming, het paspoort (hier als `<dl>`, zodat een schermlezer de paren als paren leest), het
zelfgetekende lijnicoon op het raster van 24, en de tabel met één lijn onder de kop en een
haarlijn per rij.

**Wat gewijzigd meekomt, en dat is de structuurlaag.** Vijf merktekens uit het drukwerk die op een
scherm iets anders doen dan op een blad: het vlak (uit de kolomkopband), de scheiding (uit de
kopregel), de rail (uit de gedraaide zijrail, zonder de draaiing), de lijn tussen kolommen (uit de
gescheiden kolommen, met de kantelregel erbij) en de sectiekoprij in een tabel (met `--grond-op` in
plaats van een volle hue). Per stuk staat in §6 wat er veranderde en waarom.

**Wat niet meekomt, en waarom.**

| merkteken | waarom niet |
|---|---|
| de kopregel | er is geen hoofdstuk en geen pagina om in te staan |
| de folio | er is geen paginanummer |
| de omslag | er is geen voorblad. Het equivalent is de koprand, en die is één band en geen pagina |
| aflopend werk | er is geen snijrand. Het equivalent is `.volbreed`: tot de rand van het vénster |
| de tonale bol | half buiten het blad valt op een scherm buiten het document, en dan schuift de pagina horizontaal. Alleen binnen een container met `overflow: hidden` |
| het watermerkcijfer | hangt aan een blad van vaste hoogte; op een groeiende container landt hij elke keer ergens anders |
| de doorloop-pijl | er is geen volgende pagina |
| de katernsom | er is geen pers |

**Wat erbij komt, en alleen hier bestaat.** De sprongkoppeling naar de inhoud. De filterrij — één
rij bóven de inhoud en niet een kolom ernaast, want een filter dat je moet zoeken is geen filter.
De chip als tabelkolom (merkteken 7 uit `merktekens.md`, en op een scherm het merkteken dat het
meeste werk doet). De tabelhouder die horizontaal schuift. De grafiekhouder van §5. De
themaschakelaar. Het trapvlakje, dat dezelfde trede op twee plekken aanwijst (§5). En
`.alleen-lezer`, voor tekst die alleen een schermlezer krijgt.

**Twee dingen die op een blad geen aandacht vragen en hier wel.**

Een `<caption>` hoort bij een tabel die niet schuift. Bij een tabel die wél schuift hoort hij er
niet: de caption is een blok ter breedte van de tabel, dus hij wrapt niet binnen de scrollport en
loopt er rechts uit. Op de eerste render van de maatstaf stond er op 420 px "DEELNEMERS,
BEVESTIGDE UITSTROOM EN UITBET" en dan hield het op. De titel gaat dan als `.label` bóven de
houder, met `aria-labelledby` op de tabel.

En een band die zijn eigen verticale ruimte draagt met een `.dek` erin dat óók ruimte draagt, telt
twee keer. Op de maatstaf werd dat 26 + 56 px boven én onder, en dan staat er een oranje vlak van
190 px met vier woorden erin. Dat is de luide leegte van de weigerlijst, in de primitievenlaag
zelf.

---

## 9. De weigerlijst

Vierentwintig dingen. De eerste zes en de vier over structuur bestaan alleen op een scherm; de rest
komt uit `documenten-vormentaal.md` §12 en geldt hier net zo goed. Ze staan er allemaal omdat ze de
eerste inval zijn.

1. **Een kleur die alleen binnen een `@media (prefers-color-scheme: dark)`-blok is gedefinieerd.**
   In de ongestempelde stand bestaat hij niet, de pagina rendert, en niemand ziet het. Dit
   blokkeert.
2. **Een body zonder eigen achtergrond.** De pagina leent zijn grond van de host, én elke
   alpha-neutraal composeert dan over de verkeerde kleur. Zie §2.
3. **Een donkere modus die een omkering is in plaats van een besluit.** `filter: invert()`,
   `background: #111` met de rest ongemoeid, of één kleur vervangen en de andere twaalf niet. Dan
   is navy nog steeds de inkt en staat hij op iets donkers.
4. **Een vaste kleur in een SVG.** De grafiek blijft navy terwijl de grond navy wordt.
5. **`outline: none` zonder vervanging.** Onzichtbaar op elke render, en het sluit iedereen zonder
   muis buiten.
6. **`clamp()` op de viewport voor lopende tekst.** Dan is er geen maatladder meer en valt er niets
   na te meten. Zie §3.
7. **Een grafiek met vier of meer categoriekleuren uit dit palet.** Elke vierde brengt een paar
   onder ΔE 15 mee. Zie §5.
8. **Kleur als enige codering.** Emerald haalt 1,98 op wit; wie de reeks alleen aan zijn kleur
   herkent, herkent hem niet.
9. **Oranje op een gelezen regel.** 2,51 op wit. In geen van beide thema's, want een accent dat
   maar in één thema werkt, is geen accent.
9b. **Wit op oranje.** Ook 2,51, en de uitzondering die `merk.md` §4 voor drukwerk toestaat, erft
    deze route niet. Op een oranje vlak is de inkt navy, 6,29. Zie §4.
10. **Een horizontale scrollbalk op het document.** Een brede tabel of grafiek hoort in zijn eigen
    houder te schuiven, niet de pagina breder te duwen.
11. **Slagschaduwen.** `merk.md` §4, in elk medium. Een kaart krijgt een haarlijn in zijn eigen
    kleur.
12. **Afgeronde hoeken overal.** Twee waarden met elk een taak: nul voor panelen en kaarten, vol
    rond voor een badge, chip of pil. Vier verschillende radii is geen ontwerp.
13. **Emoji als icoon.** Een tweede lettertype op de pagina dat als chatbericht leest.
14. **Verlopen die je zelf verzint.** Er is één huisverloop en het is gemeten.
15. **Drie gelijke kaarten met een icoon, een vetgezette kop en twee regels grijze tekst.** De
    duidelijkste tell die er is. Als de drie dingen echt vergelijkbaar zijn, is het een tabel.
16. **Een tabel met randen rondom elke cel en een grijze kopbalk.** Dat is de Word-tabellook.
17. **Generieke koppen.** "Inleiding", "Achtergrond", "Belangrijkste inzichten". Een kop is een
    bewering.
18. **Alles gecentreerd.** Centreren is voor een uitspraak. Lopende tekst, labels en koppen staan
    links.
19. **Een rubriek die de gebruiker nooit heeft genoemd.** Een dashboard heeft hier een eigen vorm
    van: een filterrij die niets filtert, een tegel met een getal dat niemand heeft aangeleverd, een
    trendpijl waarvan geen tweede meting bestaat. Een model weet wat er meestal op een dashboard
    staat en vult dat in.
20. **Een verzonnen feit waar een gat zat.** Zet er een zichtbare markering neer — `[DATUM]` — want
    die vindt de gebruiker wel en een plausibel getal niet.
21. **Een pagina die alleen uit kaarten bestaat.** Vijf secties onder elkaar met niets tussen zich
    in dan witruimte en een kop. Op 420 px is dat een lint van bijna 4000 px waarin geen enkel
    element zegt waar een sectie begint. Zie §6.
22. **Drie tintvlakken onder elkaar.** Dan is het geen structuur meer maar een streepjespatroon, en
    is elk vlak weer even luid als de andere. De derde sectie krijgt `.vlak--kaal`.
23. **Een lijn tussen kolommen op een `auto-fit`-raster.** Niemand weet bij welke breedte dat
    raster stapelt, dus de lijn staat de helft van de tijd verkeerd — en op de brede render zie je
    dat niet. Alleen op een `.tweeluik`, want daar is de kantelbreedte bekend. Zie §6.
24. **Vier tinten van één hue als vier categorieën.** Een trap ordent items van dezelfde soort; hij
    codeert geen verschillende dingen. En andersom: vier balken die elk hun eigen lengte al hebben,
    krijgen één tint en geen trap. Zie §5.

---

## 10. Wat er niet in staat

Geen dashboardbibliotheek en geen sjablonen. `assets/online/stijl.css` geeft de tokens voor beide
thema's, het raster, de maatladder, de kleurregels en de merktekens; wat je ermee bouwt is elke
keer opnieuw jouw beslissing. Er zit geen `.kpi-rij` in en geen `.sidebar`.

Dat is dezelfde keuze als bij `sfnl-slides` en `sfnl-documenten`, en hij komt uit dezelfde meting:
een route waarin de vorm uit een catalogus wordt gekozen, levert pagina's op die geen van alle fout
zijn en geen van alle goed. Wie zo bouwt, kiest niet meer maar vult in.

Wat er wel is als je vastloopt: `assets/online/maatstaf/` heeft één gebouwd dashboard met zijn
fragment, en de renders in beide thema's op twee breedtes. Kijk ernaar om te weten waar de lat
ligt, niet om na te tekenen.
