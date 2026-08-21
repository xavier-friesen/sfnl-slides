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

Lees deze dingen, in deze volgorde, en lees ze één keer voor de hele deck en niet per slide.
**Alle paden in dit document staan vanaf de plugin-map**, dus `${CLAUDE_PLUGIN_ROOT}` — niet vanaf
de map waarin dit bestand staat en niet vanaf het project. `reference/vormentaal.md` is dus
`${CLAUDE_PLUGIN_ROOT}/reference/vormentaal.md`. Dat geldt niet alleen voor de scripts: een
bouwer die de leeslijst vanaf `skills/sfnl-slides/` probeerde te openen, vond geen van de vier
documenten en moest de repo doorzoeken voordat hij aan stap 1 kon beginnen.

1. `reference/vormentaal.md` — de maatstaf. Wat een SFNL-slide goed maakt.
2. `reference/adviesvorm.md` — de laag erboven: antwoord voorop, exhibitcraft, de
   schetsplicht en de weigerlijst. Wat een deck beslisklaar maakt.
3. `assets/proeven/LEESMIJ.md` — de kleur- en gevuldheidsproef: zes renders met de metingen
   eronder die de kleurregels van §3 en de oppervlakken van §5 onderbouwen, plus vier die er
   later bij kwamen — `07` en `08` zijn titelmodus B, `09` en `10` de icoonproef. Geen lat, wel
   het bewijs. Lees deze wanneer je besluit 2, 3 of 4 neemt, en opnieuw wanneer je een icoon
   overweegt.
4. `assets/maatstaf/*.png` — veertien voorbeelden: tien uit decks die de vergelijking hebben
   gewonnen, en vier reconstructies van slides die als de mooiste uit deze skill kwamen. Kijk
   ernaar. Ze zijn niet om na te tekenen maar om te weten waar de lat ligt.
5. `reference/sjabloon.md` — de feiten: welke layout waarvoor, welke placeholder waar, de
   kleurslots en het alpha-recept, de volgorde binnen de XML, en negen valkuilen die stil
   misgaan.
6. De docstring van `scripts/shapes.py` — de primitieven waarmee je tekent, en waarom die er zo
   uitzien.

Draai daarna `python "${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py"` — alle scriptpaden in
deze skill zijn relatief aan de plugin-map, dus aan `${CLAUDE_PLUGIN_ROOT}`, niet aan het
project. Preflight zegt of er een interpreter, de Python-afhankelijkheden, een renderer en
de huisstijlfonts zijn. Is er geen renderer, lees dan
eerst **Zonder renderer** onderaan; dat verandert hoe je bouwt en wat je bij oplevering zegt.

`reference/voice.md` gaat over de taal op de slide. Lees dat wanneer je de outline schrijft.

Daarna is het vragenvuur van stap 1 het eerste wat je doet, en dat is een poort: zonder die acht
antwoorden schrijf je niets.

## Stap 1 — Het vragenvuur, en dit is de eerste poort

Acht vragen in één blok: vier over de opdracht, vier over de vorm. **Leg ze in één keer voor en
wacht op de antwoorden.** Er wordt niets geschreven voordat ze er zijn — geen storyline, geen
outline, geen slide. Dat is een poort en het was er geen: de skill had de vormbesluiten bij de
outline hangen, en dan lag er al tekst wanneer de gebruiker voor het eerst iets kon kiezen. Wie
de tekst eerst schrijft, kiest de vorm al.

**Stuur de keuzekaart mee vóór je de vier vormvragen stelt.** Dat is
`assets/keuzekaarten/vragenvuur.png`: per besluit de opties naast elkaar als detailuitsnede uit
een echte render, met de meting eronder. Stuur het bestand, lees het niet — dan kost het geen
tokens en geen render, en ziet de gebruiker waar hij tussen kiest in plaats van drie woorden.
Stel de vragen daarna met de optienamen van de kaart, zodat het beeld en de vraag hetzelfde
heten. Verandert er een optie, dan is de kaart opnieuw te bouwen met
`python "${CLAUDE_PLUGIN_ROOT}/scripts/keuzekaart.py"` — onderhoud, geen bouwstap.

Weet je een antwoord uit de opdracht, dan vul je het in als voorstel en zet je erbij waar je het
vandaan haalt. Het staat dus nog steeds in het blok en de gebruiker bevestigt of wijzigt het.
Overslaan is geen antwoord.

**"Kies jij maar" is een geldig antwoord.** Laat de gebruiker een besluit aan de skill, dan neemt
de skill het deckbreed, één keer, met de reden erbij bovenaan de outline. Wat er daarna niet
gebeurt is het besluit per slide opnieuw nemen: dat is het gemeten defect waar de hele
vormentaal tegen duwt. Deze tabel bakent dat af, en hij geldt ook wanneer de gebruiker zelf
kiest:

| besluit | wie kiest | mag per slide verschillen |
|---|---|---|
| 1 dichtheid | gebruiker, of de skill op verzoek | alleen met expliciete toestemming |
| 2 gevuldheid | gebruiker, of de skill op verzoek | ja — de grondtoon is deckbreed, een enkele slide mag kaal of met kleur zijn |
| 3 wat kleur codeert | oranje staat vast; de tweede hue en de set zijn een gebruikerskeuze | tweede hue per slide: ja, als hij codeert. Een ánder accent: alleen met toestemming |
| 4 titelmodus | gebruiker | nooit |

