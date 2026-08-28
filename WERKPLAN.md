# Werkplan — slides visueel aantrekkelijker maken

Status: **in uitvoering, go gegeven.** Stap 0 tot en met 6 zijn uitgevoerd (commits `25f099e`
tot `313dc1b`), inclusief de vier reconstructies in `assets/maatstaf/`, het nieuwe
`qa_tellingen.py`, en één volledige testronde in twee dichtheden. (`set_notes.py` is er in
die ronde bij gekomen en later weer uit: presentatornotities zijn nooit nodig.) Wat nog open
staat, staat onderaan bij **Openstaand**. Het plan staat op zichzelf: de opdracht, de meting eronder en de keuzes staan
hieronder, niet in een los promptdocument.

## Doel

De skill levert nu twee soorten decks op. Soms een slide die de lat haalt — een genummerde
faserij, een tabel met verzadigde rijlabels en een puntenmeter, een dumbbell-plot, een
schematische post-itwand. Vaker een tekstwand: vier kolommen met elk zeventig woorden, een
oranje band eronder, geen enkel beeld. Welke van de twee je krijgt, hangt nu af van hoeveel de
gebruiker doorvraagt.

Doel is dat de goede uitkomst de default wordt. De meetlat is visuele aantrekkelijkheid, niet
een set drempels: het gaat erom dat je de nieuwe render aanwijst als de betere.

## Nulmeting — waarom dit nodig is

Gemeten aan de twee bijgeleverde decks (`Werksessie 1 impactmeten RO/RS`, 23 en 19 slides,
gerenderd via LibreOffice met Montserrat en Lato geïnstalleerd):

| bevinding | gemeten | wat de maatstaf zegt |
|---|---|---|
| tekstlast per contentslide | werksessie gem. 177 woorden, piek 255 (slide 6); spreekdeck gem. 85 | staat nergens |
| bodymaat | deckbreed 14pt; spreekdeck gebruikt 12/13/14/15/16 door elkaar | destijds 16pt, één maat per rol (`vormentaal` §2). De 14 die hier gemeten werd is later de norm geworden; het defect was de vijf maten door elkaar, niet de 14 |
| drager 28–40pt | 4 van 17 contentslides (5, 7, 8, 15); de andere 13 volledig op 14pt navy | max 1 op 3, rest via gewicht en kleur (§1) |
| samenvattingsband | 14 van 17 contentslides, dus één per 1,2 slide | max 1 per 4 slides (§10) |
| grafieken / tabellen | 0 / 0, in een deck met 26 doelen, 65%, 42 documenten, 8 thema's | minstens één bij cijfers (§12) |
| twee registers | elke contentslide in hetzelfde middengrijs | minstens één bijna wit, minstens één verzadigd (§5) |
| plattegrond | "vier kolommen, kop plus twee alinea's" herhaalt, met per kolom dezelfde vetgezette aanhef (8×) | één plattegrond max twee keer (§10) |

Twee observaties bepalen de aanpak. **De maatstaf beschrijft elk van deze defecten al**, met
getallen — de doctrine ontbreekt dus niet. En het patroon achter alle rijen is hetzelfde: de
tekst is er eerst en de vorm past zich aan. Daarom zakt de body naar 14pt, daarom vier kolommen
in plaats van een schema, daarom geen witte slide.

Twee bijvangsten: `qa_fit.py` en `qa_typography.py` worden door vijf scripts aangehaald als "de
poort in QA-only-modus" en bestaan niet in de repo. En `libreoffice-impress` ontbrak in deze
omgeving terwijl `preflight.py` meldde dat de renderer er wél was — `soffice` gaf alleen
`Error: source file could not be loaded`.

## Stappen, in volgorde

### 0. Fixtures en nulmeting vastleggen
Renders en metingen van de twee decks-zoals-ze-zijn als vertrekpunt bewaren, zodat elke ronde
tegen hetzelfde vertrekpunt vergelijkt. Raakt geen skillbestanden.

De renderomgeving hoort bij de fixture, want `preflight.py` heeft hier al één keer gemeld dat de
renderer er was terwijl er niets rendde. Zonder deze regels is de voor/na-vergelijking niet
reproduceerbaar:

| onderdeel | versie |
|---|---|
| LibreOffice | 24.2.7.2 420 (`libreoffice-impress` moest apart geïnstalleerd worden) |
| pdftoppm (poppler) | 24.02.0 |
| fonts-lato | 2.015-1 |
| fonts-montserrat | 7.222-2 |
| python / python-pptx | 3.11.15 / 1.0.2 |

Gotham Bold is niet geïnstalleerd en zal dat vrijwel nooit zijn: titelregels worden dus
gesubstitueerd. Compositie-oordelen blijven geldig, regelafbrekingen in titels niet. Elke ronde
draait op deze omgeving, of noteert waarin hij afwijkt.

### 1. Werklijn F — de twee typografieregels
Het goedkoopst en volledig mechanisch, dus eerst.

- **Eén familie per regel.** Een aanhef binnen een doorlopende regel wordt Lato, niet Montserrat:
  aanhef in een echt zwaarder Lato-gewicht (`Lato Semibold` bestaat als eigen familienaam, dus
  geen `b="1"`-nepvet), rest in Lato Light. Montserrat SemiBold blijft voor wat losstaat: kop,
  kapitaallabel, rolnaam, kolomkop.
- **Geen hoge punt als scheiding binnen een regel.** Twee feiten zijn twee regels, twee cellen of
  twee elementen. Geldt in de contentzone, in labels en in bronregels.

**De bewijsclaim gaat mee, en dat is het zwaarste deel van deze werklijn.** De docstring van
`aanhef()` verkoopt de oude regel niet als voorkeur maar als meting: "Gemeten in `maatstaf/04`:
acht alinea's, elk met een SemiBold aanhef van twee tot vier woorden op dezelfde 16pt". De nieuwe
regel verklaart dat gemeten patroon dus fout. Dat kan niet blijven staan: dan wijst de reviewer
straks naar 04 als voorbeeld van wat we net verboden hebben.

Er is eerst een feitenvraag te beslechten. Bij het bekijken van `maatstaf/04` lijken de
vetgezette aanhefjes in x-hoogte en letterbouw op de Lato-body eronder en niet op een
Montserrat-run — mogelijk is de meting in de docstring onjuist en gebruikte de winnende slide al
een Lato-gewicht. Beslissende test: dezelfde zin in beide varianten renderen en tegen 04 leggen.

