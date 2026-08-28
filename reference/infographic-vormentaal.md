# Vormentaal voor een infographic

Dit is de maatstaf voor een losse SFNL-infographic: een visual zonder titel en zonder kader,
die in iets anders komt te staan. Geordend van meeste naar minste effect, zodat je je eigen
compositie eraan kunt toetsen.

De basis is `reference/vormentaal.md` van de sfnl-design plugin. Die regels zijn nagemeten op
vijf decks die een blinde vergelijking wonnen en op één die het niet haalde, en ze gelden hier
onverkort. Wat hieronder staat is wat er ánders is zodra de titel wegvalt en het kader wegvalt,
plus wat er op de renders van deze skill zelf is nagemeten.

Lees dit één keer voordat je de eerste vorm tekent, samen met
`assets/infographic/vormen/vormenwoordenboek.png`. Dat woordenboek hoort bij §11 en is het gereedschap
waarmee je de vorm kiest; deze tekst gaat over wat je daarna met die vorm doet.

---

## 1. Geen titel betekent dat de bewering ín de infographic staat

Een slide heeft een titel die de boodschap draagt. Een infographic heeft die niet, en de
container eromheen draagt hem misschien wel en misschien niet. Dat is geen detail van opmaak,
het is het verschil dat alles bepaalt.

**De toets: dek de omgeving af en kijk of de infographic nog iets zegt.** Blijft er een
verzameling vlakken met labels over, dan mist er een bewering.

Vier manieren om die bewering erin te krijgen, in deze volgorde van voorkeur:

1. **De figuur zegt het zelf.** De vorm ís de bewering: de staaf die er twee keer zo lang uit
   ziet, de stroom die zichtbaar op één post uitkomt, de tijdlijn waarin het eerste gat het
   grootste is. Elk element draagt zijn eigen naam en zijn eigen getal (§9), en verder staat er
   niets. Dit is de stilste vorm en vaak de beste, want er wordt niets herhaald wat de tekening
   al laat zien.

   De toets is streng en je doet hem hardop: **wijs de plek aan waar het oog het eerst komt, en
   zeg in één zin wat de lezer daar afleest.** Is dat de zin uit de intake, dan draagt de figuur
   hem en heb je verder niets nodig. Is het antwoord "dat je het moet vergelijken" of "dat er
   vijf stappen zijn", dan draagt hij hem niet en ga je naar 2 of 3. Deze route is een
   ontwerpbesluit en geen gemakzucht: hij haalt een element weg dat je anders zou tekenen, en
   dat mag alleen als de figuur het werk overneemt.
2. **Een aparte drager**, een getal of verhouding op displaymaat, met één regel eronder —
   `€ 0` / `bij nul resultaat`. Neem hem als de figuur zelf de bewering niet draagt, of als het
   getal iets toevoegt dat nergens anders op het beeld staat. Voegt hij niets toe, dan gaat hij
   eruit: een `41` links naast een staaf waar `41` boven staat, is hetzelfde getal twee keer.
3. **Een sluitregel onderaan**, één zin van maximaal ongeveer 95 tekens, met de eerste twee tot
   vier woorden in Montserrat SemiBold en de rest in Lato Light op dezelfde maat. Dit is wat
   `m1`, `m3` en `m4` doen, onder een haarlijn.
4. **Een kopregel bovenaan**, en dit is de laatste keus. Een regel bovenaan gaat er als titel
   uitzien, en dan doet hij het werk dubbel als de container ook een titel heeft. Kies dit
   alleen als de gebruiker er expliciet om vraagt. Dat de infographic los gaat rondgaan is
   daarvoor niet genoeg; het is de aanleiding om de vraag te stellen, niet het antwoord. En het
   is één regel: een kopregel met een tweede regel eronder is een titel met een ondertitel, en
   dat is de chrome van een slide.

In de PowerPoint-route erft een slide op layout 17 het SFNL-logo en het paginanummer uit de
master. Die horen niet bij de infographic, dus ze gaan eruit met `scripts/infographic/blanco.py`; het
resultaat is een witte pagina met alleen de compositie erop. Laat je ze staan omdat de gebruiker
dat wil, houd dan de onderste 0,6 in vrij en teken ze nooit zelf na.

Wat je nooit doet: een titelbalk, een gevulde kopband met de naam van het onderwerp erin, een
ondertitel of inleidende alinea onder een kopregel, of een regel in Gotham Bold. Gotham Bold is
de titelletter van het merk en die erf je normaal uit een layout; in een infographic schrijf je
hem niet. `svg.py` weigert hem.

## 2. Geen kader, en de afsluiting doet het werk

Een omlijning om het geheel is verboden. Niet omdat het lelijk is, maar omdat de container al
een rand heeft: de slide, de kolom, het tekstkader in Word. Twee randen om hetzelfde ding
leest als een schermafbeelding die in het document is geplakt.