**Twee dingen worden niet gevraagd, want ze zijn geen keuze van de lezer.** De vier maten zijn
een regel (`vormentaal.md` §2) met één tweesprong: de body mag naar 12pt bij een kaartenrij van
drie of meer of een tabelcel, en dat volgt uit de compositie en niet uit een voorkeur. De prijs
staat op `maatstaf/11`: vier kaarten van 2,95 in laten de oude body van 16pt niet toe, en de
reconstructie is daar op 13pt uitgekomen — een maat die §2 niet kent, en `maatstaf/LEESMIJ.md`
noemt hem dan ook als defect van die slide. Sinds de body op 14 staat is dat verschil één punt,
maar of 14 daar past is niet nagemeten. De uitweg blijft 12pt en niet een eigen tussenmaat. En de kaarttaal
kiest de skill zelf: recht of afgerond, deckbreed, met een 1pt-haarlijn in de eigen hue op elk
licht vlak dat los op wit staat. Beide varianten zijn uitgewerkt — `maatstaf/12` is recht zonder
haarlijn omdat het volle rijlabel de rij al begrenst, `maatstaf/11` is afgerond met haarlijn — en
kies je afgerond, dan één absolute radius deckbreed (0,08 tot 0,12 in), want een `roundRect`
zonder expliciete `adj` levert nagemeten vier verschillende radii in één deck (`vormentaal.md`
§8). Zet de gekozen kaarttaal wél bovenaan de outline: hij is deckbreed en halverwege wisselen is
het defect dat het snelst opvalt.

### De vier over de opdracht

- **Wie leest dit, en wat moet die erna kunnen besluiten?** Dit bepaalt alles. Een deck voor
  een wethouder die moet besluiten is een ander deck dan een deck voor een projectgroep die
  moet meedenken. Vraag hierbij ook of er straks iemand bij praat én of het deck daarna wordt
  nagestuurd — die twee antwoorden samen zijn besluit 1. Het is geen vijfde vraag maar de
  tweede helft van deze.
- **Hoeveel slides, ongeveer?**
- **Heb je een deck of een document dat als voorbeeld dient?** Vraag dit actief. Krijg je er
  een, dan is dát de maatstaf: render het, kijk ernaar, en volg de vormentaal ervan in plaats
  van `assets/maatstaf/`.
- **Zijn er eigen foto's, cijfers of bronnen?**

### De vier over de vorm

Elk besluit heeft een default, een referentie waar de uitkomst te zíen is (de keuzekaart, en het
bestand eronder), en een uitkomst die je erbij koopt. Volg je de default, dan hoef je niets te
motiveren; wijk je af, dan staat de reden erbij — zo is afwijken een keuze en geen bijproduct van
hoeveel tekst er toevallig in de outline stond.

De volgorde loopt van grof naar fijn en is niet willekeurig. De dichtheid bepaalt de tekstlast van
elke slide, de gevuldheid bepaalt daarbinnen hoeveel kleur er staat, kleur codeert daarbinnen wat
er onderscheiden wordt, en de titelmodus is de enige die alleen de titelrij raakt. Een besluit
verderop kan nooit een besluit eerder in de rij terugdraaien.

1. **De dichtheid: spreekdeck, licht leave-behind of leave-behind.** Eén vraag beslist hem:
   praat er iemand bij, en gaat het deck daarna de mail in?

   | situatie | dichtheid | indicatie | referentie |
   |---|---|---|---|
   | iemand praat, het deck gaat niet mee | spreekdeck | 50 tot 60 woorden per slide | `maatstaf/13`, `14` |
   | iemand praat én het deck gaat mee | licht leave-behind | 90 tot 110 | `maatstaf/12` |
   | geen spreker, het deck staat alleen | leave-behind | 120 tot 145 | `maatstaf/11`, `04` |

   **De getallen zijn een indicatie en werken twee kanten op.** Ze zeggen welk register je hebt
   gekozen, niet hoeveel woorden er op de slide moeten. Past het verhaal in minder, dan is het
   minder — een slide die op 40 woorden staat terwijl de band 90 tot 110 zegt is geen dunne
   slide maar een slide die klaar is. En vraagt het verhaal meer, dan is het meer: een bewering
   schrappen om onder een richtwaarde te blijven is de verkeerde reductie, want dan levert de
   telling het argument in. De twee verkeerde bewegingen zijn dus opvullen tot de band gehaald
   is, en snijden tot de band gehaald is. `qa_tellingen.py` telt de woorden daarom zonder
   oordeel en er staat geen drempel op. De toets die wél geldt is die van `vormentaal.md` §13:
   staat hier tekst waar een vorm had gemoeten?

   Default: **licht leave-behind**, want dat is de gewone SFNL-situatie — er wordt bij gepraat en
   het deck wordt nagestuurd. Dit register is er bijgekomen omdat de meting het aanwees: het
   gemeten spreekdeck zat op gemiddeld 85 woorden met een piek van 101, te dicht voor een
   spreekdeck en te dun voor een leave-behind. Het was geen mislukt spreekdeck maar een register
   zonder naam.

   De uitkomst per keuze, want daar is dit besluit op te beoordelen. Op een **spreekdeck** hoort
   wat de spreker zegt níét op de slide, en het gaat ook nergens anders in het bestand staan:
   het blijft bij de spreker. Lees je zo'n deck later zonder hem terug, dan mist er iets, en dat
   is de bedoeling — precies daarom is dit de dichtheid die je alleen kiest als het deck niet
   wordt nagestuurd. Op een **leave-behind** mag een slide dicht zijn: een prozaslide met twee
   goed gezette kolommen is daar een volwaardige exhibit (`maatstaf/04`), en 141 woorden is geen
   defect. **Licht leave-behind** zit ertussen: leesbaar zonder spreker, één boodschap per slide,
   geen uitgeschreven spreektekst.

   En dichtheid is geen telegramstijl: `sfnl-humanizer` verbiedt de vorm "Kosten: hoger.
   Doorlooptijd: onveranderd", dus elke regel blijft een leesbare zin of een label met een getal.
   Die twee regels duwen tegen elkaar en de eerste bouwer die dit register gebruikte moest die
   grens zelf formuleren; hier staat hij. De metingen eronder staan in `vormentaal.md` §13. Wat
   op elke dichtheid blijft staan: elk getal draagt zijn eenheid en periode op de slide zelf
   (`voice.md`).