- Blijkt 04 werkelijk Lato: dan corrigeert de nieuwe regel een verkeerde meting in plaats van dat
  hij bewijs overrulet, en dat schrijf ik zo op.
- Blijkt 04 werkelijk Montserrat: dan overruled Xaviers besluit een gemeten patroon uit een
  winnende deck. Dat mag, maar dan wordt 04 als lat voor dit aspect geschrapt of geherannoteerd,
  en staat er expliciet bij dat de rest van die slide (twee hues voor een tegenstelling, proza als
  exhibit) wél de lat blijft.

Raakt: `scripts/shapes.py` (`aanhef()` bakt de oude regel in, docstring inclusief de
maatstaf-meting; `run()` krijgt de guard), `reference/vormentaal.md` §9 (waar de oude regel
expliciet staat aanbevolen), de annotatie bij `assets/maatstaf/04`,
`reference/adviesvorm.md` §4, `agents/deck-visual-reviewer.md`, `skills/sfnl-slides/SKILL.md`.
Beide patronen worden repobreed opgezocht: een regel die op één plek verandert en op drie andere
blijft staan, komt terug.

### 2. Werklijn B — repertoire, en vooral eigen vormen makkelijk maken
De kern van de opdracht. Nu levert `shapes.py` in de praktijk rechthoeken, lijnen en tekst, en
wie alleen dat heeft bouwt kaarten met tekst — ook als het onderwerp iets anders vraagt.

- **Ruimer repertoire**: genummerde badge, puntenmeter (`●●○`), dumbbell/lollipop op schaal,
  tijdlijn op schaal, pijl tussen twee vormen, gestreepte nadrukomlijning, geschematiseerde
  post-it, gestapelde verhoudingsbalk, accolade die groepeert, ring of boog voor een aandeel.
  Ruim zijn: een ontbrekend merkteken is een slide die tekst blijft.
- **Een korte weg naar een eigen vorm**, en dit is het belangrijkste deel:
  elke PowerPoint-presetvorm vindbaar met zijn `adj`-handvatten gedocumenteerd (`vlak()` kan al
  een `prst` meekrijgen, maar niemand vindt dat terug); een eigen contour (`custGeom`) uit punten
  in inches zonder XML te typen; vormen verbinden, op elkaars rand zetten, als groep verplaatsen
  en schalen.
- **Voorwaarde**: alle bestaande discipline geldt automatisch óók op een eigen vorm — alpha in
  plaats van `lumMod`, absolute hoekradius, lijn in de eigen hue, expliciete `<a:latin/>`,
  `noAutofit`, kleur- en contrastregels. Een eigen vorm mag niet de achterdeur zijn waardoor de
  huisstijl eruit loopt.

Raakt: `scripts/shapes.py` (hoofdmoot), `reference/vormentaal.md` §12 (wanneer een vorm een zin
vervangt — positie op schaal is de kern), `skills/sfnl-slides/SKILL.md` stap 3.4.

### 3. Werklijn A — het beeldbesluit en de tekstlast per register
Niet "minder tekst", maar: er komt een moment waarop iemand kiest tussen tekst en beeld, en die
keuze wordt opgeschreven. Eén regel per slide in de outline: wat wordt beeld, wat blijft tekst,
**en waarom niet visueler**. Die laatste helft is het werk.

Het budget hangt aan het dichtheidsbesluit uit stap 4 en is dus geen enkel getal: op een
spreekdeck is veel tekst altijd fout (daar staat op de slide wat de spreker zegt), op een
leave-behind mag een slide dicht zijn en is een prozaslide een volwaardige exhibit.
Richtwaarden worden gemeten aan de vier goede voorbeelden, `assets/maatstaf/` en de twee
bijgeleverde decks. Plus: repeterende aanhef op elke kolom betekent dat die labels een rijkop
zijn en de vorm een tabel. En de bandregel scherper, met erbij wat er in plaats van de band
afsluit.

Raakt: `skills/sfnl-slides/SKILL.md` stap 2, `reference/vormentaal.md` §10 en een nieuwe
paragraaf over tekstlast per register.

### 4. Werklijn D — de intake en de vijf besluiten
Geen nieuwe widget. De vier intakevragen en de vijf deckbrede besluiten worden de plek waar de
stijl gekozen wordt in plaats van waar hij impliciet ontstaat: elk besluit krijgt een expliciete
default met de gevolgen erbij, en er komt een zesde bij — **de dichtheid** (spreekdeck of
leave-behind). De zes worden bij de outline als één blok voorgelegd. Geen vijfde intakevraag.

Raakt: `skills/sfnl-slides/SKILL.md` stap 1 en 2.

### 5. Werklijn C — meten waar meten eerlijk is
Veel van wat deze decks lelijk maakt is niet in een drempel te vatten, dus geen poort die doet
alsof dat wel zo is.

**Wél tellen** (mechanisch, zonder interpretatie), met per telling het niveau waarop hij vuurt:

| telling | niveau |
|---|---|
| meer dan één maat per rol | deck |
| bandfrequentie boven één per vier slides | deck |
| nul exhibits in een deck met cijfers | deck |
| maatsprong onder ~2 | slide |
| Montserrat en Lato in dezelfde alinea | slide |
| de hoge punt binnen een regel | slide |

Dat onderscheid is niet cosmetisch: drie van de zes tellingen kunnen per definitie niet naar één
slide wijzen, en dat bepaalt wat de escalatie in stap 6 wel en niet kan zien.

**Niet in een drempel**: tekstlast, registerverdeling, herhaalde plattegrond, aantrekkelijkheid.
Die worden gerapporteerd als getal zónder oordeel. Een `critical` op woorden per slide zou de
bouwer leren tekst te versnipperen in plaats van te reduceren — precies het defect waar we
vandaan komen.

**`qa_fit.py` en `qa_typography.py` gaan eruit, niet erin.** De keuze is nu gemaakt in plaats van
opengelaten: de repo zet zelf "Poorten: één: de outline" (README) en implementeren zou de
vormgevingspolitie herbouwen die deze plugin bewust weglaat. De dangling verwijzingen in
`preflight.py`, `_deck.py`, `add_chart.py`, `add_table.py` en `qa_text.py` worden dus opgeruimd en
`SKILL.md` en `preflight.py` zeggen wat de poort werkelijk is.