Wat een kader wél mag vervangen, en wat de compositie afsluit:

- **een haarlijn over de volle breedte**, navy op 20 tot 25 procent, met daaronder de drager
  links en de sluitregel rechts. Dit is wat alle vier de SVG-maatstaven doen en het is de
  rustigste afsluiting die er is.
- **een volle band tegen de onderrand**, van rand tot rand, met de sluitregel erin. Zwaarder,
  en daarom hoogstens één keer in een set; `m5` doet het.
- **niets** — als de laatste rij zelf de conclusie is.

**Aan de zijkanten houd je een optische marge van ongeveer 30pt aan.** Dit stond hier eerst
andersom — "de inhoud loopt door tot de canvasrand" — en dat was fout: los tekstwerk dat de
rand raakt leest als een schermafbeelding die er niet helemaal op past. Alleen een volle
vulling bloedt af; een band, een gekleurd vlak of een raster mag de rand halen, een letter niet.
Is de container zelf krap, dan is dat zijn probleem en niet dat van de infographic.

## 3. De achtergrond is doorzichtig, en dus wit

Een SVG uit deze skill heeft geen achtergrondvlak, tenzij je er expliciet om vraagt. Daarmee
past hij op elke witte drager en kun je hem in Word of PowerPoint over een bestaande
achtergrond leggen. Dat betekent ook: **je ontwerpt op wit en je toetst op wit.** Render met
`--wit` als je de kleuren wilt beoordelen, en zonder `--wit` als je wilt zien of er per ongeluk
een wit vlak in zit.

Zet je de infographic op een gekleurde drager, dan is dat een andere infographic: de container-
vullingen van 7 tot 12 procent verdwijnen dan in de achtergrond en de navy tekst haalt zijn
contrast niet meer. Vraag dat vooraf en ontwerp er dan op.

## 4. Hoogstens één drager, en soms geen

In een deck draagt ten hoogste één contentslide op drie een letter van 28pt of groter, want een
aandachtstrekker op elke slide trekt niets meer. In een losse infographic is er hooguit één, en
dan mag hij groot zijn.

**Maar hij is niet verplicht.** Dat stond hier eerst wél zo — "er is er maar één, dus hij mag
groot zijn, en hij hoort er te zijn" — en dat is te streng gebleken. Een figuur die zijn eigen
elementen direct labelt zegt vaak alles wat er te zeggen valt, en dan is een getal op
displaymaat ernaast een herhaling die het beeld drukker maakt zonder het duidelijker te maken.
Dat is nagemeten op een waterval: links stond `41` op 40pt en boven de laatste staaf stond
`41` op 18pt, hetzelfde getal, twee keer, met een halve canvasbreedte ertussen.

De volgorde is dus: eerst vaststellen wat de bewering draagt (§1), en daaruit volgt of er een
drager bij komt.

- **Draagt de figuur de bewering, dan is er geen aparte drager.** De ruimte die vrijkomt gaat
  naar de figuur, niet naar iets anders — een breder vlak, langere staven, meer lucht tussen de
  elementen. Wat je niet doet is er een ander element in schuiven omdat de hoek leeg voelt.
- **Voegt een getal of verhouding wél iets toe dat nergens anders op het beeld staat, dan is dát
  de drager.** Hij staat op **28 tot 40pt in Montserrat Light** en hij staat er **één keer**.
  `svg.py` en `shapes.py` weigeren een maat daarbuiten.
- **De dubbeltoets, en die is goedkoop.** Staat het getal van de drager ergens anders op het
  vlak ook? Dan draagt hij niet, dan herhaalt hij, en dan gaat hij eruit — of het getal bij het
  element gaat eruit, maar niet allebei blijven staan.
- Is er geen getal en geen verhouding die de infographic draagt, en draagt de figuur hem ook
  niet, dan draagt de compositie zelf: een kop in een accentkleur tegenover een kop in een
  andere, of de langste staaf in de rij. Dan is de drager niet groot maar zwaar en gekleurd.
- **Geen cijfers én monochroom?** Dan vallen die twee uitwegen ook weg, en dan is de drager
  **één woord of begrip op displaymaat**, met de vorm eromheen als tweede laag: de enige
  gesloten vorm op het vlak, de dikste lijn, of het enige element in het midden. Dit is geen
  noodgreep maar de gewone uitweg voor een beeld zonder cijfers.
- **De kneepoefening is de eindtoets.** Bekijk de render op een kwart formaat. Wat overblijft
  moet zijn wat de bewering draagt: de drager als je er een hebt, en anders de vorm zelf — de
  lengte, de dikte, het gat, het gekleurde deel. Blijven de pijltjes, de kadertjes of de nummers
  over, dan is de navigatie luider dan de boodschap. Blijft er níets over, dan is het beeld te
  vlak en helpt geen enkele hoeveelheid tekst eronder.