2. **De gevuldheid: weinig accent, kaal of met kleur.** Drie waarden, elk met een gerenderde
   referentie in `assets/proeven/` en de meting eronder (aandeel wit / verzadigd):

   | gevuldheid | wat er staat | gemeten | referentie |
   |---|---|---|---|
   | **weinig accent** — default | geen kaartvullingen: navy koppen op wit, een haarlijn per rij, en één vol oranje vlak precies waar de nadruk zit | 92 / 3 | `proeven/03` |
   | **kaal** | ook dat vlak niet: haarlijnen, kapitaallabels en kleur in de letter | 94 / 1 | `proeven/01` |
   | **met kleur** | een set hues codeert de categorieën, in volle rijlabels of vier kaarten | 80 / 14 | `proeven/02` |

   Default is **weinig accent**, gekozen op de zes gerenderde varianten van dezelfde inhoud. Dit
   is de grondtoon van de deck en geen keuze per deck-en-klaar: kaal is de slide die er om vraagt
   (een vraag, proza), met kleur is de slide waar een set categorieën uit elkaar moet blijven. Ze
   mogen dus in één deck naast elkaar staan — dat is precies wat het contrast tussen de slides
   maakt.

   **Wat hier níét meer bij hoort: een vol vlak dat een kwart van de slide beslaat.** Dat is
   `proeven/04`, gemeten 25 procent verzadigd, en hij is op de render afgekeurd: het oppervlak is
   groot en draagt bijna niets, dus de vulling wordt het luidste element terwijl de boodschap vier
   woorden is. De band van 20 tot 37 procent uit `vormentaal.md` §5 blijft de meting van de
   winnende decks, maar hij is geen doel — het contrast haal je door van gevuldheid te wisselen.

   De rest van de uitkomst: één procent verzadigd is ongeveer één vierkante inch, en de schatting
   zit er structureel naast, dus meet het met `qa_tellingen.py --renders`. Let op de val dat vier
   volle rijlabels vol vóelen en 14 procent meten, en dat een slide met alléén lichte containers
   op 65 tot 69 procent wit uitkomt — dat is geen van de drie en vraagt dus een reden.