Dat maakt het nieuwe telscript wél een verantwoording waard, en die luidt: het is een
hygiënerapport in dezelfde categorie als `qa_text.py`, geen tweede poort. Alleen wat mechanisch en
zonder interpretatie vast te stellen is blokkeert, en dat zijn afwijkingen van besluiten die de
bouwer zelf in de outline heeft genomen — niet oordelen over zijn compositie.

En de kant die wél oordeelt versterken: `deck-visual-reviewer` scherper op tekstwanden, op slides die met een vorm
beter af waren, en op "ziet dit er aantrekkelijk uit" in plaats van alleen "is dit correct".

Raakt: een nieuw QA-script in `scripts/`, `scripts/preflight.py` (inclusief de foutieve
renderermelding), `agents/deck-visual-reviewer.md`, `skills/sfnl-slides/SKILL.md` stap 5.

### 6. Werklijn E — escalatie naar `sfnl-infographic`
Geen bovengrens per deck, nooit ongevraagd.

**De aanleiding komt primair van het oog, niet van de telling.** De eerdere formulering — drie of
meer poortwaarschuwingen op één slide — kan structureel niet vuren op de slides waar het om gaat:
tekstlast, registerverdeling en aantrekkelijkheid houdt stap 5 bewust buiten de poort, en drie van
de zes tellingen zijn deckbreed. Een klassieke tekstwand haalt dus makkelijk nul
poortwaarschuwingen. Dus:

- **Aanleiding 1, leidend:** `deck-visual-reviewer` wijst een slide aan als tekstwand of als slide
  die met een vorm beter af was, en het herontwerp met het eigen repertoire haalt het in één ronde
  niet.
- **Aanleiding 2, aanvullend:** de slidegebonden tellingen uit stap 5 vuren samen met zo'n
  bevinding. Nooit op zichzelf: een lage maatsprong is een compositiefout, geen infographic-vraag.

De skill meldt dan wat er aan de hand is, stelt de escalatie voor met de kosten erbij, en wacht op
ja of nee. Bij nee herontwerpt hij de slide zelf met het repertoire uit stap 2.

**Nagekomen in ronde 8:** die escalatie wees naar een skill buiten deze plugin, en dat is de
reden dat hij in de praktijk zelden landde. `sfnl-infographic` staat er nu in, met dezelfde
`shapes.py`, hetzelfde sjabloon en dezelfde layouts, dus de escalatie blijft binnen één plugin
en de vraag "wat geef je mee" heeft een antwoord: het vlak en de titel.

Raakt: `skills/sfnl-slides/SKILL.md`.

### 7. Testrondes
1. Herbouw de werksessie uit dezelfde inhoud, volgens de skill zoals hij dan is, zonder extra
   aanwijzingen — dat is het hele punt van de test.
2. Bouw beide registers: dezelfde inhoud één keer als spreekdeck en één keer als leave-behind.
   Het bijgeleverde paar is precies dat, en of het dichtheidsbesluit werkt blijkt alleen als de
   twee uitkomsten werkelijk verschillen.
3. Blinde vergelijking, met **twee jurylieden**: de aangescherpte `deck-visual-reviewer` én de
   ongewijzigde versie van vóór stap 5, uit `main`. Rechter en verdachte tegelijk veranderen maakt
   "verbetering" niet te onderscheiden van "de lat is verschoven"; de oude reviewer is de vaste
   maat. Beide krijgen de oude en de nieuwe render naast de vier goede voorbeelden, zonder uitleg,
   met één vraag erbij — welke van deze slides zou je aan een klant laten zien. Wijken de twee van
   elkaar af, dan is dat zelf een bevinding over de aanscherping.
4. Twee tot drie ronden, per ronde één wijziging met een reden. Stopt de verbetering, dan stop ik ook.

## Ontwerpkeuzes en hun alternatieven

| keuze | alternatief dat is afgewogen | waarom niet |
|---|---|---|
| Merktekens als primitieven, plus een makkelijke weg naar een eigen vorm | een patroonbibliotheek waar de skill uit kiest | de skill kiest bewust geen patronen uit een catalogus; een catalogus levert opnieuw eenvormigheid, alleen met mooiere blokken |
| Tekstlast rapporteren zonder oordeel | een harde `critical` op woorden per slide | dan leert de bouwer versnipperen in plaats van reduceren, en dat is het defect zelf |
| Tekstlast koppelen aan het register | één deckbreed maximum | veel tekst is niet altijd fout: op een leave-behind mag een slide dicht zijn, op een spreekdeck nooit |
| Aanhef binnen een regel in Lato Semibold | Lato Light met `b="1"` | nepvet; `Lato Semibold` bestaat als eigen familienaam en is een echt gewicht |
| Escalatie op verzoek, met de aanleiding uit het oog van de reviewer | aanleiding uit de mechanische poort; of automatisch escaleren voor de mooiste slides | de poort ziet tekstwanden per definitie niet, en automatisch escaleren kost quota terwijl het repertoire uit stap 2 het overgrote deel zelf moet afhandelen |
| `qa_fit.py` en `qa_typography.py` opruimen | ze alsnog implementeren | de repo zet zelf "Poorten: één: de outline"; implementeren herbouwt de vormgevingspolitie die deze plugin bewust weglaat |
| Geen nieuwe widget | invulwidget met live voorbeeldslide | Xavier heeft dit expliciet zo gekozen: de intake en de vijf besluiten zijn de plek |

## Definitie van klaar

Per werklijn: de wijziging staat in de betreffende bestanden, repobreed consistent (geen regel
die op één plek is aangepast en elders blijft staan), en `python scripts/preflight.py` plus de
bestaande testsuite lopen schoon.

Voor het geheel, in deze volgorde van gewicht:

1. De nieuwe renders zijn in de blinde vergelijking aan te wijzen als de betere.
2. Slide 6 — de vier kolommen van 255 woorden — is een schema, een tabel of twee slides geworden.
   Reductie mag en is meestal het punt: wat eruit gaat, gaat eruit met een reden die op te schrijven
   is. De toets is dat geen bewering ongemerkt verdwijnt, niet dat alle 255 woorden ergens
   terugkomen — dat laatste zou versnipperen belonen, precies het defect uit stap 5.
3. De tellingen uit werklijn C staan schoon.

Staat 3 schoon terwijl 1 niet lukt, dan zijn de verkeerde dingen gemeten en gaat dat terug in de
skill.