Vier maten, één maat per rol, en die leg je vast vóór de eerste vorm: drager 28–40, kop 18,
body 16, voetnoot 11. Op een smal canvas mag body naar 14 en kop naar 17, maar niet per element
— één keer, voor de hele infographic. 12pt is de vloer.

## 5. De compositie vult het canvas, en hier zit de val

Het laatste element eindigt op de onderrand. Dat is dezelfde regel als in een deck, en hij gaat
hier even vaak mis, met precies dezelfde verkeerde lezing: *maak de blokken hoger tot het vol
is.* Dan krijg je vlakken waarvan de onderste helft leeg gekleurd is, en dat leest hetzelfde als
een kale infographic.

De juiste volgorde is meten, dan verdelen:

1. Meet met `hoogte_van()` hoe hoog de inhoud van elk blok is.
2. Blijft er ruimte over, dan is het antwoord **meer inhoud, grotere letters of een andere
   plattegrond** — niet een hoger blok.
3. Wat je bewust overhoudt, verdeel je over de scheidingen en over de afsluitende band. Ruimte
   tussen de blokken is compositie; ruimte ónderin een blok is een gat.
4. Toets de vulgraad met `vulgraad()`: teksthoogte gedeeld door blokhoogte, norm 0,90.

**En het canvas is zelf een keuze.** Dit is wat een infographic van een slide onderscheidt en
het is het middel dat het snelst helpt. Een vroege versie van `m4` stond op 460 × 640pt en
hield op 472pt op: 168pt dood wit onderin. De reparatie was niet meer inhoud maar een korter
canvas. Past je compositie niet in de hoogte die je koos, verander dan éérst de hoogte.

Alleen in de PowerPoint-route kán dat niet: daar is het canvas 13,33 × 7,50 in en staat het
vast. **Nagemeten gevolg: een hele slide vraagt ongeveer twee keer de inhoud van een band van
960 × 320pt.** Dezelfde drie kaarten die een band vullen, laten op een slide de onderste 2,9 in
leeg. Op een slide is de plattegrond dus vaak rijen over de volle breedte in plaats van kolommen.

## 6. Kleur zit ook in de letter, en elke hue codeert iets

Onverkort uit de deck-vormentaal, en het middel dat het meest ontbreekt: **minstens één accent
staat als tekstkleur op wit**, niet alleen als vulling. Een gekleurde letter is stiller dan een
gevuld blok en zegt hetzelfde.

Contrast op wit, uitgerekend. `svg.py` dwingt dit af en weigert een te kleine letter in een
lichte hue. De getallen staan hier ter oriëntatie en niet als bron: `svg.py` rekent ze bij het
importeren uit met `scripts/gedeeld/merk.py`, dus ze kunnen niet meer uit de pas lopen met de
kleur die er werkelijk staat. Na te rekenen met `python scripts/gedeeld/merk.py --contrast
oranje wit`.

| kleur | op wit | mag dragen |
|---|---|---|
| navy | 15,8 | alles, ook een alinea |
| royal | 5,9 | alles, ook een alinea |
| grapefruit | 3,1 | een kop vanaf 18pt |
| oranje | 2,5 | displaymaat, of een kop vanaf 18pt |
| sky | 2,3 | idem |
| emerald | 2,0 | idem |

Ze stonden hier als 15,3 / 5,7 / 2,6, en dat waren de verhoudingen van het palet van vóór 27
augustus 2026. Geen enkele rij in de kolom "mag dragen" is erdoor veranderd; zie
`reference/merk.md` §1 voor de verschuiving per rol.

Op een volle vulling: wit op navy en royal, navy op de lichte accenten. Eén uitzondering, en
alleen voor de grootste drager: op 40pt mag wit ook op emerald, oranje en sky, want daar leest
het cijfer als vorm.

**Eén accent, tenzij kleur iets te coderen heeft.** De toets is één vraag per kleur: *wat
codeert deze hue, in één woord?* Kun je dat niet zeggen, dan gaat de kleur eruit. De vaste laag:
grapefruit is kost of waarschuwing, emerald is baat, navy is structuur en totaal, oranje is het
punt waar het om gaat. Sky en royal zijn vrij.

`m3` heeft twee hues omdat kost tegenover baat staat en de lezer die twee moet scheiden. `m1`,
`m2` en `m4` hebben er één, en gebruiken hem spaarzaam: in `m1` draagt oranje alleen de
inleg en de grootste post, de rest is navy op 16 procent. Dat is de enige reden dat er ergens
meer dan één is, en de reden dat er meestal één is.