3. **Wat kleur codeert: oranje staat vast, de tweede hue is de keuze.** Oranje is het accent
   naast navy, vast en deckbreed. Dat wordt niet per deck opnieuw gekozen: het is de huiskleur en de enige hue in het
   palet die als merk leest in plaats van als categorie.

   De uitkomst die je erbij koopt, en die hoort hier expliciet te staan: oranje haalt 2,6 op wit
   (`vormentaal.md` §3). Het accent kan dus nooit een gelezen regel dragen. Een accent in de
   letter is displaymaat of een kop vanaf 18pt; alles wat werkelijk gelezen wordt blijft navy.
   Heb je een accent nodig dat ook een alinea draagt, dan is dat royal (5,7), en dat is een
   afwijking met een reden.

   **Nadruk zet je niet in de letterkleur, en dat is nagemeten.** Twee van de vier koppen
   oranje en de andere twee navy laten de navy koppen sterker lezen (15,3 tegen 2,6), dus de
   kleur wijst de verkeerde twee aan — `proeven/01`. De vorm die het oplost staat in
   `proeven/03`: alle koppen navy, en het element met nadruk draagt een volle oranje chip met
   navy tekst. Kleur in de letter is dus voor codering waarin élk lid van de set een hue krijgt;
   blijft een deel navy, dan hoort de nadruk in een vlak.

   Wat hier wél gekozen wordt, is wat kleur codeert. Per slide mag er één tweede hue bij als die
   iets onderscheidt dat de lezer apart moet houden — twee kanten van een afweging
   (`maatstaf/04`), kost tegenover baat, nu tegenover straks. Schrijf per hue in één woord op wat
   hij betekent: grapefruit is kost of waarschuwing, emerald is baat, navy is structuur, sky en
   royal zijn vrij. Vraagt de deck een **sét** van drie of vier hues — vier fasen, vier
   tabelrijen, vier categorieën die terugkomen — dan is dat één deckbreed besluit dat je hier
   neemt en niet per slide (`maatstaf/11`, `12` zijn beide zo'n set). Daarna beslis je er niet
   meer over. Twee categorieën in dezelfde set krijgen nooit dezelfde hue, en twee blokken die
   samen één werkstroom vormen krijgen nooit twee verschillende.
4. **De titelmodus** (`voice.md`, Titels). Modus A is de default: de titel is een volle zin die
   de boodschap draagt, en er komt géén subtitel — idx 1 blijft leeg. Modus B kies je alleen
   wanneer de deck echte hoofdstukken heeft die de lezer moet kunnen terugvinden: dan is de
   titel de hoofdstuknaam, blijft hij binnen dat hoofdstuk letterlijk gelijk, hoort er bij elk
   hoofdstuk een divider, en draagt de subtitel de leidende zin van de slide. De subtitel is
   dus vooral een modus-B-instrument. Bij twijfel modus A, en schrijf op waarom.

   **Daaruit volgt een ondergrens, want de divider is niet optioneel in deze modus.** Dividers
   mogen pas vanaf vijf contentslides (zie Dividers, hieronder), dus onder vijf bestaat modus B
   niet: daar is het modus A. Dat is geen formaliteit — modus B is er om hoofdstukken
   terugvindbaar te maken, en in een deck van vier slides is er niets terug te vinden.

   Modus B is gebouwd, dus je kunt hem laten zien: `proeven/08` is de contentslide met de
   hoofdstuknaam als titel en de bewering in de subtitel, en `proeven/07` is de divider die
   ervoor hoort. Let op wát de subtitel kost, want het is niet ruimte: hij staat in de geërfde
   header (`0.48, 1.04 · 12.52 × 0.63`, boven de dash op 1,72) en de contentzone begint in beide
   modi op 1,93. Wat hij kost is hiërarchie — 14pt Montserrat Light onder een titel van 24pt
   Gotham Bold is het lichtste element van de slide, dus de bewering die daar staat moet in de
   contentzone een drager krijgen (`voice.md`, In modus B draagt de contentzone de boodschap
   mee).

   Dit besluit varieert nooit per slide en wordt ook nooit per slide aan de skill gelaten: de
   modus is precies de afspraak die de titelrij van de hele deck leesbaar houdt. Half A en half B
   levert een deck waarin de lezer niet weet of een titel een bewering of een hoofdstuk is.

**Wat je na dit blok hebt** is een vormbesluit per rij, en dat gaat als eerste blok bovenaan de
outline mee: per besluit de gekozen waarde, en alleen bij een afwijking van de default de reden.
Vier regels van de gebruiker, plus de kaarttaal en een eventuele afwijkende bodymaat die de skill
zelf nam — zes regels die in één keer te herlezen zijn.

## Stap 2 — Outline, en de tweede poort

De besluiten uit stap 1 staan bovenaan `outline.md` en gelden voor elke slide. Neem je ze daar
niet over, dan neem je ze per slide opnieuw en dan verspringt de deck zonder dat iemand kan zien
waarom.


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
  Schrijf je er een, dan geldt het budget uit `voice.md`: één zin, hooguit twee regels. De
  toets: kun je de subregel vervangen door "hieronder staat het", dan schrap je hem. Twee of
  drie subtitels in een deck van twaalf slides is dus normaal en twaalf is een signaal dat de
  titels hun werk niet doen (`voice.md`, Titels). Een ontbrekende subtitel is nooit een
  bevinding — niet in de QA en niet in een review.
- **Layout** — met het nummer, en kies niet standaard 19. Een tweeluik is 22, waar de
  kolomkoppen geërfde placeholders zijn: die geven je de doos en de zetting, maar `set_text.py`
  kent geen kleur, dus wil je de kop in de hue van zijn kolom, dan laat je de placeholder leeg
  en zet je hem zelf met `label()` in dezelfde doos. Doorlopende tekst is 20. Een
  schema over de volle hoogte zonder titel is 17. Vier contentslides op 19 achter elkaar is de
  eenvormigheid waarop de vergelijking verloren is.
- **Boodschap** — in één zin: wat moet de lezer hiervan overhouden.
- **Drager** — welk element de boodschap draagt, gekozen uit vier: een getal, de compositie
  zelf, een kop of kernbegrip in de hue van zijn categorie, of een sluitregel. Een slide zonder
  drager gaat niet naar de bouwstap. Wijs hier ook aan welke slides de dragermaat van 28 tot
  40pt krijgen; de grens van één op drie staat in `vormentaal.md` §1, en het zijn de slides waar de
  boodschap werkelijk een getal of een verhouding is.
- **Plattegrond in vier woorden** — "drie kaarten, open onderkant", "tabel plus conclusie",
  "vier rijen". Zet ze onder elkaar en tel ze: komt één plattegrond meer dan twee keer voor, of
  staan er twee gelijke naast elkaar, dan herschik je hier. Na het bouwen kost dat een herbouw
  van de contentzone.
- **Vorm die de inhoud vraagt — het beeldbesluit.** Dit veld was één woord en is nu één
  regel, geschreven vóór de tekst: eerst het woord (getal, grafiek, tabel, proces, verdeling,
  proza), dan wat beeld wordt, wat tekst blijft, en **waarom het niet visueler kon**. Die
  laatste helft is het werk, en de reden gaat over de inhoud — zoals de keuzeregel bij de
  schets (`adviesvorm.md` §3). "De fasen zijn even lang, dus een as zou een verschil
  suggereren dat er niet is" is een reden; "n.v.t." en "past niet" zijn dat niet, want een
  reden die op elke slide past beslist niets. Proza is een volwaardig antwoord
  (`maatstaf/04`), mits de reden zegt waarom er in de boodschap geen verhouding, tijdstip of
  afstand zit (`vormentaal.md` §12). En een **icoon** is hier een middel en geen opsmuk: je
  tekent het zelf met `icoon()` op het 24-raster (`vormentaal.md` §14, `proeven/09`), er is geen
  bibliotheek, en het mag alleen mee als het een soort codeert die de lezer moet vergelijken,
  iets markeert dat over meerdere slides terugkomt, of een zin in een schema vervangt. Naast een
  kop die het al zegt is het decoratie — `proeven/10` zet dezelfde drie rijen met en zonder
  iconen naast elkaar, en zonder is de rustigere. En één toets hoort er standaard bij: staat op elke kolom
  dezelfde vetgezette aanhef, dan zijn die labels een rijkop en is het antwoord tabel — de
  gemeten slide van 255 woorden was precies dat, vier kaarten met acht keer dezelfde twee
  labels (`vormentaal.md` §13). Vraagt de brief "hoe werkt het" of "in welke stappen", dan is
  het geen lijst; draagt de deck cijfers, dan zit er minstens één grafiek, tabel, schema of
  verdeling in.
- **Tekst** — letterlijk zoals hij op de slide komt, inclusief cijfers, eenheid en bron.
- **Herkomst** — achter elke inhoudelijke regel `[brief]`, `[dossier]` of `[aanname]`. Een
  aanname mag nooit als vaststelling op de slide; die gaat er alleen op als open vraag of als
  expliciete aanname. Zet alle aannames als lijstje onder de outline.

**Wat je niet in de outline zet: maten.** Geen inches, geen kolombreedtes, geen kaartindeling,
geen patroonnaam. De plattegrond, de drager en het beeldbesluit horen er wél in — dat is de
reden waarom de tekst deze lengte heeft, en het is het enige stuk vorm dat vóór het bouwen te
beoordelen is. De uitvoering ontdek je op de render.

**Wat een contentslide is.** Elke slide die niet de cover, een divider of de outro is. De
dividerregel hieronder en het bandbudget uit `vormentaal.md` §10 hangen er beide aan, en
`qa_tellingen.py` telt zo — een deck van 23 slides met een cover, vier dividers en een outro
heeft dus 17 contentslides. Wie de dividers meetelt houdt vier slides meer over en dus een hele
band meer budget, en dat is precies waar de telling en de bouwer een keer uit elkaar liepen.

**Dividers.** Vanaf twee inhoudelijke hoofdstukken én zeven contentslides zijn sectiedividers
verplicht, één per hoofdstuk, uit de fotolayouts 6 t/m 16. Bij vijf of zes contentslides met
duidelijke blokken mag het. Onder vijf niet, en dus bestaat titelmodus B daar ook niet
(besluit 4). Nooit twee achter elkaar en nooit als laatste
slide. Een foto mag het onderwerp niet tegenspreken; past er voor geen enkel hoofdstuk een
passende foto, kies dan één neutrale voor allemaal — consistentie boven variatie.

**De uitspraakslide, als de deck er een heeft.** Eén vraag of één bewering, gecentreerd op een
vol vlak over de hele slide, verder niets: geen titel, geen kaart, geen toelichting. Dat is de
enige plek waar een groot vol vlak los van de gevuldheidsregel staat, want er staat niets naast
dat de aandacht moet delen (`vormentaal.md` §5). Bouw hem op layout 17 met één `drager()` — niet
op layout 5, dat is het citaat over een foto met de oranje band eronder. Eén per deck, en alleen
voor de vraag waar het werkelijk om gaat.

**Cover en slot.** Slide 1 is layout 1, het 2×2 kleurraster met de foto en de witte logokaart.
Past de dektitel niet op de layoutmaat (`7.63, 5.79 · 5.33 × 0.56`, één regel), dan groei je dat
vak zelf naar boven — daar is ruimte, en onder het vak zit de klant-en-datumregel al. `fit_title.py`
doet dat niet voor je: dat script raakt alleen de contentlayouts 19 t/m 22. Kies dus ook niet
layout 4 omdat de titel niet past, want dat levert de vlakkere cover op. Nooit de organisatienaam als kop. De
klant-en-datumregel (idx 13) vul je als lijst van twee: de klant op regel één, de datum op
regel twee — als één regel breekt hij op de smalle placeholdermaat midden in de datum. Een
extern deck eindigt op layout 2 of 3, de oranje outro zonder tekstplaceholders. Een intern deck
eindigt op de beslis- of adviesslide.

Laat `sfnl-humanizer` over de teksten gaan vóórdat je de outline voorlegt. Tekst die ná de bouw
verandert, betekent slides opnieuw bouwen.

**Leg de outline dan voor en wacht op goedkeuring.** Dit is de tweede en laatste poort, en de
eerste stond in stap 1. Ga
niet bouwen omdat de outline "duidelijk genoeg" lijkt.

## Stap 3 — Bouwen

Zes stappen. Alle paden hieronder zijn relatief aan de plugin-map; `$S` is `${CLAUDE_PLUGIN_ROOT}/scripts`
en `<plugin>` hieronder is `${CLAUDE_PLUGIN_ROOT}` zelf — dezelfde map, drie schrijfwijzen,
en er is er maar één.

**Windows: houd de builddir kort.** De uitgepakte boom gaat 53 tekens diep, dus werk in
`C:/w/<naam>` en zet het eindbestand daarna op zijn plek. `prepare_template.py` rekent dit
vooraf na en zegt het als het niet past.

**Zet de bouw meteen in één herbouwbaar script, niet in losse aanroepen.** Eerste regel van dat
script gooit de builddir weg en begint bij `prepare_template.py`; daarna alle slides. Dit is
stap één en niet stap drie, want `write()` uit `shapes.py` voegt vormen tóe vóór `</p:spTree>`
en `add_slide.py` hangt een slide achteraan: een tweede run op een bestaande builddir verdubbelt
alles wat er al staat. Nagemeten gevolg: een deck waarvan de bouw pas na de eerste visuele ronde
herbouwbaar werd gemaakt, en dat tot die tijd niet opnieuw gebouwd kón worden zonder de map met
de hand op te ruimen. De visuele loop in stap 4 is per definitie meerdere ronden, dus je hébt
een script dat je onbeperkt kunt herhalen — anders repareer je met de hand in XML wat je had
kunnen herbouwen.

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

**Een beeld, een haak en een sectiekop.** Drie dingen die er sinds de oogst uit elf bestaande
decks bij zijn gekomen, en die je anders zelf gaat namaken:

- `foto(slide, naam, x, y, w, h, bestand, prst="ellipse")` zet een afbeelding in een vorm — een
  rond portret op een teamslide, een partnerlogo op een cover, een verkleind eindproduct als
  artefact. Hij regelt zelf de media, de relationship, het content-type en de uitsnede, en een
  tweede aanroep met hetzelfde bestand hergebruikt het bestaande beeld. Dat laatste is de reden
  dat je hem gebruikt in plaats van het plaatje ná de bouw in PowerPoint erin te slepen: zo
  blijft de deck herbouwbaar.
- `accolade(naam, x, y, w, h, hue, punt_y=...)` knoopt een groep vormen aan één uitkomst. Geef
  `punt_y` de y van het midden van de doelvorm, dan wijst de haak daar werkelijk naartoe in
  plaats van naar zijn eigen midden. Dit is het merkteken dat een schema met dertig blokken
  leesbaar houdt; vier pijlen doen hetzelfde werk luider.
- Een sectiekop in een tabel is `{"sectie": "FASE 1"}` tussen de rijen in `add_table.py`. Die
  rij pakt de volle breedte en draagt een volle vulling, en scheidt twee delen van dezelfde
  tabel zonder een tweede kop.

`reference/merktekens.md` heeft er nog zevenentwintig, met per stuk wat het codeert en of de laag
het al kan. Lees dat wanneer je merkt dat je een kaart met tekst aan het maken bent.

**Gebruik `scripts/shapes.py`.** Dat is de primitievenlaag: vlakken, lijnen, tekstruns,
kolomrasters, een hoogtemeting, een handvol merktekens die élk één ding tekenen (punt, meter,
pijl, streep) en het gereedschap om een eigen vorm te maken (`adj`, `contour`, `verbind`,
`schaal`). Het is géén patroonbibliotheek; er zit geen kaartenrij en geen stroomschema in. Wat
je ermee bouwt is elke slide opnieuw jouw beslissing.

Waarom je hem gebruikt in plaats van zelf XML te typen: de eerste deck die met deze skill werd
gebouwd had een ad-hoc bouwlaag die `<a:ln><a:noFill/>` op elke vorm hardcodeerde en zijn lichte
vullingen met `lumMod` maakte. Daarmee waren de twee mooiste referentieslides — witte kolommen
met een haarlijn in de eigen hue, en een verzadigde kop boven een nauwelijks getint paneel —
structureel onbouwbaar, en de bouwer merkte dat niet.

```python
import sys; sys.path.insert(0, "<plugin>/scripts")
from shapes import (ZONE, Deck, aanhef, binnen, cols, contour, drager, gat_onder,
                    hoogte_van, label, meter, para, pijl, punt, run, schaal, streep,
                    tekst, tekst_op, verbind, vlak, vulgraad, write)

D = Deck(body=14, kop=18, label=14, display=32)       # de vier maten, één keer
xs, w = cols(3, 0.24)                                 # raster
h = hoogte_van([(kop, D.kop, "Montserrat SemiBold"),  # hoe hoog moet dit blok zijn
                (txt, D.body, "Lato Light")], w)
vormen = [
    vlak("Kop 62", xs[0], ZONE["y"], w, 1.35, vulling="emerald",
         tekst=[para(drager("62", D.display,           # Montserrat Light, nooit Gotham
                            tekst_op("emerald", D.display)), algn="ctr")], anchor="ctr"),
    vlak("Kaart A", xs[0], 3.28, w, h, vulling="container:emerald", lijn=("emerald", 1),
         tekst=[para(label(kop)), para(run(txt, "Lato Light", D.body), spc_voor=600)]),
    tekst("Regel", xs[1], 3.28, w, 0.9,
          [para(*aanhef("Twee loketten.",                # Lato Semibold + Lato Light
                        "De doorlooptijd blijft op 41 dagen steken.", D.body))]),
    punt("Badge 1", xs[2], 3.28, 0.50, "emerald", tekst="1"),   # merkteken, geen XML
    vlak("Halve punt", xs[2] + 0.7, 3.28, 0.16, 0.16,           # élke preset via adj
         prst="pie", vulling="emerald", adj={"adj1": 5400000, "adj2": 16200000}),
]
write("unpacked/ppt/slides/slide3.xml", vormen)
```

**Een eigen vorm, in drie wegen.** Dit is waar de laag het meest oplevert, want een ontbrekend
merkteken is een slide die tekst blijft.

1. **Een presetvorm met zijn handvatten** — `vlak(prst=..., adj=...)`. `prst` is elke
   PowerPoint-presetvorm; `adj` zet zijn `adj1`/`adj2`. De tabel `PRESET_ADJ` in `shapes.py`
   zegt per vorm wat die waarden doen: een halve punt is `pie` met `adj1=5400000, adj2=16200000`,
   een dunne ring is `donut` met `adj=12500`, een stap in een volgorde is `chevron` met
   `adj=25000`. Zonder `adj` krijg je PowerPoints defaults, en die zijn op deze maten fout — een
   `pie` wordt een pacman en een pijl van 0,24 in hoog een driehoekje.
2. **Een merkteken** — `punt()` (met een gecentreerd cijfer, of half gevuld), `meter()` (een rij
   punten die een grofheid codeert), `pijl()` (met een kop die niet de helft van de hoogte is),
   `streep()` (horizontaal én verticaal, met alpha voor een haarlijn), `verbind()` met `anker()`
   (twee vormen op hun rand verbinden). Elk tekent één ding en houdt zich aan de kleurregels.
   En `icoon()`, dat een zelfgetekend lijnicoon op een raster van 24 zet: je geeft de geometrie
   in rastereenheden, de functie geeft de dikte, de hue, de ronde uiteinden en de groep
   (`vormentaal.md` §14). Er is geen iconenbibliotheek en die komt er niet.
3. **Een eigen contour** — `contour("Wig", 0, 0, [(0.48, 4.2), (2.0, 3.6), (2.0, 4.8)],
   vulling=("grapefruit", 20000))`. Punten in inch, en de laag schrijft het `custGeom`. Met
   `sluit=False` en een `lijn` is het een open lijnstuk: een accolade, een knik.

**Draagt afstand informatie, dan staat hij op schaal.** `px = schaal(ZONE["x"], ZONE["w"], 2024,
2028)` geeft een functie die een waarde naar een x in inch omzet — de formule uit
`vormentaal.md` §7. Dat is het enige rekenwerk waar het oog de fout niet kan repareren: een punt
op de verkeerde plek ziet er precies zo goed uit als een punt dat goed staat. Het label bij een
tik houd je binnen de zone met `binnen()`; het punt zelf verschuift nooit.

Nog steeds géén patroonbibliotheek: er is geen `kaartenrij()`, geen `stroomschema()` en geen
`tijdlijn()`. De merktekens tekenen één ding, de compositie is elke slide opnieuw jouw
beslissing.

Wat er extra nee zegt zodra je een eigen vorm maakt: `"grijs"` als vulling of als kaartlijn (dat
is de Word-tabellook — een lichte vulling is alpha op de volle kleur), `hoek` en `adj` samen, een
`adj`-handvat dat de preset niet heeft, een `label()` met een alphakleur (die mist in de render
zijn laatste letter — gebruik de kleur `"grijs"`), een cursieve run die langer is dan één korte
regel, en een meter van meer dan vijf punten.

Wat de laag voor je regelt: alpha in plaats van `lumMod`, de `adj` van een `roundRect` uit een
absolute radius, een lijn in dezelfde hue als de vulling, de expliciete `<a:latin/>` op elke run,
`noAutofit`, de juiste elementvolgorde, `lnSpc` op 112 procent, en de tekstkleur die bij een
vulling en een puntgrootte hoort. `Deck(display=...)` weigert een drager buiten 28 tot 40pt, en
`run()` weigert Gotham Bold: die letter staat in de titel en komt uit de layout.

`Deck(display=...)`, `run()` en `para()` zijn de drie plekken waar de laag nee zegt: een drager
buiten 28 tot 40pt, Gotham Bold in de contentzone, en een alinea met een Montserrat- én een
Lato-run. Die laatste is de regel 'één familie per regel': is het een kop of een label, zet het
dan op zijn eigen regel met `label()`; is het een aanhef binnen de regel, gebruik `aanhef()`.

`hoogte_van` en `vulgraad` zijn er om de val uit `vormentaal.md` §6 te vermijden: eerst meten hoe
hoog de inhoud is, dan pas beslissen hoe je de restruimte verdeelt. Ruimte tussen de blokken is
compositie, ruimte ónderin een blok is een gat.

**De norm voor `vulgraad` is 0,9, en `gat_onder` blijft onder 0,25 in.** Die twee samen, want
een verhouding is schaalblind. De meting rekent strakker dan de renderer zet, dus een blok dat
0,78 meet staat op de render mét een gat — dat is nagemeten en het is de reden dat de drempel
hier hoog ligt. Haalt een blok de norm niet, dan is het antwoord meer inhoud, grotere letters,
een andere compositie, of het blok inkorten en de slide met een ander element afsluiten. Nooit
een hoger blok, en nooit het getal als bewijs: ook boven 0,9 kijk je naar de render.

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
python $S/fit_title.py unpacked --mode a          # of --mode b, naar besluit 4
python $S/clean.py unpacked
python $S/office/pack.py unpacked deck.pptx --original <plugin>/assets/sfnl-sjabloon.potx
```

`fit_title.py` meet de titels met het echte Gotham Bold en laat de titelbox omlaag groeien waar
hij twee regels nodig heeft — de bovenkant blijft staan, de onderkant zakt de subtitelband in, en
dat gebeurt uitsluitend op de contentlayouts 19 t/m 22, en toetst de titelmodus die je in besluit 4 koos: titels in
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

`--type radar` en `radar_markers` zijn er voor één geval: een profiel over vaste assen, waar de
vórm van het web de boodschap is. Het meetplan Welzijn op Recept doet dat met de zes assen van
positieve gezondheid, voor en na. Voor een reeks over tijd of een vergelijking van categorieën is
een radar de verkeerde keuze — die suggereert een samenhang tussen de assen die er niet is.

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

Kijk eerst zelf naar het contactblad — de render is je enige vormbeoordeling, dus die kijk je
niet uit. Open op volle grootte alleen wat er verkeerd uitziet. Zet daarna de
`deck-visual-reviewer` op diezelfde renders, met het pad erbij zodat hij niet opnieuw rendert; die kijkt met een frisse blik naar overloop,
overlap, uitlijning, halflege zones, kleur die niets zegt, en eenvormigheid over de deck.

**Render naar een pad waar de reviewer bij kan, en controleer dat vóór je hem stuurt.** Een
subagent leest alleen binnen de aangesloten mappen; renders die in een sandbox- of tempmap van de
shell staan, zijn voor hem onzichtbaar. Nagemeten gevolg: een reviewer die geen enkele slide kon
openen, in plaats daarvan de bouwcode las, en een ronde kostte waarna de visuele beoordeling
alsnog met de hand moest. Zet de PNG's dus in de projectmap, noem dat pad expliciet in de
opdracht, en laat hem beginnen met de bevestiging dat hij het contactblad ziet. Zegt hij dat hij
geen beeld heeft, dan is de uitkomst geen visuele review — hoe bruikbaar zijn structurele
opmerkingen ook zijn.

Repareer alle bevindingen van een ronde in één keer en render opnieuw met een nieuw prefix
(`raster-2`). Doorgaan tot er niets meer te melden is.

Wat je in de eerste ronde zelf al gaat zien, en wat geen regel voor je oplost:

- Een label dat over twee regels loopt terwijl de andere labels dat niet doen. Dan staan de
  getallen eronder niet meer op één lijn, en dat leest als slordig. Kort het label in, of geef
  de labels een eigen vorm met een vaste hoogte zodat de getallen wel uitlijnen.
- Tekst die net buiten zijn vak valt. Het vak wordt kleiner of de tekst korter, niet het
  lettertype.
- Een compositie die op 4,5 in ophoudt. Maak de elementen groter, niet het gat.
- Een blok met lucht onderin, ook als `vulgraad` een net getal gaf. De meting is strakker dan
  de renderer, dus onder 0,9 is het een bevinding en niet een grensgeval. Wat je op de render
  ziet weegt zwaarder dan wat de functie zei.

**Vertrouw de render niet voor regelafbreking als de huisstijlfonts ontbreken.** Meldt
`preflight.py` geen Gotham of Montserrat, dan substitueert de renderer bredere letters en vallen
titels en koppen in echte PowerPoint rúimer uit dan je ziet. Compositie, wit, overlap en
uitlijning beoordeel je gewoon; regelafbreking en dus vakhoogte niet. Rek in dat geval geen
tekstvak met de hand op om een afbreking te repareren — dat vak staat dan in de echte weergave te
ruim. De cover is de gevoeligste plek, want daar staat de dektitel op één regel in een vak van
5,33 in dat je zelf op maat hebt gezet, en geen script rekent hem na.

### Escalatie naar `sfnl-infographic`

Er is een tweede skill die één beeld op maat bouwt. Die kost een aparte ronde en een aparte
agent, dus je zet hem nooit ongevraagd in en er is geen bovengrens per deck.

De aanleiding komt van het oog, niet van een telling. Concreet: `deck-visual-reviewer` wijst een
slide aan als tekstwand of als slide die met een vorm beter af was, en jouw herontwerp met het
repertoire uit `shapes.py` haalt het in één ronde niet — de bevinding staat er in de hercheck
nog, of dezelfde slide komt voor de tweede keer terug.

De slidegebonden tellingen uit `qa_tellingen.py` — maatsprong, twee letterfamilies, de hoge
punt — zijn hierbij aanvullend en nooit op zichzelf genoeg. Een lage maatsprong is een
compositiefout, geen infographic-vraag: die los je op met maat, gewicht en kleur. De drie
deckbrede tellingen kunnen per definitie niet naar één slide wijzen en spelen hier geen rol.

Is het zover, dan meld je wat er aan de hand is — welke slide, waarom het herontwerp het niet
haalde, en wat het beeld zou moeten doen — stel je de escalatie voor met de kosten erbij (een
extra ronde en een aparte agent per beeld), en wacht je op ja of nee. Bij nee herontwerp je de
slide zelf met het repertoire, en zeg je bij oplevering dat die slide de zwakste is gebleven.

Als de loop schoon is, doe je één keer de beslistoets uit `adviesvorm.md` §5: de titelrij
hardop, de kneep per slide, en de vraag of de ontvanger met alleen deze deck het besluit kan
nemen. Wat daar sneuvelt is een contentfout en gaat terug naar de outline, niet naar de opmaak.

## Stap 5 — Opleveren

Controleer de hygiëne en de tellingen:

```bash
python $S/qa_text.py deck.pptx
python $S/qa_tellingen.py deck.pptx --renders png
```

`critical` blokkeert de oplevering. `warn` is een aanwijzing: kijk ernaar en beslis.

`qa_tellingen.py` is geen derde poort — de poorten zijn het vragenvuur en de outline, en beide
zijn een mens die ja zegt. Het telt zes dingen die
mechanisch vast te stellen zijn en die afwijken van besluiten die je zelf hebt genomen: meer
dan één maat per rol, een band vaker dan één per vier slides, nul grafieken en tabellen in een
deck met cijfers, een maatsprong onder 2 op een slide, Montserrat en Lato in dezelfde alinea,
en de hoge punt binnen een regel. Drie daarvan blokkeren: maten per rol, letterfamilies en de
hoge punt. Dat zijn precies de drie waar geen interpretatie aan te pas komt. De andere drie —
bandfrequentie, nul exhibits bij cijfers, en een maatsprong onder 2 — zijn een `warn`, want geen
van de drie is zonder de render te beoordelen.

Vier getallen komen zonder oordeel mee: woorden per slide en per element, de registerverdeling
(alleen met `--renders`), en de herhaalde plattegrond. Daar staat bewust geen drempel op. Een
`critical` op woorden per slide leert je tekst versnipperen in plaats van reduceren, en dat is
het defect zelf: het gemeten deck stond op gemiddeld 177 woorden per contentslide met een piek
van 255, en tien slides van negentig woorden zijn geen verbetering. Lees die cijfers, weeg ze
tegen het dichtheidsbesluit, en laat de render en `deck-visual-reviewer` erover oordelen.

Zijn de huisstijlfonts gesubstitueerd, zeg dat dan bij de oplevering en noem waar het uitmaakt:
vraag de gebruiker het deck één keer in echte PowerPoint te openen en vooral naar de cover te
kijken. Somt de bouw handmatige hoogtecorrecties op tekstvakken, noem die met naam — dat zijn de
plekken die in de echte weergave te ruim kunnen staan. Laat dit geen algemene disclaimer worden;
één concrete plek waar hij moet kijken is meer waard dan een voorbehoud over de hele deck.

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

Zes dingen. De eerste drie zijn van de soort "het bestand is stuk", en 4 tot 6 zijn een
`critical` uit een script. Wat daarin over vorm gaat, staat er alleen omdat het te tellen is
zonder interpretatie: Gotham Bold hoort niet in de contentzone, dezelfde rol staat niet op twee
maten, een alinea draagt één letterfamilie, de hoge punt scheidt niets, en een titel die over de
subtitel heen groeit laat tekst verdwijnen. Verder blokkeert er niets op vormgeving; dat oordeel
komt van de render.

1. Het content-type staat niet op `presentation.main`. PowerPoint opent de deck dan in
   sjabloonmodus.
2. `pack.py` meldt een schemafout.
3. De grafieken zijn verdwenen na de laatste `pack`. Vergelijk `charts` in de JSON van
   `qa_text.py` met wat je hebt toegevoegd.
4. `qa_text.py` meldt een `critical`: een restplaceholder, een `{{MARKER}}` uit het concept,
   een sjabloonprompt, een slide zonder inhoud, of Gotham Bold in de contentzone.
5. `fit_title.py` meldt een `critical`: een titel van twee regels boven een gevulde subtitel,
   waar de gegroeide titelbox over de subregel heen loopt.
6. `qa_tellingen.py` meldt een `critical`: dezelfde rol op twee maten, Montserrat en Lato in
   dezelfde alinea, of een hoge punt als scheiding binnen een regel. Alle drie zijn afwijkingen
   van een besluit uit de outline, niet oordelen over je compositie.

## Zonder renderer

Meldt `preflight.py` geen renderer, dan bouw je blind. Dat verandert twee dingen.

Bouw conservatiever: minder elementen per slide, ruimere marges tussen vormen, en kort de tekst
in tot ruim binnen zijn vak in plaats van precies. Meet wat je kunt meten:

```bash
python $S/fit_title.py unpacked --check   # passen de titels, met het echte font, zonder te schrijven
python $S/inspect_deck.py deck.pptx   # wat staat er werkelijk op elke slide
python $S/qa_tellingen.py deck.pptx   # zonder --renders: geen registerverdeling
```

En zeg wat je zó niet hebt gezien. `qa_text.py` en `qa_tellingen.py` zien geen overlap, geen
contrast, geen dood wit en geen baseline; ze meten wat in de XML staat. Blind bouwen betekent
dus: geen vormbeoordeling, en dat zeg je bij oplevering met zoveel woorden.

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

Renderen en beoordelen doe je daarna net zo goed als bij een nieuwe deck. De tellingen scope je
wel:

```bash
python $S/qa_tellingen.py uit.pptx --nieuw 12,13
```

Een deck dat vóór de huidige regels is gebouwd heeft op vrijwel elke slide een gemengde alinea —
op het eerste gemeten deck 71 stuks. Zonder `--nieuw` blokkeren die het toevoegen van twee slides
op tachtig bevindingen in tekst waar je niet aan hebt gezeten. Ze verdwijnen niet, ze komen onder
`overgeerfd` te staan: waar, en iemand mag besluiten het oude deck door te trekken. De deckbrede
tellingen blijven wel gewoon staan, want een tweede maat per rol introduceer je juist zelf zodra
je een slide toevoegt die niet bij de deck past.