Op te leveren: de diff, de contactbladen van vóór en ná, de meting op beide, en een kort verslag
— welke drempels erin staan en waarop ze zijn gemeten, wat er is afgevallen, en wat er open blijft.

## Randvoorwaarden

- Branch `claude/brave-pascal-orang9`, kleine commits per werklijn, commitberichten in de toon van
  de bestaande geschiedenis (één regel die zegt wat het besluit was).
- Geen nieuwe Python-afhankelijkheden.
- De referentiedocumenten hebben een eigen register: nagemeten, met de verkeerde lezing erbij waar
  die is voorgekomen. Schrijven in dat register of niet schrijven.

## Ronde 2 — het vragenvuur als poort, en een referentie per antwoord

Deze ronde gaat over de andere kant van dezelfde opdracht: niet of de bouwer visueel denkt, maar
of de gebruiker de vorm werkelijk kan kiezen. De zes besluiten hingen bij de outline, dus er lag
al tekst wanneer er voor het eerst iets te kiezen was, en vijf van de zes hadden een default met
een reden maar geen beeld en geen uitkomst. Wat er is gedaan:

- **De zes zijn stap 1 geworden, samen met de vier intakevragen, en het is een poort.** Tien
  vragen in één blok, en er wordt niets geschreven voordat ze beantwoord zijn — geen storyline,
  geen outline, geen slide. Overslaan bij een bekend antwoord mag niet meer: dan vul je het in
  als voorstel en de gebruiker bevestigt het. De skill heeft daarmee twee poorten en beide zijn
  een mens; de README, `preflight.py`, `qa_text.py` en `qa_tellingen.py` citeerden "Poorten: één:
  de outline" en zijn meegegaan.
- **Elk besluit heeft nu een referentie én een uitkomst.** Bij besluit 1 en 3 wijst de maatstaf
  het aan: `13`/`14`, `12` en `11` zijn de drie dichtheden, en `11` (afgerond, haarlijn in de
  eigen hue) tegenover `12` (recht, geen haarlijn) zijn de twee kaarttalen. Dat stond nergens,
  terwijl de beelden er al waren. `LEESMIJ.md` noemt het nu per slide.
- **Een derde dichtheid: licht leave-behind.** De meting wees hem al aan en niemand had hem
  benoemd — het gemeten "spreekdeck" op gemiddeld 85 woorden was te dicht voor een spreekdeck en
  te dun voor een leave-behind. Dat was geen mislukt deck maar een register zonder naam, en het
  is de gewone SFNL-situatie: er wordt bij gepraat én het deck gaat mee. Daarmee is het de
  default. De drie hangen aan één vraag (praat er iemand bij, en gaat het deck de mail in?) en
  elk aan een gemeten voorbeeld.
- **Oranje is het accent, vast.** Besluit 4 was "één accentkleur naast navy" zonder te zeggen
  welke, en dat is geen besluit maar een lege plek: geen van de veertien voorbeelden is een
  deck-met-één-accent, dus de default had ook geen beeld. Nu staat oranje er, met de uitkomst
  erbij die je erbij koopt — oranje haalt 2,6 op wit, dus het accent kan nooit een gelezen regel
  dragen en alles wat gelezen wordt blijft navy. Per slide mag één tweede hue erbij als die iets
  codeert; een sét van drie of vier hues (`11`, `12`) is een deckbreed besluit en geen
  slidekeuze. In `vormentaal.md` §3 is de vaste laag daarop bijgesteld: oranje codeert buiten een
  set niets, want daar ís hij het accent.
- **Wie wat mag kiezen, staat in één tabel.** "Kies jij maar" is een geldig antwoord per besluit.
  Kaarttaal mag de skill altijd zelf nemen, ook afwijkend, met een reden. Dichtheid en accent per
  slide laten verschillen mag alleen met expliciete toestemming. De titelmodus varieert nooit per
  slide. Dat is de grens tussen "de skill kiest" en het gemeten defect dat het besluit per slide
  opnieuw neemt.
- **Twee onscherpe plekken gedicht.** Besluit 3 vroeg ook naar de vullingssoort en dat overlapte
  met besluit 5: een deck waarvan de default "vol" is, kan geen slide op wit meer hebben. De
  vulling hoort bij de registers en is daar nu ondergebracht. En "de rest ligt ertussen" in §5
  gaf de middenband vrij die diezelfde paragraaf als het defect meet; die zin heeft nu een vloer,
  namelijk de gemeten 44 tot 53 procent wit met 42 tot 54 procent tint.

Wat deze ronde niet heeft: een render. De omgeving had `python-pptx` niet, dus de wijzigingen zijn
doctrine en geen gemeten uitkomst. De drie dichtheden zijn nog nooit als drie decks naast elkaar
gebouwd, en dat is de test die hierbij hoort.

## Ronde 3 — de kleur- en gevuldheidsproef