## 6b. Een trap binnen één hue, voor verschil binnen één categorie

Het palet draagt drie categorieën en geen vier. Dat is nagemeten met de validator van de
`dataviz`-skill: royal, oranje en emerald halen alle checks, en elke vierde merkkleur brengt
een paar onder de zichtvloer mee — royal↔violet 6,9, oranje↔grapefruit 8,7, sky↔emerald 9,4,
tegen een vloer van 15. Na te rekenen met `svg.deltaE("royal", merk.HEX["violet"])`.

Maar de opdracht die langskomt is meestal ook geen vier categorieën. Het zijn **vier items van
dezelfde soort**: vier uitvoerders, zes gemeenten, vijf fasen, drie investeerders. Die dragen
allemaal dezelfde grootheid. Een tweede hue zou daar een tweede soort suggereren die er niet is,
en dan liegt de kleur. Voor dat geval is er de **tinttrap**: dezelfde hue, gemengd met wit, waarbij
de hue de soort codeert en de tint de plaats binnen die soort. `trap()` in `svg.py`, met de
waarden uit `merk.TINTTRAP`.

### Hoeveel stappen een figuur werkelijk kan dragen: drie, en alleen in een donkere hue

Vier stappen staan in `merk.py` en vier stappen haalt geen enkele hue. Gemeten met
`validate_palette.py --ordinal --surface "#FFFFFF"`, twee toetsen: elke stap moet zelf boven
2,0 contrast op het papier blijven (anders is het een leeg spoor en geen staaf), en twee
opeenvolgende stappen moeten minstens 0,06 OKLCH L uit elkaar liggen (anders is het één vlek
met een verloop). `svg.trap_draagt()` rekent beide uit; de tabel is de uitkomst, niet de bron.

| hue | stappen | het lichtste dat nog mag | wat er stukloopt op de volgende stap |
|---|---|---|---|
| navy | **3** — vol, sterk, half | `half` 2,85 op wit | `licht` haalt 1,70 |
| zwartblauw | **3** | `half` 2,54 | `licht` 1,61 |
| royal | **2** — vol, sterk | `sterk` 3,16 | `half` 1,99, net onder |
| violet | **2** | `sterk` 3,00 | `half` 1,94 |
| grapefruit | 2 | `sterk` 2,25 | `half` 1,69 |
| oranje | **1** | `vol` 2,51 | `sterk` 1,92 |
| sky | **1** | `vol` 2,32 | `sterk` 1,79 |
| emerald | **0** | — | `vol` haalt zelf maar 1,98 |

Emerald op nul is geen fout in de tabel maar dezelfde meting die in §6 emerald verbiedt tekst te
dragen onder 18pt: de volle kleur ligt al te dicht op het papier. Een volle emerald staaf mag;
een lichtere emerald staaf ernaast is er geen tweede staaf maar een vlek.

**Een tweede, onafhankelijke meting geeft hetzelfde antwoord.** Leg de navytrap langs de
categorische toets in plaats van de ordinale — dus: kun je twee vlakken uit elkaar houden? — dan
is het slechtste paar van drie stappen 18,8 en dat haalt de vloer van 15 ruim. Zet je de vierde
stap erbij, dan zakt het slechtste paar naar 14,5 en valt het eronder. Royal komt op drie
stappen uit op 13,1 en op twee op 15,6. Twee toetsen die niets van elkaar weten wijzen dezelfde
grens aan, en dat is de reden om er iets van te geloven.

De opeenvolgende afstanden zelf, ter oriëntatie (`svg.deltaE`, OKLab ×100): navy 23,9 / 18,8 /
14,5 · royal 15,6 / 13,1 / 10,1 · grapefruit 9,8 / 9,4 / 8,2 · oranje 8,6 / 8,0 / 6,7 ·
emerald 7,0 / 6,2 / 5,2. Een trap in een lichte hue is geen trap.

**Praktisch: de trap is een navytrap.** Navy is de enige hue die er drie draagt en tegelijk de
hue die in dit huis toch al structuur en totaal codeert. Dat is geen beperking maar de vorm van
het antwoord: de trap zet zes gemeenten in navy en houdt oranje vrij voor het ene ding dat het
accent is. Er is dus nog steeds **één accent naast navy** — een trap is geen tweede accent.

### Wanneer een trap mag, en wanneer niet

De toets uit §6 verandert niet: *codeert de kleur iets wat de vorm niet al zegt?* Wat daar bij
een trap uit volgt, zijn drie gevallen en ze zijn scherp te scheiden.

**Wel — de tint draagt de grootheid en de vorm draagt alleen de plaats.** Een kaart, een matrix,
een rooster van tegels, een gestapelde band, een rij vlakken van gelijke maat. Daar zegt de vorm
"waar" en verder niets, dus de tint zegt "hoeveel" en dat is nieuwe informatie. Dit is het geval
waarvoor de trap bestaat.

**Wel, maar zelden — de tint herhaalt een ordening die de figuur zelf al laat zien.** Een
gesorteerde staafgrafiek: de lengte zegt het al. De trap voegt niets toe en is dus versiering,
tenzij de figuur ook nog in zwart-wit of op een projector moet werken. Standaard: laat hem weg
en gebruik één hue met een doellijn erdoor. Bij een gesorteerde staaf is dat de goede keuze en
niet een gebrek aan fantasie.

**Niet — de tint codeert identiteit zonder grootheid.** Vier uitvoerders op alfabet in vier
tinten zetten liegt, want een trap suggereert **volgorde** en de lezer leest een rangorde die er
niet is. Dit is de valkuil, en hij is verraderlijk omdat het beeld er goed uitziet. De regel:
**een trap hoort bij een grootheid die werkelijk oploopt, of bij een sortering die de figuur zelf
laat zien.** Kun je niet in één woord zeggen wat donkerder betekent, dan gaat de trap eruit en
staat er één hue.

**Wanneer dan een tweede hue?** Als de items van verschillende soort zijn en de lezer die
soorten uit elkaar moet houden: kost tegenover baat, plan tegenover realisatie, uitvoerder
tegenover gemeente. Dan codeert de hue de soort, en dan zijn er hoogstens drie. Hue en tint
kunnen samen: twee soorten in twee hues, en binnen elke soort een trap — mits beide hues er een
dragen, dus in de praktijk navy plus één.

**En geen van beide** is nog steeds het gewone antwoord. Als lengte, positie of dikte de meting
al draagt en er is één ding dat het accent verdient, dan is dat één hue plus oranje. De trap
komt erbij wanneer de vorm de meting níet draagt.

### Twee dingen die een trap altijd nodig heeft

**Direct labelen, en dus geen legenda.** Dat staat al in §9 en het geldt hier dubbel: de vloer
van 2,0 zegt dat de lezer de stappen als *meer of minder* kan zien, niet dat hij ze kan
herkennen. Een legenda vraagt herkennen, en dat is een andere vloer (15 op `deltaE`, en die
halen alleen navy en zwartblauw; `svg.trap_herkenbaar()` rekent het uit). De twee getallen
lopen maar bij één hue uiteen: grapefruit mag twee stappen tekenen (2,25 op wit) en die twee
liggen onderling 9,8 uit elkaar, dus zichtbaar als vlak en niet uit elkaar te houden als kleur.
Een trap met een legenda is onleesbaar; een trap met labels erbij niet.

**De inkt volgt niet de stap.** Vanaf `sterk` haalt navy op elke hue ruim de 4,5 — royal 5,0,
violet 5,3, oranje 8,2, emerald 9,8, sky 8,8 — dus binnen een trap hoeft de tekstkleur niet mee
te veranderen. Twee uitzonderingen, en het zijn er echt twee: op `vol` dragen royal en violet
wit, en **navy als hue draagt wit tot en met `sterk`** (zwartblauw net zo) en pas vanaf `half`
navy. Gebruik `merk.inkt_op_tint()` of `svg.tekst_op(tint(...))` en gok het niet.

**En deze vloer geldt hier, niet overal.** `sfnl-online-design` zet vier treden royal waar
`trap_draagt()` er twee toestaat, en dat is geen divergentie die is blijven liggen maar een ander
meetpunt: op een scherm raakt elk segment aan zijn buurman, de twee lichtste treden dragen
verplicht een haarlijn, en de sprong tussen twee treden wordt gemeten in plaats van de trede tegen
de grond. Die route rekent het na met dezelfde functies — de kleinste sprong is ΔL 0,096 tegen de
vloer van 0,06 hierboven. Zie `reference/online-vormentaal.md` §5. Andersom geldt dit hoofdstuk
zodra zo'n trap in een los beeld of in drukwerk belandt.

Uitgewerkt in `assets/infographic/maatstaf/m6-tinttrap`: vier uitvoerders in één navytrap van
drie stappen, waar de breedte het deelnemersaantal draagt en de tint het plaatsingspercentage.

## 7. Een container is bijna wit, en een lijn maakt er een kaart van

Een lichte vulling is `fill-opacity` op de volle kleur, per hue gekalibreerd: navy 0,07, royal
0,10, sky 0,10, emerald 0,10, grapefruit 0,09, oranje 0,12. Nooit een lichtere hex erbij
verzinnen — die leest als eigen kleur in plaats van als achtergrond. `container()` doet dit.