De twee besluiten die na ronde 2 nog op doctrine stonden zonder render, zijn gebouwd: zes
varianten van dezelfde inhoud (drie gevuldheden maal twee kleurschema's) plus drie gerichte
proeven erna. De renders en de metingen staan in `assets/proeven/`, de opzet erbij zodat ze te
herhalen zijn. Vier dingen kwamen eruit, en alle vier zijn in de doctrine gezet:

- **Nadruk in de letterkleur draait de hiërarchie om.** Twee van vier koppen oranje, twee navy:
  de navy koppen lezen sterker (15,3 tegen 2,6). Dat is de keerzijde van "oranje is het accent"
  die op papier niet te zien was. De vorm die het oplost is een volle oranje chip met navy
  tekst, met alle koppen navy.
- **Het grijs is geen grijs.** `tx1` lumMod 65 rendert als `#5176A7`, 51 procent verzadigd — een
  vijfde blauw naast sky en royal. Geen enkele lichtheidstrap van dat slot is neutraal, want
  `tx1` is zelf `#233348`. Het stille label is daarom navy op alpha 70 zonder spatiëring, en het
  lumMod-recept is beperkt tot decks zonder set hues.
- **De alpha-en-spatiëringsbug is een klipping en heeft geen veilige ondergrens.** Niet
  aan-of-uit: het tekort loopt op met de spatiëring maal het aantal tekens, dus `spc=60` klipt al
  en `VERANTWOORDEN` verliest bij 100 de hele N. Een spatie erachter helpt niet en een breder vak
  ook niet.
- **Verzadigd is te begroten, en vier rijlabels halen het niet.** Eén procent is ongeveer één
  vierkante inch: een blok van 8 bij 2,5 in meet 21 procent, een band over de volle breedte 25,
  en vier rijlabels van 3,40 in samen 14 — terwijl die slide vol voelt. Verzadigd lukt ook met
  alleen oranje, dus daar is geen set hues voor nodig.

Bijvangst: de renderomgeving is in deze sessie opnieuw opgebouwd (`libreoffice-impress`,
`fonts-lato`, `fonts-montserrat`, `poppler-utils`), en met alleen `libreoffice-core` meldt
`preflight.py` nu correct dat er geen importfilter voor pptx is.

## Ronde 4 — besluit 5 herschreven op de renders

Xavier heeft de zes varianten bekeken en de keuze gemaakt, en die keuze verandert besluit 5 van
"twee registers" naar drie gevuldheden:

- **`proeven/03` is de default** — weinig accent: geen kaartvullingen, navy koppen op wit, een
  haarlijn per rij, en één vol oranje vlak precies waar de nadruk zit (92 procent wit, 3 procent
  verzadigd).
- **`proeven/01` is kaal** en **`proeven/02` is met kleur**; beide mogen in dezelfde deck naast de
  grondtoon staan, waar de inhoud erom vraagt. Dat wisselen ís het contrast tussen de slides.
- **`proeven/04` valt af.** Hij haalt 25 procent verzadigd en zit dus binnen de band die de
  winnende decks laten zien, en hij wordt toch niet aangemoedigd: het oppervlak is groot en
  draagt vier woorden. Daarmee is de band van 20 tot 37 procent in §5 een meting geworden in
  plaats van een doel — een wijziging in de doctrine die alleen op een render te nemen was.

Gevolgen die zijn meegenomen: de vullingssoort staat nu bij de gevuldheid in plaats van bij de
kaarttaal (besluit 3 vroeg er ook naar), `deck-visual-reviewer` heeft twee nieuwe rijen (wisselt
de gevuldheid, en draagt een groot vol vlak wel iets), en het ijkpunt in `qa_tellingen.py` zegt
niet langer dat de reeks naar 20 tot 37 procent toe moet.

## Ronde 5 — het vragenvuur ingedeeld, met een kaart erbij

Twee wijzigingen, beide op verzoek van Xavier.

**Van zes vormbesluiten naar vier, in de volgorde grof naar fijn:** dichtheid, gevuldheid, wat
kleur codeert, titelmodus. De vier maten en de kaarttaal worden niet meer gevraagd — de maten zijn
een regel met één tweesprong (body 12pt bij een kaartenrij van drie of meer), en de kaarttaal
kiest de skill zelf met de reden in de outline. Ze staan nog wél in stap 1, als het blok "twee
dingen worden niet gevraagd", want de bouwer moet weten wat er dan geldt. Het vragenvuur is
daarmee acht vragen: vier over de opdracht, vier over de vorm.

**Een keuzekaart bij de vier vormvragen.** `assets/keuzekaarten/vragenvuur.png`: per besluit de
opties naast elkaar als detailuitsnede uit een echte render, met de meting eronder. De skill
stuurt het bestand en leest het niet, dus het kost geen tokens en geen render — dat was de eis.
`scripts/keuzekaart.py` bouwt hem opnieuw uit de renders die in de repo staan; het is
onderhoudsgereedschap en geen bouwstap.

Daarvoor moest één gat gedicht worden: titelmodus B had geen render. Die is er nu
(`proeven/07`, `08`) — een divider uit fotolayout 6 met de hoofdstuknaam, en een contentslide met
diezelfde naam als titel en de bewering in de subtitel. De bijvangst die hier stond — "de
subtitel duwt de contentzone omlaag" — is later nagemeten en onjuist: de subtitel staat op
`1.04 · 0.63`, dus boven de dash op 1,72, en de zone begint in beide modi op 1,93. Wat modus B
werkelijk kost is hiërarchie, niet ruimte.

## Ronde 6 — iconen, getekend en niet geleend

De skill kon geen icoon maken. `contour()` kon een eigen vorm, maar niets zei hoe een icoon in
deze huisstijl gezet wordt, dus kwam er geen. Nu:

- **`icoon()` in `shapes.py`**, een raster van 24 bij 24 waarop je de geometrie zelf opgeeft —
  lijn, pad, vorm, cirkel, stip, boog, rechthoek — en de functie de discipline afdwingt: één
  schachtdikte, één hue, geen vulling, ronde uiteinden, één groep. Expliciet géén bibliotheek en
  ook niet de iconengalerij van PowerPoint: dat was de eis, en het is dezelfde keuze als bij de
  patroonbibliotheek die deze plugin niet heeft.
- **`vormentaal.md` §14** met de vraag die vóór het tekenen komt (draagt het icoon iets wat de
  tekst niet al draagt) en de gemeten zetting: 1,5pt, 0,72 in naast een kop van 18pt, 0,44 in als
  ondergrens, ten hoogste twaalf onderdelen, navy tenzij de hue codeert.
- **Twee renders als bewijs**: `proeven/09` (zes iconen, drie diktes, drie maten, zes hues, één in
  wit op vol) en `proeven/10` (dezelfde drie rijen met en zonder icoon). Die tweede is de
  belangrijkste, want hij laat zien dat de versie zónder iconen de rustigere is zodra de kop het
  al zegt — daar komt de regel uit.

Twee metingen die eruit vielen. Een icoonlijn van 1,5pt in oranje haalt 2,6 op wit en leest
lichter dan zijn eigen kop ernaast, dus navy is de default en een hue alleen als hij codeert. En
een pijlkop op een boog moet uitgerekend worden: de eerste kringloop had een kop op geschatte
coördinaten en die zweefde los van de boog — in de code onzichtbaar, op de render meteen.

## Ronde 7 — is de visuele reviewer zijn ronde waard?

De vraag kwam van Xavier: die agent doet elf harde grenzen, twee zoekopdrachten, een
aantrekkelijkheidsvraag en een escalatievoorstel in één ronde, en de duurste bevindingen komen
terug als de slide al gebouwd is. Eruit halen, laten staan, of een tweede pass op de outline?

**Opzet.** De repo blijkt per ongeluk een testset te zijn: 24 renders in `assets/`, met per
slide in de twee `LEESMIJ.md`'s opgeschreven wat eraan mankeert. Dus: acht beelden, de agent
blind erop (zonder die twee bestanden, want die bevatten de antwoorden), en scoren tegen een
scoreblad dat vóór zijn rapport is vastgelegd. Vier bevindingen die hij moest vinden, twee
beelden waarop hij niets mocht vinden, en één vergelijking waar een menselijk besluit op schrift
staat (`proeven/03` tegen `04`, afgekeurd op 21-08-2026).

**Uitkomst.**

| toets | resultaat |
|---|---|
| geklipte glyph op `proeven/06` | gevonden, tot de gradatie per rij (`MEETDOEI`, `VERANTWOORDE`) |
| getal over zijn label op `maatstaf/01` | gevonden, alle vier de labels |
| lege kaarthelften op `01` | gevonden, 1,2 in restgat gemeten |
| dubbele omzetreeks op `08` | gevonden, staven nagerekend tegen de tabelkolom |
| 0,58 in wit tussen de blokken op `14` | half: de kale onderkant (0,7 in) wel, de tussenruimte niet — daar zag hij een rastermismatch van 1,2 in, die na controle echt is |
| valse positief op `11` (141 woorden, de sterkste van de vier) | geen: "voor het overige schoon", geen tekstwandclaim |
| valse positief op `13` (aslabel binnen de zone) | geen: hij verschoof tik noch label |
| `03` tegen `04` | koos `04` af, met dezelfde reden als Xavier, plus zelfstandig de inversie uit `proeven/01` |
| vijf claims buiten het scoreblad, nagekeken | alle vijf waar |

**Twee besluiten.** Hij blijft (a en c vallen af). Van zijn ongeveer 35 bevindingen waren er zes
in de outline te zien, dus minder dan een vijfde — een aparte outline-agent betaalt twee keer
voor werk dat deze pass toch doet, en het voorstel daarvoor is ingetrokken. Wat wel veranderde:
vijf van zijn elf grenzen waren al een `critical` of `warn` in de tellers en zijn uit zijn tabel
gehaald (daar dreven zijn eigen getallen ook uit de maatstaf weg), en de loop werkt nu op de
gradatie in plaats van op leegte — vier bevindingen per slide maal zeventien contentslides is
vijfenzeventig per ronde, en "doorgaan tot er niets meer te melden is" stopt dan nooit.

**Bijvangst.** `maatstaf/13` stond in `LEESMIJ.md` als foutloos en is het niet: de as mist zijn
ijklijn bij 1, de getallen achter de rijlabels zeggen niet wát ze zijn, en de legenda staat in
omgekeerde leesrichting. Dat staat nu in de kolom rechts, met de waarschuwing dat een lege cel
in die kolom geen bewijs van schoon is.

**Wat deze proef niet zegt.** n is acht en hij is niet deterministisch, dus dit is "ziet hij een
ontbrekende glyph", geen precisiecijfer. En de test die het meeste zou zeggen — vindt hij op een
verse deck dingen die de bouwer zelf op het contactblad miste — vraagt een omgeving met
`python-pptx` en een pdf-naar-png-omzetter, en die was er niet.

## Ronde 8 — `sfnl-infographic` in de plugin, en de skills samenstelbaar

Werklijn E hierboven eindigde in een escalatie naar een skill die niet in deze plugin zat. Dat
werkte in theorie: de deckskill stelde de escalatie voor, de gebruiker zei ja, en dan moest er
een skill worden aangeroepen die zijn eigen kopie van de huisstijl droeg, zijn eigen fontzoeker
had en de deckscripts met een glob over `~/.claude/plugins/**` probeerde te vinden. Wat er in
de praktijk gebeurde is wat er altijd gebeurt bij een verwijzing naar iets dat er niet staat:
de bouwer viel terug op de SVG-route omdat de PowerPoint-route "niet beschikbaar" leek, terwijl
`shapes.py` en het sjabloon een map hoger lagen.

Deze ronde zet die skill in de plugin en gebruikt wat er al stond. Vier dingen zijn gemeten en
niet aangenomen.

**1. De letters zijn nu echt gemeten.** `assets/documenten/fonts/` draagt Montserrat en Lato als
woff2 voor de HTML-drukroutes, en `svg.py` leest diezelfde bestanden. Een woff2 is een
gecomprimeerde TrueType, dus fontTools leest hem — met `brotli` erbij, want zonder die module
krijg je het bestand niet open en zakt de meting stil terug op een schatting. Dat is de reden
dat `preflight.py` niet meldt *of er een fontbestand is* maar of de meting echt is.

Eén ding was daarbij niet vanzelf goed. Montserrat komt als één variabel bestand over het bereik
300–800, en zijn standaardinstantie is `wght=100`. Wie de `hmtx` rauw leest, meet dus Thin: de
`e` is daar 587/1000 tegen 597 op Light en 622 op SemiBold. Gemeten op een regel van 46 tekens is
dat 18,4 pt verschil tussen Light en SemiBold, bijna vijf procent — genoeg om een regel te laat
te laten afbreken. `_metriek()` instantieert daarom op het gevraagde gewicht.

En de onbekende-tekenschatting is omgedraaid. Een teken dat niet in de latin-subset zit — in de
praktijk alleen het promillageteken — kreeg de breedte van een spatie, 3,20 pt op 16 pt. Dat is
de verkeerde kant op: het teken is bijna drie keer zo breed, dus zo'n regel brak te laat af. Nu
is de schatting de breedte van een cijfer, 9,60 pt.

**En de maatstaf zelf was fout, wat het bewijs is dat dit geen decimalenwerk is.** De vijf
maatstaven zijn opnieuw gebouwd met de echte metriek, en `m1-geldstroom` verandert zichtbaar: de
drager stond er als `€ 1,2` / `mln` op twee regels, en de bronregel liep ook over twee regels.
Beide passen op één regel — met de geschatte, ruime metriek paste "€ 1,2 mln" op 40 pt niet in
zijn blok van 240 pt, dus brak `regels_van()` hem af. Het beeld dat de skill als norm meestuurde
had dus een gebroken drager, en dat is precies het defect waar §4 van zijn eigen vormentaal tegen
waarschuwt. De PNG's in `assets/infographic/maatstaf/` zijn opnieuw gerenderd.

**2. De render haalt de letters niet meer bij Google Fonts.** `render_svg.py` sluit `fonts.css`
in, hetzelfde bestand dat de documentenroute gebruikt, en om dezelfde drie redenen die in
`assets/documenten/fonts/LEESMIJ.md` staan. Zonder internet viel de render terug op Helvetica en
beoordeelde je de verkeerde regelval — precies de meting die dat bestand liet maken. En Chromium
wordt opgezocht met `scripts/documenten/_browser.py`, want op een machine met
`PLAYWRIGHT_BROWSERS_PATH` klopt het buildnummer van de pip-versie bijna nooit en faalt
`launch()` met een melding die eruitziet alsof er geen browser is.

**3. Eén canvashelper-zoeker in plaats van twee.** `zoek_helper()` staat nu in
`scripts/gedeeld/canvas.py` en beide skills gebruiken hem. Er stonden twee versies van, en ze
waren niet gelijk: de documentenversie sorteerde de treffers alfabetisch en nam de laatste, dus
van `bundled-skills/3b10cbb2/` en `bundled-skills/ea784c4b/` won de tweede op zijn eerste
letter en niet omdat hij bij deze sessie hoorde. Een oude payload betekent een canvas op een
verouderde editor, en dat merk je pas als iemand erin klikt. De gedeelde versie sorteert op
skillversie en daarbinnen op uitpaktijd.

**4. Het samenstellen is een script en geen alinea.** Alle drie de containers zeiden al wanneer
er een infographic nodig is — `vormentaal.md` boven twaalf onderdelen, `documenten-vormentaal.md`
§11, `rapport-vormentaal.md` onder "Geen infographics ontwerpen" — maar geen van de drie zei
**hoe**, en daar zit het defect. Een SVG schaalt álles mee, ook zijn letters. Gemeten op
`m1-geldstroom.svg`: een band van 960 × 320 pt krimpt in het documentkader van 680 px met factor
0,53 en zet daarmee een voetnoot van 10 pt op 5,31 pt, onder de leesvloer van 8, zonder dat er
iets in de markup fout staat.

De reparatie is het canvas en niet het kader. `svg.py` heeft nu zes canvassen met de breedte van
de doelkaders — `doc-breed`, `doc-kolom2`, `doc-kolom3`, `rap-breed`, `rap-kolom`, `rap-dubbel` —
en `Maten.voor("document")` en `Maten.voor("rapport")` voor de maatladder van de container, want
een beeld dat zijn eigen 16 pt meeneemt zet een zevende maat op een pagina die er zes heeft.
`insluiten.py` is de poort: hij leest de `viewBox` en alle `font-size`-waarden, rekent de factor
uit en weigert onder de vloer.

**En daar kwam de eenheid uit, wat pas op de gebouwde pagina bleek.** De eerste versie van deze
zes canvassen stond in punten — 510 × 279 voor het documentkader — met de gedachte dat 510 pt en
680 px hetzelfde fysieke formaat zijn en de SVG dus 1:1 rendert. Dat is ook waar, en het is
irrelevant: **het meetapparaat van de containers leest de opgegeven maat en niet de gerenderde.**
De `te-klein`-regel van `qa_document.py` neemt `getComputedStyle(el).fontSize`, en dat getal
staat in het lokale coördinatenstelsel van de SVG; een `viewBox` die de inhoud opschaalt, ziet
die regel niet. De gebouwde documentpagina gaf elf `critical` — acht keer `te-klein: tspan staat
op 10 px (7,5 pt)` op tekst die op de render 13,33 px was, plus `letterfamilies: 3` — en geen
van de elf was een echt defect.

Dus staan de zes canvassen nu in px met de px-ladder van hun route, precies zoals
`documenten-stramien.md` §5b altijd al voorschreef ("`viewBox` even breed als het kader in px")
en §11 punt 2 bedoelde met "de maatladder geldt ook binnen de SVG". `Canvas` draagt daarvoor een
`eenheid`, `Maten.voor()` zet hem, `schrijf()` weigert een canvas en maten die niet
overeenkomen, en de drie drempels die in punten staan — het dragerwindow van 28 tot 40, de
kopvloer van 18, de displayvloer van 40 — rekenen mee. Zonder die omrekening zou een lichte hue
op een px-canvas ineens tekst van 13,5 pt mogen dragen waar de regel 18 pt eist.

De derde melding was de letterfamilie. `svg.py` schrijft `font-family="Lato Light, Lato,
sans-serif"` en `qa_document.py` telt de eerste naam als familie, dus stonden er drie families op
een pagina die er twee mag hebben. `insluiten.py` haalt de snede uit de naam: het gewicht draagt
hem al en `fonts.css` declareert `'Lato'` op 300, dus de letter blijft exact dezelfde.

Nagemeten na die drie reparaties: hetzelfde beeld op `doc-breed` haalt factor 1,0, en de
gebouwde documentpagina komt door `qa_document.py` met **geen bevindingen**.

**En toen bleek de pagina nog twee dingen te dragen die niemand had geteld.** Allebei zijn ze
onzichtbaar zolang je naar de infographic kijkt, en allebei zichtbaar zodra hij op de pagina
staat — precies het soort defect waar een poort voor is en een render niet.

Het eerste is de **omlijsting**. Een los beeld hoort een aanhef te dragen en een bronregel; dat
staat zo in de inventaris onder "Wat er op het vlak komt", en het klopt, want er is niets anders
dat ze draagt. In een exhibit is er wel iets anders: de pagina heeft een kop, en onder het kader
staat een bijschrift. Op de proefpagina stond de kop "De inleg gaat voor de helft naar
begeleiding" en daaronder in het beeld "WAAR DE INLEG HEEN GAAT", en de bronregel stond twee
keer. `insluiten.py` vergelijkt nu de tekst op het beeld met `--pagina` en `--bijschrift`, en
hij kent het verschil tussen omlijsting en elementlabel: de rol volgt uit de attributen
(kapitalen met letterspatiëring, dekking 0,70, een maat in het dragerwindow) en niet uit de naam,
en hij blokkeert alleen op de omlijsting. Dat onderscheid kwam uit een valse melding: de eerste
versie vlagde het staaflabel "Begeleiding op de werkvloer" omdat de chapeau diezelfde woorden
gebruikte — maar direct labelen is vormentaal §9 en staat boven deze toets.

Het tweede is het **dode wit onderin**. Op een los beeld is dat de eerste bevinding van de
renderloop en zie je het gewoon. In een `.beeldkader` niet: de verhouding van het kader komt uit
de `viewBox`, dus een canvas dat voor 70 procent gevuld is reserveert 30 procent wit op de
pagina. De proef stond op `doc-breed` met zijn defaulthoogte van 372 px terwijl de compositie tot
260 kwam, en die 111 px stonden als niets midden in een zetspiegel. `pas_hoogte(c, vormen)` zet
de hoogte op de inhoud plus één marge — 372 naar 179 — en `wit_onder()` in `svg.py` is de enige
plek waar de regel staat, zodat de waarschuwing in `schrijf()` en de poort in `insluiten.py` niet
uit elkaar kunnen lopen. Eén ondermarge telt niet als dood wit; dat was de eerste versie van de
regel wél, en die stelde dan voor de hoogte te veranderen naar precies dezelfde hoogte.

Wat er daarna gebeurt, lijkt een terugslag en is het niet: `qa_document.py` meldt over de pagina
"de inhoud houdt op 57 procent van de zetspiegel op". Het wit is van onzichtbaar in het beeld
naar zichtbaar op de pagina verplaatst, en daar is het een paginabesluit — meer inhoud of een
kortere pagina — in plaats van een gat waar niemand naar kijkt.

**Wat de proef nog opleverde.** De PowerPoint-route is end-to-end nagelopen op layout 19, en dat
bracht twee fouten in de SKILL aan het licht die er van de losse versie in zaten. De eerste is
luid: `Deck` heeft geen `sluit` en wél een `kop`, precies omgekeerd aan wat er stond, dus een
`TypeError` op de eerste regel van het bouwscript. De tweede is stil en erger. `svg.py` rekent
de dekking als breuk (`0.16`) en `shapes.py` in OOXML-honderdduizendsten (`16000`); met de
verkeerde eenheid wordt `int(0.16)` nul, dus `<a:alpha val="0"/>`, dus een vorm die volledig
doorzichtig op de slide staat. Drie van de vier staven waren er niet en `pack.py` valideerde
schoon. Nu weigert `_clr()` een alpha tussen 0 en 1000 en zegt in de foutmelding welke van de
twee lagen je vermoedelijk voor je had. Twee lagen met een eigen eenheid mag; een eenheid die
stil een onzichtbare vorm oplevert niet.

Raakt: `skills/sfnl-infographic/`, `scripts/infographic/`, `assets/infographic/`,
`reference/infographic-*.md`, `reference/samenstellen.md`, `scripts/gedeeld/canvas.py`,
`scripts/documenten/preflight.py`, `scripts/shapes.py`, en de kruisverwijzing in de drie andere
SKILL's.

## Openstaand

- **De exhibitroute is één keer gedraaid, op één kader.** De keten is end-to-end gebouwd voor
  `document`/`breed`: infographic op `doc-breed`, door `insluiten.py`, als `.beeldkader` in een
  `.dc.html`, door `bouw.py` en `render.py`, en schoon door `qa_document.py`. Wat niet gemeten
  is: de vier andere kaders, en de rapportroute voorbij de `figuren`-regel — `bouw.py` van de
  rapportskill heeft die JSON nog niet met een beeld uit dit script verwerkt.
- **Er is geen maatstaf voor de exhibitroute.** De vijf maatstaven staan alle vijf op een los
  canvas; een infographic op `doc-breed` of `rap-kolom` naast de pagina waar hij in staat, is
  het beeld dat een bouwer nodig heeft om te zien wat 10 pt brood in een figuur doet. Dat is een
  render en een LEESMIJ-alinea, geen nieuw mechanisme.
- **De PowerPoint-route is gerenderd via LibreOffice met gesubstitueerde fonts.** De compositie
  is daarmee geldig beoordeeld, de regelval indicatief. Dat is de bekende beperking van deze
  renderroute en niet nieuw, maar het geldt dus ook voor de proef van ronde 8.
- **De blinde vergelijking met twee juryleden is niet gedraaid.** Beide juryagents zijn
  afgebroken op een spend limit, halverwege deck A en deck B. De decks en renders staan klaar in
  `/home/user/werk-jury/` (A = nieuw leave-behind, B = het oude werksessie-deck, C = nieuw
  spreekdeck) en de ongewijzigde reviewer staat in
  `/home/user/werk-nulmeting/deck-visual-reviewer-ONGEWIJZIGD.md`. Dit is punt 1 van de
  definitie van klaar, dus die is nog niet gehaald.
- **Twee gaten uit de testronde zijn niet gedicht** (dezelfde spend limit): `fit_title.py` geeft
  nog geen waarschuwing wanneer titels van één en twee regels door elkaar lopen, en layout 22
  belooft in `sjabloon.md` nog kolomkoppen die te herkleuren zijn terwijl geen script dat kan —
  `set_text.py` biedt daar alleen `b="1"` en dat is sinds §9 nepvet.
- **Een tweede testronde ná de tellerreparaties** is niet gedraaid. De vier reparaties in
  `qa_tellingen.py` maken drie ontwerpbesluiten weer vrij die de bouwer onder dwang van de
  teller had genomen (labelmaat naar 12pt, badges naar 18pt, merkstreepje naar 1,60 in).
- ~~De vier goede voorbeeldslides zijn alleen als afbeelding beschikbaar, niet als bestand.~~
  **Gedaan.** Ze staan als `11` tot `14` in `assets/maatstaf/`, met per slide in `LEESMIJ.md`
  waarvoor ze de lat zijn en waarvoor niet.
- **Twee referenties ontbreken nog steeds als A/B op dezelfde inhoud:** recht tegen afgerond
  (kaarttaal) en 14 tegen 12pt body. Beide zijn nu besluiten van de skill zelf, dus ze staan niet
  op de keuzekaart — maar de bouwer kiest ze wel blind.
- **De drie dichtheden zijn niet naast elkaar gebouwd.** Testronde 2 uit het plan hierboven ging
  over twee registers; er zijn er nu drie, en of licht leave-behind werkelijk iets anders
  oplevert dan de twee andere is niet gemeten.
- **Het vragenvuur is niet in een echte bouw gebruikt.** Dat de poort werkt — acht antwoorden
  vóór de eerste regel tekst — is doctrine tot een bouwer het een keer heeft doorlopen.
- ~~De feitenvraag uit stap 1: gebruikt `maatstaf/04` werkelijk Montserrat SemiBold als
  aanhef?~~ **Beslecht.** Nagemeten op de PNG: het is werkelijk Montserrat SemiBold, dus de
  typografieregel overrulet een gemeten patroon en corrigeert geen verkeerde meting. Zie
  `vormentaal.md` §9 en `assets/maatstaf/LEESMIJ.md`.