**Een vlak van 9 procent vulling heeft een 1pt lijn in exact dezelfde hue nodig om als kaart te
lezen in plaats van als vlek.** Dit is de best gevalideerde vormregel die er is. `vlak()` zet
die lijn er automatisch bij zodra de vulling doorzichtig is. Een grijze of navy rand eromheen
maakt er een Word-tabel van.

Wil je écht geen lijn — bij een staaf, een spoor onder een staaf, een volvlak — geef dan
`lijn_=None`. Dat is expliciet, en dat is bewust: in een vroege versie met staven kregen de
grijze sporen eronder allemaal een navy haarlijn, en dat maakte er een tabel van.

Eén kaarttaal, één hoekradius, absoluut in punten, en halverwege wisselen is het defect dat het
snelst opvalt.

**Deze paragraaf gaat over hoe een kaart eruitziet, niet over of er kaarten moeten zijn.** Geen
van de vijf maatstaven heeft één containervulling: wat daar gevuld is, draagt inhoud — een staaf,
een kolom, een stroom, een vierkantje. Lees dit dus als de regel die geldt zódra de vorm om een
container vraagt, en niet als een uitnodiging om er een te bedenken.

## 8. Uitlijning is de goedkoopste kwaliteit die er is

**Naast elkaar betekent bovenaan uitgelijnd.** Staat een blok alleen, dan mag je het verticaal
centreren. Staat het in een rij, dan is de bovenkant vast.

**Een label of getal in een rij staat op één baseline, en dat regel je met een eigen vak.** Dit
is de fout die op elke render terugkomt. In een vroege kolommenversie stonden de vier getallen eerst als derde
alinea in hetzelfde blok als de toelichting. Twee toelichtingen waren twee regels en twee waren
drie, dus de getallen zakten per kolom mee: **15,7pt verschil tussen twee kolommen die naast
elkaar staan.** De reparatie is het getal in een eigen blok op een vaste y, en dat is de enige
manier die werkt.

**Eén linkerrand.** Alles wat onder elkaar staat begint op dezelfde x, en dan reken je de inset
mee en niet alleen de vormrand. In PowerPoint heeft een vak met vulling insets van 0,2 en een
vak zonder vulling 0 — zet dat laatste dus op `x + 0,2`, anders hangt de eerste letter over de
rand van de kaart waar hij in staat. In `m5` viel het euroteken daardoor buiten de kaart.

**Draagt afstand informatie, dan staat hij op schaal.** Een staaflengte is `aandeel × breedte`.
Een moment op een tijdlijn staat op `breedte × (t − t0) / (t1 − t0)`. Botsen twee labels, dan
wijken de teksten uit naar twee rijen, nooit de posities. Vier banden onder elkaar zijn geen
tijdlijn.

## 9. Direct labelen, geen legenda

Een legenda dwingt de lezer heen en weer te kijken tussen kleur en betekenis. In een visual die
los in een document staat is dat het verschil tussen wel en niet gelezen worden.

Elke staaf, elke kolom en elk segment draagt zijn eigen naam en zijn eigen getal, op of naast de
vorm. Past dat niet, dan zijn er te veel categorieën en is het een tabel of een native grafiek.

Getalopmaak: komma voor decimalen, punt voor duizenden, euroteken met een spatie, en de eenheid
in dezelfde run als het getal — `€ 1,04 mln`, niet `1,04` met `mln` in de toelichting.

## 10. Een cijfer draagt zijn herkomst mee

Eén regel van 11pt Lato Light in navy op 70 procent, zonder vulling, direct onder de doos waar
hij bij hoort en over de breedte van die doos. Twee beelden krijgen twee bronregels.

Dit is de enige chrome die een titelloze infographic wél draagt, en de reden is dat de lezer het
cijfer moet kunnen geloven ook als de infographic los van zijn bron rondgaat. Eenheid en
peildatum staan daar, en dus niet in de grafiek.

Zegt de gebruiker dat de container de bron al draagt, dan laat je hem weg. Dat is de enige
uitzondering en je noemt hem bij de oplevering.

## 11. Vorm volgt de inhoud, en de vorm kies je uit een woordenboek

Stel eerst de vraag die de infographic beantwoordt, dan volgt de vorm eruit. De zwakste stap in
het maken van een infographic is niet de opmaak maar deze keuze, en die valt bijna altijd op de
vorm die je het laatst hebt gezien.

**Daarom is er `assets/infographic/vormen/vormenwoordenboek.png`: zesenveertig vormen, structureel, zonder
kleur en zonder opmaak, geordend naar de vraag die ze beantwoorden**, met `reference/infographic-vormkeuze.md`
ernaast dat per vorm zegt wat hij aan gegevens eist, hoeveel erin past en welk canvas hij wil. Kijk daar eerst naar. Je kunt er
niets uit kopiëren — dat is de bedoeling — je kunt er alleen mee kiezen. De indeling volgt de
negen categorieën van de Visual Vocabulary van de Financial Times (afwijking, correlatie,
rangschikking, verdeling, verandering over tijd, deel van geheel, grootte, ruimte, stroom); de
tekeningen zijn opnieuw gemaakt voor deze skill, want de FT-poster is auteursrechtelijk
beschermd en zit hier dus niet in.

Dit blijft geen patroonbibliotheek. Het woordenboek zegt wélke vorm, niet hoe hij eruitziet: de
compositie, de kleur, de maten en de afsluiting zijn elke keer opnieuw jouw beslissing.

**En er staat één vorm níet in: de kaartenrij.** In vijfenveertig van de zesenveertig bepaalt
een meting een maat — de x van een moment is zijn datum, de lengte van een staaf is zijn waarde,
de dikte van een stroom is zijn aandeel, het aantal stippen is het aantal mensen. Verandert het
getal, dan verandert de tekening. In een rij dozen verandert er niets: die ordent tekst, en dat
is een legitieme plattegrond maar geen antwoord op hoeveel, wanneer of waarheen.

De toets is één vraag aan je eigen beeld: **welk getal zou deze tekening veranderen?** Kun je er
geen noemen, dan heb je geen vorm gekozen maar een lijst opgemaakt. Dat mag, mits je het weet en
het zegt. Wat niet mag is erin rollen: de kaartenrij is goedkoper te tekenen dan elke figuur,
past op elk canvas en eist niets van je gegevens, dus hij wint elke keuze die je niet expliciet
maakt. `reference/infographic-vormkeuze.md` zet daar drie grendels op.

De tabel hieronder is de snelle vertaling van vraag naar vorm. Hij is een snelweg en geen hek:
de echte keuze maak je met de vormtoets in `vormkeuze.md`, waar elke kandidaat langs vier
controles gaat voordat er iets gebouwd wordt.

| de inhoud vraagt | dan is het | en niet |
|---|---|---|
| in welke stappen, in welke volgorde | een schema met richting | een bulletlijst |
| hoe verhoudt dit zich tot dat | een verdeling op schaal, of een gepaarde staaf | een rij tekstvakken |
| wie doet wat, wie draagt wat | rollen naast elkaar, één per kolom of rij | een organogram |
| wie hangt aan wie, en wat staat erbuiten | een naaf | een rij kaarten |
| waar gaat het geld naartoe | een sankey | pijlen tussen dozen |
| hoe loopt dit over tijd | een tijdlijn op schaal, of een native grafiek | vier gelijke banden |
| wat liep wanneer en hoe lang | een Priestley-tijdlijn | een lijst met data |
| hoeveel is het | één drager met zijn eenheid en bron | drie getallen naast elkaar |
| wat kost het en wat levert het op | twee hues tegenover elkaar | één lijst met plussen en minnen |
| wie ging vooruit en wie achteruit | een helling | twee kolommen getallen |
| hoeveel van de honderd | een rasterplot | een percentage in tekst |
| een reeks over tijd, of meer dan zes categorieën | een native grafiek | handgetekende staafjes |
| drie perioden of meer maal twee grootheden of meer | een tabel | proza |

**De laatste twee rijen kunnen allebei vuren, en dan is er een voorrangsregel:** gaat het om het
verloop, dan wint de grafiek; moet de lezer exacte waarden kunnen aflezen of vergelijken over
rijen én kolommen, dan wint de tabel. Bij twijfel allebei — grafiek boven, tabel eronder.

**En een vorm uit dit woordenboek verslaat een regel uit deze tabel.** Vraagt de opdracht om een
naaf terwijl de rij "wie doet wat" naar kolommen stuurt, dan is de naaf goed: de tabel is een
snelweg, geen hek. Zeg alleen wélke regel je overrulet en waarom, want dat is een
ontwerpbeslissing en geen slordigheid.

**Het aantal volgt uit de inhoud.** Heb je twee items en dacht je aan drie kaarten, dan wordt het
een rij van twee. Geen derde kaart met een verzonnen regel en geen halflege kaart.

## 12. Herhaling zit in de geometrie

Maak je meer dan één infographic voor hetzelfde document, zet dan de plattegrond van elk in vier
woorden onder elkaar — "vier kolommen met kopband", "rijen met staaf", "drie rijen vol
breedte" — en tel ze. Komt één plattegrond meer dan twee keer voor, dan herontwerp je er een.
Een band van dezelfde maat met één regel erin is dezelfde vorm, of hij navy, oranje-tint of
grijs is.

En verdeel de registers: als je er drie maakt, staat er minstens één **bijna helemaal wit** —
geen enkele vulling, alleen gekleurde koppen, haarlijnen en tekst — en minstens één **echt
verzadigd**. Een set waarin alles in het middengrijs ligt, is de set die karakterloos leest.

## 13. De meting is ruim, en dat is expres

`breedte()` telt de advances uit het echte fontbestand, plus de letterspatiëring, maal een
veiligheidsmarge van 3,5 procent. Die marge dekt twee dingen die je niet kunt wegrekenen: er
wordt niet gekernd, en de renderer haalt Montserrat en Lato via Google Fonts terwijl de meting
het lokale bestand leest — dezelfde familie, niet gegarandeerd dezelfde versie. Nagemeten
verschil op een sluitregel van 537pt: 3,4 procent, oftewel een regel die volgens de meting paste
en op de render tot de canvasrand liep.

Gevolg voor jou: de meting breekt eerder af dan strikt nodig, en dat is de goede kant om fout te
zitten. Wat de meting **niet** dekt: `pad()` heeft geen doos en wordt dus nergens gecontroleerd,
en een cirkel breekt tekst af op zijn omhullende vierkant en niet op de koorde — tekst in een
naaf moet je met de hand op `2·√(r² − dy²)` zetten.

## 14. Van de stijlvragen naar getallen

De vier stijlvragen uit widget 2 zijn geen smaak maar invoer. Dit is wat elke stand concreet
betekent, zodat een keuze niet halverwege verwatert.

**Uitleggende tekst**

| stand | wat er per element op staat | body | wat je verandert |
|---|---|---|---|
| geen | een label, een getal, een eenheid | 16 | de standaard; de drager mag naar 40pt, want er is ruimte |
| één regel | label, getal, één zin van hoogstens ~95 tekens | 16 | alleen als de gebruiker erom vroeg |
| volledig | label, getal, twee tot drie regels | 14 | de blokken worden hoger, dus vaak rijen in plaats van kolommen |

Bij "geen" is het beeld niet zelfstandig leesbaar zonder iemand die het toelicht. Dat is toch de
standaard, omdat een infographic in een deck, een rapport of een mail bijna altijd tekst of een
spreker naast zich heeft, en omdat ongevraagde toelichting het beeld eerder vult dan verklaart.
Noem het wel bij de oplevering, met de vraag of er een toelichtingsstand bij moet.

**Wat kleur doet**

| stand | aantal hues | waar de hue zit | let op |
|---|---|---|---|
| één accent | navy plus één | in de letter én in één vulling | dezelfde hue betekent overal hetzelfde |
| kleur codeert | navy plus twee of drie | één per categorie, rol of fase | schrijf per hue in één woord op wat hij codeert; twee blokken die samen één werkstroom vormen krijgen nooit twee hues. Drie is het plafond en dat is gemeten: elke vierde merkkleur brengt een paar onder de vloer van 15 mee — zie §6b |
| trap binnen één hue | navy plus één accent, plus tinten | de tint codeert de plaats binnen één soort, niet de soort | alleen als "donkerder" in één woord te zeggen is; navy draagt drie stappen, royal en violet twee, de lichte hues geen — §6b |
| monochroom | alleen navy | gewicht en maat doen het werk | container navy op 0,07; hiërarchie komt uit 18pt SemiBold tegen 16pt Light, en uit de drager |

**Hoeveel vlak**

| stand | vulling | lijnwerk | drager |
|---|---|---|---|
| bijna wit | geen | haarlijnen, gekleurde koppen | tekstkleur op wit, of één getal op displaymaat |
| kaarten | container 7 tot 12 procent | 1pt in de eigen hue om elke kaart | navy of de eigen hue in de kaart |
| verzadigd | volle vlakken | nauwelijks | wit op navy of royal, navy op een lichte hue, wit op 40pt |

Maak je er meer dan één in dezelfde set, dan staat er minstens één op "bijna wit" en minstens één
op "verzadigd" (§12).

**Bronvermelding**

| stand | wat er gebeurt |
|---|---|
| in het beeld | 11pt Lato Light navy op 70 procent, onder de doos waar hij bij hoort, met eenheid en peildatum |
| container draagt hem | geen bronregel, en je noemt dat bij de oplevering — een beeld dat los gaat rondgaan verliest anders zijn herkomst |
| geen bron | dan staat er geen cijfer op dat als vaststelling leest; een aanname gaat er alleen op als expliciete aanname |

---

## Wat hier niet staat

Geen patroonnamen. Geen bibliotheek met tijdlijnen en trechters. Geen maximumaantal
tekstgroottes. Geen script dat je compositie afkeurt voordat je hem gezien hebt.

En geen belofte dat dit genoeg is. De vijf maatstaven zijn niet perfect, en
`assets/infographic/maatstaf/LEESMIJ.md` noemt per stuk wat eraan mankeert. De lat is de compositie, niet
de uitvoering.

De render blijft het enige oordeel over de vorm.
