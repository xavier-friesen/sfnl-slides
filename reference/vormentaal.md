# Vormentaal

Dit is de maatstaf. Geen catalogus met patronen om uit te kiezen, en geen drempels waar een
script op afkeurt: wat een SFNL-slide goed maakt, geordend van meeste naar minste effect, zodat
je je eigen compositie eraan kunt toetsen.

Elke regel hieronder is nagemeten. Waar er een getal staat, komt dat uit de XML of de render
van de vijf decks die de blinde vergelijking wonnen, uit de deck die het niet haalde, of uit
de nulmeting van twee later gemeten decks — een werkdeck van 23 en een spreekdeck van 19
slides — en de vier reconstructies `11` tot `14` in `assets/maatstaf/`. Waar een regel eerder
verkeerd te lezen bleek, staat de verkeerde lezing er expliciet bij — dat is geen overbodige
uitleg, dat zijn fouten die daadwerkelijk gemaakt zijn.

`merktekens.md` staat ernaast: dertig merktekens uit elf bestaande SFNL-decks, met per stuk wat het
codeert en of de laag het al kan. Dat is geen catalogus om uit te kiezen maar het antwoord op de
vraag "wat kan ik eigenlijk tekenen" — de vraag die de bouwer stelt op het moment dat hij anders
een kaart met tekst maakt.

Lees dit één keer voordat je de eerste slide bouwt, samen met de veertien voorbeelden in
`assets/maatstaf/`. Die veertien zijn niet foutloos: `assets/maatstaf/LEESMIJ.md` zegt per
slide waarvoor hij de lat is en waarvoor niet.

---

## 1. Elke slide heeft één drager, en grote letter is daarvoor de uitzondering

De drager is het element dat de boodschap draagt: één getal, één verhouding, één kernbegrip,
één zin. Al het andere ondersteunt.

**Hiërarchie is het werk, maat is er maar één middel voor.** In de deck die het niet haalde is
het grootste element in de contentzone 19pt, en daardoor moet je hem gaan lezen om te weten
waar je begint. Maar de correctie daarop is doorgeschoten: toen de band 40 tot 60pt was, stond
er op élke slide een getal van 40pt, en een aandachtstrekker op tien van de tien slides trekt
niets meer. Grote letter werkt doordat hij zeldzaam is.

Dus: **ten hoogste één contentslide op drie draagt letter van 28pt of groter**, en op die
slide staat hij één keer. Kies daarvoor de slides waar de boodschap werkelijk een getal of een
verhouding ís — het resultaat, het bedrag, de doorlooptijd. Zet hem in Montserrat Light,
tussen 28 en 40pt, via `drager()` in `shapes.py`. **Op wit is die drager navy**: dat is de
huiskeuze, en de reden is te zien zodra je ze naast elkaar zet — een getal van 32pt in oranje
haalt 2,6 op wit en leest daardoor lichter dan de kop eronder, terwijl navy op 15,3 staat en het
gewicht draagt dat de maat belooft. Een accenthue op een drager is dus een besluit met een reden,
niet de gewone weg; op een volle vulling geldt §3 en kiest `tekst_op()`. Gotham Bold gebruik je nooit in de
contentzone, want dat is de titelletter en die erf je uit de layout.

**Op de andere slides is de drager niet groot maar zwaar en gekleurd.** Dit is waar het in de
praktijk misgaat, want de neiging is om te denken dat een slide zonder groot getal geen drager
kán hebben. Dat kan wel: een kolomkop van 18pt vette Montserrat Light in een accentkleur op wit
terwijl de rest navy is, één rij die als enige een volle kleur draagt, een rangnummer, of de
compositie zelf. Op de sterkste referentieslide zonder cijfers is de drager 18pt Montserrat
vette Montserrat in emerald tegenover 18pt in grapefruit, op wit — verder niets.

De toets die overal geldt: is de drager minstens **tweeënhalf keer de bodymaat** op diezelfde
slide, of onderscheidt hij zich in gewicht en kleur? Op een body van 14pt is dat 35pt, dus
midden in de dragerband. Loopt je hele slide op 14pt navy, dan is
er geen hiërarchie maar een verzameling.

De kneepoefening blijft de eindtoets: klein of onscherp bekeken moet de drager overblijven.
Blijven de pijltjes of de kadertjes over, dan is de navigatie luider dan de boodschap.

## 2. Vier maten per deck, en niet meer

Leg vóór de eerste slide vier getallen vast en gebruik overal die vier:

| rol | richting | waarvoor |
|---|---|---|
| **drager** | 28 tot 40pt Montserrat Light | het getal of begrip dat de slide draagt, op ten hoogste één slide op drie |
| **kop** | 18pt Montserrat Light, vet | kolomkop, kaartkop, rolnaam |
| **body** | 14pt Lato Light | alles wat gelezen wordt, en de sluitregel |
| **voetnoot** | 11pt | bron, eenheid, peildatum |

**Er zijn drie letters in een deck, en gewicht komt uit `b="1"`.** Gotham Bold in de titel,
Montserrat Light voor wat lósstaat en op zijn eigen regel begint — een kop, een label, een
rolnaam, een kolomkop, de drager — en Lato Light voor wat gelezen wordt. Meer familienamen
bestaan hier niet: een kop is Montserrat Light met `vet=True`, een aanhef binnen een
doorlopende regel is Lato Light met `vet=True` op een rest zonder. `run()` in `shapes.py`
weigert elke andere naam en `qa_text.py` meldt hem als `critical`.

Dat is een besluit van de eigenaar van 28 augustus 2026 en het draait de vorige regel om, die
`Montserrat SemiBold` en `Lato Semibold` als echte gewichten voorschreef en `b="1"` op een
light snede "nepvet" noemde. Wat er tegenover staat: in het bestand stonden vijf familienamen
voor een huisstijl die drie letters heeft, en drie van die vijf snedes reizen niet met de
plugin mee, dus ze werden op elke andere machine gesubstitueerd — de meting van `fit_title.py`
en `hoogte_van()` kon ze niet vinden en de render zette iets anders dan de naam beloofde. Wat
je inlevert: het gewicht is nu gesynthetiseerd en geen eigen snede. Beoordeel een
gewichtsverschil op de render dus niet als vormfout; wat je daar ziet is wat PowerPoint van
een light snede maakt. Gotham Bold staat alleen in de titel, en die schrijf je niet zelf — hij
komt uit de layout. Schrijf je hem toch in de contentzone, dan weigert `run()` het en
blokkeert `qa_text.py` de deck.

**Vier is het aantal, en de rest is afgeleid en geen keuze.** 12pt is de dichte variant voor
een kaartenrij van drie of meer of een tabelcel, en het is de vloer voor alles wat gelezen wordt.
De voetnoot van 11pt valt daarbuiten: dat is een eigen rol met een eigen maat, geen kleinere body.
14pt is het kapitaallabel — dezelfde maat als de body, maar in vette Montserrat Light en in
kapitalen, dus een andere rol en geen tweede bodymaat. En een sluitregel is bodymaat: een eigen
maat voor de laatste regel is precies het defect uit de afgekeurde deck, die drie
sluitregelmaten over vier slides had. 10pt gebruik je niet meer.

De body stond hier eerst op 16pt. Twee dingen wezen naar 14: de decks die werkelijk gemaakt zijn
zakten er ongemerkt allemaal naartoe, en op 16 vraagt de toets uit §1 — de drager is
tweeënhalf keer de body — een drager van 40pt, en dat is precies het plafond van de band. Op 14
valt die toets op 35pt en dus binnen de band. 14 is dus een besluit en geen concessie; wie er
16 van maakt, doet dat deckbreed en schrijft de reden erbij.

**Dezelfde rol houdt deckbreed dezelfde maat.** De afgekeurde deck had vier bodymaten en drie
sluitregelmaten over vier slides. Los is elke slide dan correct en naast elkaar leest het als
vier keer opnieuw beginnen. Er is géén maximum aan het aantal maten per slide — dat was een
smaakregel — maar er is wel één maat per rol.

Een kapitaallabel krijgt letterspatiëring: `spc="150"` tot en met 13pt, `spc="100"` daarboven.
Zonder spatiëring leest caps als geschreeuw in plaats van als label.

## 3. Kleur zit ook in de letter

Dit is het middel dat het meest ontbrak. In alle tien de referentieslides staat minstens één
accent als **tekstkleur op wit**: `WAT WERKT` in emerald naast `WAT KNELT` in grapefruit, een
getal van 32pt in oranje, een toelichtingsregel in de kleur van de rij waar hij bij hoort. De
afgekeurde deck had 31 gevulde vlakken en nul gekleurde letters.

Let op waarom die twee kolomkoppen in `maatstaf/04` twee verschillende hues dragen: het is een
tegenstelling, en de kleur zegt welke kant je leest. Dat is de reden dat er twee zijn, en niet
dat twee kolommen twee kleuren krijgen.

Een gekleurde letter is stiller dan een gevuld blok en zegt hetzelfde. Waar je een kopbalk van
een halve inch zou tekenen, kan de kop zelf de kleur dragen.

Vanaf welke maat dat mag, hangt af van het contrast op wit. Uitgerekend:

| kleur | op wit | mag dragen |
|---|---|---|
| navy | 15,3 | alles, ook een alinea |
| royal | 5,7 | alles, ook een alinea |
| grapefruit | 3,1 | een kop vanaf 18pt |
| oranje | 2,6 | displaymaat, of een kop vanaf 18pt die je niet hoeft te lezen om de slide te snappen |
| sky | 2,3 | idem |
| emerald | 2,0 | idem |

Daaronder is de tekst navy.

**Op een volle vulling:** wit op navy en royal. Op de lichte accenten staat navy, want daar
haalt wit 2,0 tot 3,1. Eén uitzondering, en die is nagemeten in de sterkste referentieslide:
op 40pt mag wit ook op emerald, oranje en sky, want daar leest het cijfer als vorm en niet als
tekst. Dat is een bewuste keuze die je op de render controleert, geen default — en 40pt is de
bovenkant van de dragerband, dus deze uitzondering geldt alleen voor de grootste drager in de
deck. Staat je drager op 28 of 32pt, dan is de tekst op een volle lichte hue navy.

**Oranje is het accent, en een tweede hue is een keuze per slide.** Dit is de andere kant van
hetzelfde en het gaat even vaak mis. Het accent naast navy is oranje: de huiskleur, en de enige
hue in het palet die als merk leest in plaats van als categorie. Dat staat vast en wordt niet
per deck opnieuw gekozen.

Wat je daarmee opgeeft, want dáár is dit besluit op te beoordelen: oranje haalt 2,6 op wit (de
tabel hierboven). Het accent kan dus nooit een gelezen regel dragen. Een accent in de letter is
displaymaat, of een kop vanaf 18pt die je niet hoeft te lezen om de slide te snappen; alles wat
werkelijk gelezen wordt blijft navy. Heb je een accent nodig dat óók een alinea draagt, dan is
dat royal (5,7) — een afwijking met een reden, en geen tweede default.

**En daaruit volgt een regel die op de render is nagemeten: nadruk zet je niet in de letterkleur.**
Zet je op een witte slide twee van de vier koppen in oranje en laat je de andere twee navy staan,
dan lezen de navy koppen sterker — 15,3 tegen 2,6 — en wijst de kleur precies de verkeerde twee
aan. Dat is gebouwd en gemeten: `proeven/01`. De vorm die het oplost staat ernaast in
`proeven/03`: alle koppen navy, en het element dat nadruk krijgt draagt een volle oranje chip met
navy tekst erin. Kleur in de letter blijft dus voor codering waar élk lid van de set een hue
krijgt (`maatstaf/04`); zodra een deel van de set navy blijft, hoort de nadruk in een vlak.

**Per slide mag er één tweede hue bij, en alleen als die iets codeert.** Twee kanten van een
afweging, kost tegenover baat, nu tegenover straks: `maatstaf/04` is precies dat, twee kolomkoppen
in twee hues omdat de kleur zegt welke kant je leest. De toets is één vraag, en je stelt hem per
kleur: **wat codeert deze hue, in één woord?** Kun je dat niet zeggen, dan gaat de kleur eruit en
blijft het oranje.

**Een sét hues is geen slidekeuze maar een deckbesluit.** Vier fasen, vier rijen, vier
categorieën die door de hele deck terugkomen: dan dragen drie of vier hues tegelijk informatie,
en dat neem je één keer voor de hele deck (skill, stap 1, besluit 3), met per hue in één woord
wat hij codeert. `maatstaf/11` en `12` zijn beide zo'n set — vier fasekaarten en vier
tabelrijen in royal, oranje, sky en emerald — en ze zijn dus geen bewijs dat vier hues per
slide mogen. Wie een set per slide opnieuw verzint, krijgt dezelfde rol in twee kleuren.

**Rol naar hue, één keer en dan vasthouden.** Heb je besloten dat kleur iets codeert, schrijf dan
op welke categorie welke kleur krijgt, en beslis er daarna niet meer over. Dezelfde rol die op
slide 4 sky draagt en op slide 11 emerald, betekent dat de kleur decoratie is geworden. De vaste
laag: grapefruit is kost of waarschuwing, emerald is baat, navy is structuur en totaal. Sky en
royal zijn vrij voor categorieën zonder eigen lading. Oranje codeert buiten een set niets — daar
ís hij het accent; binnen een deckbrede set is hij één van de hues en codeert hij wat de set hem
toewijst (`maatstaf/11`, `12`).

**En het grijs is geen grijs.** Het huisrecept voor een stil label — `tx1` met `lumMod 65000` —
rendert als `#5176A7`: contrast 4,67 op wit en 51 procent verzadiging, dus een vijfde blauw dat
naast sky en royal als lid van de set meedoet (`proeven/05`, met de vier trappen van datzelfde
slot in `proeven/LEESMIJ.md`). Er is ook geen trap die het oplost: `tx1` is `#233348` en elke
verlichting houdt de blauwzweem, van 27 procent verzadiging op lumMod 40 tot 52 op lumMod 80. Het
palet heeft dus geen neutraal grijs, en dat is een feit om mee te rekenen in plaats van te
omzeilen.

Wat een stil label dan is, en het hangt aan één vraag: staat de tekst in kapitalen?

- **Een kapitaallabel is `tx1` lumMod 65**, de kleur die `shapes.py` `"grijs"` noemt en die
  `sjabloon.md` onder Kleur als hét grijs documenteert. Caps krijgen spatiëring (§2), en
  spatiëring gaat op deze renderer niet samen met een alphakleur (§9), dus dit is de enige kleur
  die overblijft — en daarmee is het de default en niet de uitwijkplaats. Ja, het is een
  staalblauw en niet grijs; in een deck met sky of royal is het dus een vijfde blauw, en die prijs
  betalen we, want het alternatief is caps zonder spatiëring. `label()` zet hem met één argument:
  `label("MEETDOEL", 14, "grijs")`.
- **Een stille regel zonder kapitalen is navy op alpha 70** (`#625E8C`, contrast 6,0, verzadiging
  33 procent). Dit voegt geen hue toe: het is dezelfde navy, lichter. Daar staat geen `spc` op en
  dus is er geen klipping. Dit is de bronregel van §11, de eenheid, de peildatum.
- **Navy 100 procent** wanneer het label mag meedoen in de hiërarchie. Op 14pt naast een kop van
  18pt leest dat als een tweede kop, dus dit is de uitzondering en niet de weg eruit.

**Eén ding om te herzien zodra iemand ernaar kijkt.** De klipping is nagemeten op LibreOffice
24.2.7.2 (`proeven/06`) en niemand heeft het in echte PowerPoint getoetst. Klipt het daar niet,
dan is navy op alpha 70 mét spatiëring de betere default en vervalt het staalblauw voor labels.
Dat is één proef van vijf minuten in PowerPoint, en tot die er is, staat het hierboven.

Twee categorieën in dezelfde set krijgen nooit dezelfde hue. En één hue voor alles is het defect
uit de afgekeurde deck — maar let op de verkeerde lezing daarvan: dat defect was één lichte tint
over vier slides die vier verschillende dingen deden, niet één accent dat consequent één ding
betekent.

Waar het misgaat: twee kaarten naast elkaar die samen één werkstroom vormen — "opslaan" links en
"terugvinden" rechts — met een emerald kop op de een en een royal kop op de ander. Er is niets
tegengesteld aan die twee, de lezer leest ze achter elkaar en hoeft ze nooit te vergelijken. Twee
hues suggereren daar een tegenstelling die er niet is. Eén accent op beide koppen zegt hetzelfde
en leest rustiger.

De tweede hue per slide hoort in de outline, bij de slides waar kleur iets doet. Daar is hij te
overzien en te herzien voordat er iets gebouwd is; op de render is hij alleen nog te repareren.

## 4. Een container is bijna wit

Een lichte vulling maak je met `<a:alpha>` op de volle kleur, niet met `lumMod`. In de vijf
winnende decks komt `lumMod` geen enkele keer voor: navy staat op alpha 6000 tot 8000, de
accenten op 9000 tot 14000.

Dat is geen detail. Het recept `lumMod 20000 / lumOff 80000` levert een vlak dat één stap te
donker is en daardoor als eigen kleur meedoet in plaats van als achtergrond. Bij navy levert
het bovendien een blauwpaars vlak op, en daarvoor moest een apart lavendelverbod bestaan. Met
alpha is die uitzondering niet meer nodig.

De neutrale container is navy op alpha 7000: koel, kleurloos, en de default zodra er niets te
onderscheiden valt. Warmgrijs komt in geen enkele winnende deck voor; naast vol oranje leest
dat warme taupe als een niet-ingekleurd vlak.

Boven ongeveer 14000 wordt een container een kleur. Dat mag, maar dan is het een vlak dat iets
betekent en geen achtergrond meer.

## 5. Drie gevuldheden, en het contrast zit tussen de slides

Gemeten aandeel wit, tint en verzadigd per slide. De afgekeurde deck: 44 tot 53 procent wit, 42
tot 54 procent tint, 1 tot 7 procent verzadigd — op élke contentslide dezelfde band. Dat
middengrijs is precies wat een deck karakterloos maakt: nergens is iets leeg en nergens is iets
vol, dus er is geen contrast tussen de slides onderling. Dát is wat dit besluit moet voorkomen,
en niet "er moet ergens veel kleur staan".

**Drie gevuldheden, met de render en de meting eronder** (`assets/proeven/`, LibreOffice, 1921
px):

| gevuldheid | wat er staat | gemeten wit / verzadigd | referentie |
|---|---|---|---|
| **weinig accent** — de default | geen kaartvullingen: navy koppen op wit, een haarlijn per rij, en één vol oranje vlak precies waar de nadruk zit | 92 / 3 | `proeven/03` |
| **kaal** | ook dat vlak niet: alleen haarlijnen, kapitaallabels en kleur in de letter | 94 / 1 | `proeven/01` |
| **met kleur** | een set hues codeert de categorieën, in volle rijlabels of vier kaarten | 80 / 14 | `proeven/02` |

De default is **weinig accent**, en dat is een besluit van Xavier op de zes gerenderde varianten:
van de drie is dit de vorm die het beste leest, en de andere twee zijn er voor de slide die er
werkelijk om vraagt. Een deck is dus niet één gevuldheid — het is deze grondtoon met soms een
kale slide (een vraag, proza) en soms een gekleurde (een set categorieën die de lezer apart moet
houden). Een deck dat volledig in één gevuldheid staat is het middengrijs van de andere kant: het
gemeten spreekdeck stond op 83 tot 88 procent wit op élke contentslide en had nergens iets anders.


**Wat er níét meer wordt aangemoedigd: een vol vlak dat een kwart van de slide beslaat.**
`proeven/04` is precies dat — een oranje band van 12,52 bij 1,90 in, gemeten 25 procent
verzadigd, dus binnen de band die de referentiedecks laten zien — en hij is afgekeurd op de
render. De reden is dat het oppervlak groot is en bijna niets draagt: de vulling wordt het
luidste element op de slide terwijl de boodschap vier woorden is. De band van 20 tot 37 procent
blijft dus staan als méting van wat de winnende decks deden, maar hij is geen doel. Het contrast
tussen slides haal je door van gevuldheid te wisselen (92/3 tegenover 80/14), niet door een vlak
groter te maken.

**Reken vol oppervlak wel na, want de schatting zit er structureel naast.** Dit is het enige
besluit dat je tijdens het bouwen niet ziet. Op een deck dat met deze skill is gebouwd waren twee
slides als verzadigd aangewezen en maten ze 7 en 12 procent, en beide voelden tijdens het bouwen
als "die slide is de volle". Een slide is 13,33 bij 7,5 in, dus 100 vierkante inch, en één
procent verzadigd is ongeveer één vierkante inch vol:

| compositie | vol oppervlak | gemeten verzadigd |
|---|---|---|
| één band van 12,52 bij 1,90 in | 23,8 vierkante inch | 25 procent (`proeven/04`, afgekeurd) |
| één blok van 8,00 bij 2,50 in | 20,0 | 21 procent |
| vier rijlabels van 3,40 bij 0,98 in | 13,3 | 14 procent (`proeven/02`) |
| één chip van 1,50 bij 0,46 in per nadrukrij | 1,4 | 3 procent (`proeven/03`) |
| alleen lichte containers, geen vol vlak | 0 | 1 tot 2 procent |

De vullingssoort hoort hier en niet bij de kaarttaal (§8): welke vulling de standaard is, volgt
uit de gevuldheid die je hier kiest. Bij weinig accent is dat geen vulling plus één vol vlak, bij
kaal geen vulling, en bij met kleur de volle hue voor het label en de gekalibreerde tint voor het
paneel (§4).

Twee dingen om vast te houden. **Een kolom volle rijlabels voelt vol en is het niet**:
`proeven/02` meet 14 procent, want vier labels van 3,40 in halen samen de helft van wat een band
over de volle breedte haalt — dus verwacht daar geen verzadigde slide, en ga hem ook niet
opvullen tot hij er een is. En **een slide met alléén lichte containers** komt uit op 65 tot 69
procent wit met 30 tot 34 procent tint: dat is geen van de drie gevuldheden hierboven, en het is
de zone waar de referentie geen enkele slide heeft. Tint over de hele slide is dus een keuze om
te verantwoorden, geen default.

Meet het in dezelfde ronde als de render: `qa_tellingen.py --renders` geeft het aandeel wit, tint
en verzadigd per slide. Zonder die meting blijft dit besluit een intentie, en dat is nagemeten:
het middengrijs uit de afgekeurde deck ontstond niet doordat iemand besloot dat elke slide in het
midden mocht liggen.

**De uitzondering op dat alles is de uitspraakslide, en die is geen groot vlak op een gewone
slide.** Eén vraag of één bewering, gecentreerd op een vol vlak over de héle slide, verder niets:
geen titel, geen kaart, geen toelichting. Geoogst uit de kick-off Aidsfonds, waar hij midden in de
deck staat als een volledig oranje slide met één vraag tussen aanhalingstekens. Hij valt buiten de
regel hierboven omdat het bezwaar daar is dat een groot vlak bijna niets draagt terwijl er tekst
naast staat die het aandacht afneemt — hier is er niets naast, en de vulling ís de slide, net als
bij de divider en de outro die het sjabloon al heeft. Op een spreekdeck is dit de plek waar de
spreker een minuut stil kan vallen, en het kost nul woorden.

Bouw hem op een layout zonder titel (17) met één `drager()` — niet op layout 5, dat is het
citaat over een foto — en let op §3: op oranje is de tekst
navy tenzij hij op 40pt staat. Wat hij níét is: een oplossing voor een slide waar je geen vorm
voor kon vinden. Eén per deck, en alleen voor de vraag waar het werkelijk om gaat.


## 6. De compositie vult de zone, de blokken volgen de inhoud

De contentzone loopt van 1,93 tot 6,93 in. Het eerste element staat tegen 1,93 aan en de
onderkant van het laatste element ligt op 6,93, met een halve centimeter marge. De winnaars
bezetten die vijf inch voor meer dan 95 procent.

**En hier zit de val, want deze twee regels lijken elkaar tegen te spreken.** "De compositie
vult de zone" en "een blok is zo hoog als zijn inhoud" zijn beide waar, en de verkeerde lezing
is: maak de blokken hoger tot de zone vol is. Dan krijg je vier kaarten waarvan de onderste
helft leeg gekleurd vlak is, en op de render leest dat hetzelfde als een kale slide. Die fout
is gemaakt, op alle vier de contentslides tegelijk.

De juiste volgorde:

1. Reken uit hoe hoog de inhoud van elk blok is: som van de regelhoogtes plus de alineagaten
   plus de insets, en er komt niets bovenop. Een regel is 1,12 keer de puntgrootte.
2. Vergelijk met de zone. Blijft er ruimte over, dan is het antwoord **meer inhoud, grotere
   letters of een andere compositie** — niet een hoger blok.
3. Blijft er ruimte over die je bewust laat, verdeel die dan over de scheidingen en houd de
   blokken op hun inhoud. Ruimte tussen de blokken is compositie; ruimte ónderin een blok is
   een gat.
4. Meet de vulgraad: teksthoogte gedeeld door blokhoogte. **De norm is 0,9, en het restgat
   onderin het blok blijft onder 0,25 in.** Haalt een blok dat niet, dan kort je het in en
   sluit je de slide met een ánder element af.

**De meting rekent strakker dan de renderer zet, en dat maakt een middelmatig getal
verraderlijk.** `vulgraad` telt kale regelhoogtes; PowerPoint telt fontmetriek, alinearuimte
en de descender van de laatste regel mee. Wat gemeten 0,78 is, staat op de render dus met een
zichtbaar gat onderin — precies dat is nagemeten op een kolomblok dat op het getal was
goedgekeurd. Lees 0,78 niet als voldoende. En kijk boven 0,9 nog steeds naar de render: een
verhouding is schaalblind, 20 procent lucht in een kolom van vijf inch is een vol centimeter
dood gekleurd vlak en 20 procent in een blok van 1,2 in ziet niemand.

Vier korte definities vullen geen vijf inch in vier kolommen. In vier rijen over de volle
breedte doen ze het wel. Dat is wat "een andere compositie" betekent.

**Wat vullen niet is:** meer bullets. Wat het wél is: een blok dat de hoogte pakt omdat het
inhoud heeft, een drager met een getal, een tweede sectie, een afwegingsregel. Weet je niets te
bedenken, dan hoort de inhoud van deze slide bij de vorige.

## 7. Uitlijning is de goedkoopste kwaliteit die er is

**Naast elkaar betekent bovenaan uitgelijnd.** Staat een blok alleen, dan mag je de tekst
verticaal centreren en is de overgebleven lucht padding. Staat het in een rij of naast een
tweede blok, dan is de bovenkant vast: `anchor="t"` met dezelfde `tIns`, en de restlucht valt
onderaan. Centreren in een rij zet de eerste regels van de buren millimeters uit elkaar zodra
de een meer regels heeft dan de ander. Nagemeten gevolg van precies die fout: 0,13 in verschil
tussen twee kolommen die naast elkaar staan, goed zichtbaar en volstrekt onnodig.

**Eén linkerrand.** Alles wat onder elkaar staat begint op dezelfde x, en dan reken je de inset
mee en niet alleen de vormrand. Een sluitregel met een andere inset dan de blokken erboven
lijnt met niets uit. Let op: een `roundRect` snijdt de tekst extra in, dus naast een `rect`
verschuift de linkerrand zichtbaar. Toets het op de render als één ding: staat de linkerkant
van álle tekst op één lijn?

**Een label boven of naast een getal is één regel.** Slaat het om terwijl de buurlabels één
regel zijn, dan zakt het getal eronder mee en staat de rij niet meer op één baseline. Kort het
label in of geef alle labels dezelfde vaste hoogte. Wil je getallen echt op één lijn, geef ze
dan een eigen vak met voor elke kaart dezelfde y, dezelfde hoogte, dezelfde maat, `anchor="t"`
en `tIns="0"`.

**Draagt afstand informatie, dan staat hij op schaal.** Op een tijdlijn is de x-positie van een
moment `0,48 + 12,52 × (t − t0) / (t1 − t0)`. Botsen twee labels, dan wijken de teksten uit
naar twee rijen — nooit de posities. Vier banden onder elkaar zijn geen tijdlijn, want dan staat
elke stap even ver van de vorige.

## 8. Lijnwerk is het lichte register

Een deck die alleen gevulde vlakken kent, heeft één register. De winnaars gebruiken 11 tot 39
lijnelementen per deck.

**Een lijn om een kaart heeft dezelfde hue als de vulling.** Een witte kaart met een lijn van
1pt in emerald is een kaart; dezelfde kaart met een grijze of navy rand is een Word-tabel. Dit
is de best gevalideerde vormregel die er is: op één referentieslide staat hij drie keer, elke
kolom met een 1pt lijn in exact de hue van zijn eigen vulling. Een vlak van 9 procent vulling
heeft die lijn nodig om als kaart te lezen in plaats van als vlek.

**Een streep scheidt lichter dan een vlak.** Onder een label, tussen twee blokken, boven een
sluitregel.

**Eén kaarttaal per deck.** De hoekvorm van je eerste kaart geldt voor elke kaart. Afgerond of
recht is vrij; halverwege wisselen is het defect dat het snelst opvalt, ook als beide varianten
los goed zijn. En dat is gebeurd: drie slides afgerond, de vierde recht.

Beide varianten staan uitgewerkt in de maatstaf, dus dit besluit heeft een beeld aan elke kant.
`maatstaf/11` is afgerond met per kaart een 1pt-haarlijn in de eigen hue — vier losstaande
kaarten die elk een fase dragen. `maatstaf/12` is recht en zónder haarlijn: vier tabelrijen,
waar het volle rijlabel de rij al begrenst. Dat is de nuance die het onderscheid draagt: de
haarlijn hoort bij een kaart die los op wit staat, niet bij een rij in een tabelband. Kies je
recht en staan er losse kaarten op wit, dan komt de haarlijn er dus alsnog bij.

**Eén hoekradius, absoluut.** Een `roundRect` zonder expliciete `adj` krijgt PowerPoints default
van 16,67 procent van de korte zijde. Dat betekent dat een blok van 1 in hoog een pil wordt en
een blok van 2,5 in een nette kaart — vier verschillende radii in één deck zonder dat iemand er
iets aan koos. Kies één radius in inch, ongeveer 0,08 tot 0,12, en reken de `adj` per vorm
terug.

**Elk gekleurd vlak draagt inhoud.** Een balk, streep of vlak dat alleen kleur is, gaat eruit.
De enige uitzondering is de geërfde oranje dash, en die is merk.

## 9. Zetting

Een eigen vorm erft geen regelafstand en geen alinea-afstand. Zet beide, en deckbreed hetzelfde.

- **Regelafstand** 112 procent op lopende tekst. De winnaars staan op 110 tot 115; Lato Light op
  enkel wit staat te dicht. Een label of getal van één regel krijgt geen regelafstand.
- **Alinea-afstand** 6pt in een kaart of tabelcel, waar de kaartrand het scheidingswerk al doet.
  In een prozakolom ongeveer een hele regelhoogte, want daar is de witruimte de enige scheiding
  tussen twee beweringen.
- **Regellengte** maximaal ongeveer 95 tekens. Een alinea van meer dan twee regels is daarom
  niet breder dan ongeveer 10 in; de volle 12,52 is voor één regel. De banden in de afgekeurde
  deck liepen 111 tot 121 tekens, en dat is de belangrijkste reden dat ze lezen als tekst die
  over was in plaats van als een uitspraak.
- **Eén familie per regel, en het gewicht komt uit `b="1"`.** Een aanhef van twee tot vier
  woorden haalt twee hiërarchieniveaus binnen één tekstregel, zonder tweede kolom en zonder
  tweede vak. Staat die aanhef binnen een doorlopende regel, dan is hij **Lato Light met
  `vet=True`** op een rest in Lato Light zonder, op dezelfde maat. Montserrat blijft voor wat
  **lósstaat en op zijn eigen regel begint**: een kop, een kapitaallabel, een rolnaam, een
  kolomkop — ook daar Montserrat Light met `vet=True`, en de drager is dezelfde snede zonder
  gewicht. `aanhef()` en `label()` in `shapes.py` doen dit; `para()` weigert een alinea met
  een Montserrat- én een Lato-run, en `run()` weigert elke familienaam die geen van de twee
  is.

  **Hier stonden eerst echte snedes, en dat is per 28 augustus 2026 omgedraaid.** De regel
  was: de aanhef is `Lato Semibold`, de kop is `Montserrat SemiBold`, en `b="1"` op een light
  snede is nepvet omdat de renderer zelf kiest wat hij ervan maakt. Die redenering is niet
  fout — het gewicht ís nu gesynthetiseerd — maar ze leverde vijf familienamen op in een
  huisstijl die drie letters heeft, en drie van die vijf snedes reizen niet met de plugin mee.
  Nagemeten in `merk.md` §2: `assets/documenten/fonts/` draagt Lato Semibold niet, dus de
  meting kon hem niet vinden en de render substitueerde hem. Het besluit van de eigenaar is
  drie letters, en de prijs is het gesynthetiseerde gewicht. Gevolg voor de beoordeling: een
  aanhef die "niet echt zwaarder" wordt is geen bevinding meer maar de bedoelde uitkomst.

  **De verkeerde lezing, en die kwam uit dit document.** Hier stond eerder dat de aanhef
  Montserrat SemiBold moest zijn, en `shapes.py` beriep zich daarvoor op een meting in
  `maatstaf/04`. Die meting is nagerekend en ze is juist — `04` zet werkelijk Montserrat
  SemiBold in een Lato Light-alinea. Op de PNG van die slide, 1920 px bij 144 dpi: `Vaste` in
  de aanhef is 92 px breed bij een kapitaalhoogte van 23 px, verhouding 4,00, en dat is exact
  Montserrat SemiBold (Lato Semibold zet 3,35); `noemen` in de rest is 106 px bij een
  x-hoogte van 17 px, verhouding 6,2, en dat is Lato Light (Montserrat Light zet 8,0). De
  regel hierboven overruled dus een gemeten patroon uit een winnende deck, en niet een
  verkeerde meting. De reden is dat twee families binnen één tekstregel twee letterbouwen en
  twee x-hoogtes op dezelfde maat naast elkaar zetten, en dat leest als een zetfout in plaats
  van als hiërarchie. **Voor dít aspect is `assets/maatstaf/04` geen lat meer.** Voor de rest
  van die slide blijft hij dat wel: twee hues voor een tegenstelling, proza als exhibit, de
  bronregel per kolom. Dat staat ook in `assets/maatstaf/LEESMIJ.md`, want wie de PNG's
  bekijkt leest dit document niet noodzakelijk.

- **Geen hoge punt als scheiding binnen een regel.** `tekst tekst · meer tekst` is de vorm
  die ontstaat als twee feiten op één regel worden geperst. Twee feiten zijn twee regels,
  twee cellen of twee elementen. Dit geldt in de contentzone, in een label en in een
  bronregel. Het middenpunt is geen scheidingsteken maar een noodgreep om iets dat niet paste
  alsnog te laten passen, en de lezer moet het uit elkaar halen. Een bronregel met een bron,
  een eenheid en een peildatum is drie feiten: zet ze onder elkaar, of laat er twee weg.
- **Insets** 0,2 links en rechts en 0,15 boven en onder op een vak met vulling; 0 op een
  tekstvak zonder vulling, zodat de tekst met de vakrand uitlijnt en dus met de rest van de
  kolom.
- **Centreren** tot ongeveer 3 in breed, daarboven links uitgelijnd.
- **Cursief mag, en alleen op een korte, niet-lopende regel**: een datum, een eenheid, een
  bron, een scenario-aanduiding. Eén regel, ten hoogste 48 tekens, en niet als alinea. Voor
  lopende tekst en voor alles van meer dan één regel blijft cursief verboden — een cursieve
  alinea leest langzamer en er is een goedkoper middel voor nadruk, namelijk kleur (§3).
  `run(..., cursief=True)` in `shapes.py` laat precies die korte regel door en weigert de
  rest.

  **Hier stond eerder alleen "Cursief niet", en dat was te absoluut.** Het origineel van
  `maatstaf/11` zet per fasekaart een cursieve datumregel in de hue van de kaart, en die
  regel werkt daar juist doordat hij niet gelezen maar herkend wordt: hij zegt "dit is
  wanneer", niet "lees mij". Met het verbod zoals het er stond was die slide niet met de
  eigen laag te bouwen — de reconstructie schreef er een eigen run omheen, en dan is de
  regel geen regel meer maar een obstakel. Het verbod gold dus voor lopende tekst en is nu
  ook zo opgeschreven. Dit is een besluit, niet een meting.
- **`noAutofit` op elk vak dat je zelf schrijft.** Past de tekst niet, dan wordt het vak groter
  of de tekst korter, nooit het font kleiner. Eén vak met 90 procent schaling haalt een hele rij
  uit de lijn.

Drie regels over de tekens zelf. Ze stonden hier niet en kwamen uit de opschoningsroute
(`sfnl-deck-check`), die ze mechanisch toepast; ze horen hier omdat ze over zetting gaan en niet over
opschonen. De titel en de subtitel staan los daarvan in `voice.md` (kapitalen, geen punt, geen
uitroepteken; de subtitel in zinsvorm).

- **Eindinterpunctie volgt de vorm van de regel.** Een losse regel, een label, een kolomkop en
  een lijstitem eindigen zonder punt; een volle zin in een prozablok houdt zijn punt. Een
  vraagteken blijft altijd staan en een afkorting met punten (`o.a.`) wordt nooit afgeknipt. Wat
  hier het zwaarst weegt is niet welke van de twee je kiest maar dat de deck het overal hetzelfde
  doet: vier kaarten waarvan twee met en twee zonder punt is dezelfde soort fout als twee
  kaartvormen in één deck (§8).
- **Een slash die twee begrippen scheidt krijgt een spatie aan beide zijden**: `zorg / welzijn`,
  niet `zorg/welzijn`. Een samentrekking (`en/of`), een breuk (`3/4`), een eenheid (`km/u`) en een
  pad in een URL houden hun slash zonder spaties.
- **Een reeks krijgt een en-streepje**: `2023–2025`, niet `2023-2025`. Het koppelteken verbindt
  een samenstelling, het en-streepje spant een bereik, en het gedachtestreepje is er voor een
  tussenzin — die laatste gebruik je op een slide vrijwel nooit (`voice.md`, Humanizer-kern 8).

## 10. Herhaling zit in de geometrie, niet in de vulling

Zet achter elke slide de plattegrond in vier woorden — "drie kaarten, open onderkant", "tabel
plus conclusie", "vier rijen" — zet die onder elkaar en tel ze. Komt één plattegrond meer dan
twee keer voor, of staan er twee gelijke naast elkaar, dan is er een slide die opnieuw ontworpen
moet worden. Doe dat in de outline; na het bouwen kost het een herbouw van de contentzone.

**Een band van 12,52 bij 1,25 in met één regel erin is dezelfde vorm, of hij navy, oranje-tint
of warmgrijs is.** Dat is de val waar de afgekeurde deck in liep: de bouwer dacht de herhaling
te doorbreken door de vulling te wisselen en zette drie keer hetzelfde blok neer. Ten hoogste
één zo'n band per vier slides — en dat maximum alléén is aantoonbaar niet genoeg: een later
gemeten deck zette veertien banden op achttien contentslides, één band per 1,2 slide, terwijl
deze regel er toen al stond. De regel werd gelezen en niet gevolgd, omdat er op elke slide iets
moest afsluiten en de band het enige afsluitmiddel was dat de bouwer paraat had. Daarom staan
de vier andere afsluiters hier uitgeschreven, want dit is de plek waar je er een nodig hebt:

- **De laatste rij is zelf de conclusie.** In een tabel of een rij blokken is de onderste rij
  de uitkomst — het totaal, het advies, de laatste stap. Dan sluit de inhoud de slide af en
  hoeft er niets onder.
- **Eén cel of kaart draagt de volle kleur.** In een rij gelijke elementen krijgt het element
  waar het om gaat de volle vulling of de gestreepte nadruk (`maatstaf/11`); het oog eindigt
  daar en de conclusie staat al op de slide.
- **De sluitregel op wit.** Eén regel zonder vulling, aanhef in vette Lato Light, hooguit een
  streep erboven (§8). Zegt precies wat de band zegt, zonder het vlak.
- **Er valt niets af te sluiten.** In titelmodus A draagt de titel de bewering al; een slide
  die zijn boodschap boven heeft staan hoeft haar onderaan niet te herhalen. De compositie
  eindigt waar de inhoud eindigt en vult de zone met inhoud (§6), niet met een band.

De band die dan overblijft is de slide waar de conclusie werkelijk een eigen zin is die nergens
anders op de slide staat — op `maatstaf/11` komt hij precies één keer voor, onder het
beslismoment.

**Bedoelde herhaling is geen eenvormigheid, en dat onderscheid ontbrak hier.** Drie keer
dezelfde plattegrond zonder reden is het defect waar deze paragraaf over gaat. Maar drie keer
letterlijk hetzelfde beeld met één element dat verschuift, is een middel — en een sterk middel.
Geoogst uit de kick-off Baanbrekers: driemaal dezelfde verandertheorie-canvas, met daarover een
gestreept kader dat één keer om de linkerhelft ligt, dan om het middendeel, dan om de rest, elk
met zijn eigen label (`WP 1`, `WP 2 — SESSIE 1`, `WP 3`). De lezer orienteert zich één keer en
volgt daarna alleen het kader. Drie verschillende composities voor dezelfde drie stappen hadden
hem drie keer laten zoeken.

Het verschil is te benoemen en dus te toetsen: **verschuift er één element terwijl de rest
letterlijk gelijk blijft, dan is de herhaling het middel; verschilt de inhoud terwijl de
plattegrond gelijk blijft, dan is de plattegrond de luiheid.** Bouw het eerste met
`duplicate_slide.py` en verplaats het kader met `place_shapes.py`, zodat de slides werkelijk
identiek zijn en niet bijna.

Variatie zit niet in het layoutnummer. Zes contentslides op layout 19 met zes verschillende
composities is goed. Maar kies de layout ook niet standaard: een tweeluik is layout 22, waar de
kolomkoppen geërfde placeholders zijn waarvan je de doos overneemt en de kop zelf zet, want
`set_text.py` kent geen kleur (`sjabloon.md`, Welke layout waarvoor); doorlopende tekst is
20; een schema over de volle hoogte zonder titel is 17. Vier contentslides op 19 achter elkaar
is de eenvormigheid waarop de vergelijking verloren is.

## 11. Een cijfer draagt zijn herkomst mee

Eén regel van 11pt Lato Light in navy op 70 procent dekking, zonder vulling, insets 0, direct
onder de doos waar hij bij hoort en over de breedte van die doos — niet onder de slide. Twee
beelden op één slide krijgen twee bronregels.

**Ook hier geen hoge punt.** `Bron: monitor 2024 · n = 118 · peildatum 1 juli` is drie feiten
op één regel; dat is twee regels of het is er één met minder erin (§9).

Dat is geen kleine letter en geen verplichting. Het is de reden dat de lezer het cijfer
gelooft, en het is de plek waar de eenheid en de peildatum staan, want die hoeven niet in de
grafiek. In de afgekeurde deck staat geen enkele bronregel; in de referentie staan ze onder elk
cijferblok.

Getalopmaak: komma voor decimalen, punt voor duizenden, euroteken met een spatie, en de eenheid
in dezelfde run als het getal — `€ 1,04 mln` en niet `1,04` met `mln` in de toelichting. Staat
er iets op de getalpositie, dan is het een getal met een eenheid; een maand, een naam of een
voorwaarde gaat naar de regel eronder.

## 12. Vorm volgt de inhoud, niet het raster

Vraagt de inhoud om een volgorde — een proces, een route, een fasering — dan is het geen
bulletlijst maar een schema. Vraagt hij om een verhouding, dan is het geen rij tekstvakken maar
een verdeling. Is het een reeks over tijd of een vergelijking van meer dan zes categorieën, dan
is het een native grafiek; handgetekende staafjes zijn dat niet. Een financiële reeks van drie
perioden of meer maal twee grootheden of meer is een tabel, want een financiële lezer kan proza
niet vergelijken. Draagt een deck cijfers, dan zit er minstens één grafiek, tabel, schema of
verdeling in.

**Meter of chip: graduatie tegen categorie.** Twee merktekens die op elkaar lijken en iets
anders zeggen. De puntenmeter uit `maatstaf/12` — drie punten waarvan er twee vol staan — codeert
een gráádmeter, en de kunst is dat hij grof is: drie punten zeggen "zwaar, en dat is geen
precisie". De chip codeert een categorie: een klein gekleurd blokje met één woord erin, zoals de
derde kolom in de check-in die per rij `GELIJK`, `ANDERS` of `ALLEEN GZ` draagt. Beide vervangen
een woord door een vorm, maar een chip in een reeks suggereert een ordening die er niet is, en
een meter voor een categorie suggereert een graad die er niet is. Vraag dus: kan het meer of
minder zijn (meter), of is het dit of dat (chip)?

**Het aantal volgt uit de inhoud.** Heb je twee items en dacht je aan drie kaarten, dan wordt
het een rij van twee. Geen derde kaart met een verzonnen regel en geen halflege kaart. Sjabloon-
slots zijn geen bronitems.

**Proza mag de exhibit zijn.** Twee goed gezette kolommen met gekleurde koppen, aanhefruns en
een sluitregel is een compositie, geen tekstslide. Dat is de sterkste referentieslide die er is.

### Wanneer een vorm een zin vervangt

De toets is één vraag: **staat er in de zin een verhouding, een tijdstip of een afstand?** Dan
hoort dat getal in de geometrie en niet in de tekst, want een positie lees je in één blik en een
zin moet je uit elkaar halen.

Drie voorbeelden, alle drie nagemeten in `assets/maatstaf/`:

- **Een afstand.** `13` zet vijf projecttypes op een as van 1 tot 4, met per type twee punten en
  de lijn ertussen. De zin die dat vervangt luidde: "bij zorgprocesprojecten wordt gemiddeld
  doel 2 benoemd terwijl er tot doel 3,5 wordt gerapporteerd". Vijf van die zinnen naast elkaar
  is niet te vergelijken; vijf lijnstukken op dezelfde as is één blik. Het gat tússen de twee
  punten is de boodschap, en dat gat bestaat alleen als de posities op schaal staan.
- **Een verhouding.** `12` zet naast elk rijlabel een puntenmeter van drie punten, waarvan er
  twee vol zijn en één half. Dat vervangt "zwaar, maar iets minder zwaar dan sturen" — een
  bewering die in proza een vergelijking vraagt die de lezer zelf moet maken.
- **Een tijdstip.** `11` zet vier fasen als vier kaarten met een datumregel per kaart. Daar is
  de vorm bewust géén tijdlijn: de fasen zijn even lang en volgen elkaar op, dus er is geen
  afstand te coderen. Vier kaarten is dan eerlijker dan een as, want een as zou een verschil
  in tijd suggereren dat er niet is.

**Positie op schaal is de kern, en het is de enige plek waar het oog de fout niet repareert.**
Draagt afstand informatie, dan staat hij op schaal (§7): de x van een moment is
`0,48 + 12,52 × (t − t0) / (t1 − t0)`, en `schaal()` in `shapes.py` geeft die functie. Alles
wat op een slide misstaat kun je op de render zien en verschuiven — behalve een punt dat op de
verkeerde plek staat, want dat ziet er precies zo goed uit als een punt dat goed staat. Vier
banden onder elkaar met "2024", "2025", "2026" en "2029" erin lezen als een tijdlijn en zijn
het niet.

**De verkeerde lezing, en die is voorgekomen.** "Positie draagt de informatie" werd gelezen als
"dus zet de labels waar ze passen". Op de reconstructie van `13` liep het aslabel `4 SYSTEEM`
1,2 in buiten de slide, en de eerste reflex was om de tik naar links te schuiven zodat het
label paste. Dan is de as niet lineair meer en is het beeld een leugen. De regel is andersom:
het punt staat op schaal en blijft daar, het label wijkt — het schuift binnen de zone
(`binnen()`), het lijnt rechts uit, of het gaat naar een tweede regel. Botsen twee labels, dan
wijken de teksten en nooit de posities.

**Een merkteken is geen versiering.** Een punt, een meter, een pijl, een streep: elk codeert
één ding, en de toets is dezelfde als bij kleur (§3) — wat codeert dit teken, in één woord? Is
het antwoord "de volgorde" of "het gewicht", dan staat het er goed. Is het antwoord "het maakt
de slide levendiger", dan gaat het eruit, net als elk gekleurd vlak dat alleen kleur is (§8).
Blijven bij de kneepoefening de pijltjes over in plaats van de boodschap, dan was het
navigatie.

## 13. Tekstlast volgt de dichtheid, en het defect is tekst waar een vorm had gemoeten

Er is geen deckbreed maximum aan woorden per slide. `qa_tellingen.py` telt de woorden en
rapporteert ze bewust zonder oordeel, en deze paragraaf draait dat niet stilletjes om in een
norm: de getallen hieronder zijn richtwaarden met de meting eronder, geen drempels. Wat er wél
is: één dichtheidsbesluit per deck, en één toets per slide.

**Het dichtheidsbesluit: spreekdeck, licht leave-behind of leave-behind.** Dit is een ander
onderscheid dan de drie gevuldheden van §5 — dat gaat over kleurbezetting per slide, dit over
woorden per deck — en het is het eerste deckbrede besluit in het vragenvuur (skill, stap 1).

Drie waarden, met per waarde de meting eronder. De getallen zijn woorden per contentslide
inclusief titel, en het zijn indicaties: ze zeggen welk register je hebt gekozen en niet hoeveel
woorden er op een slide moeten staan. Ze werken dus twee kanten op. Past het verhaal in minder,
dan is het minder — onder de band zitten is geen dunne slide maar een slide die klaar is, en
opvullen tot de band gehaald is, is het defect uit §6 in tekstvorm. Vraagt het verhaal meer, dan
is het meer: een bewering schrappen om onder een richtwaarde te blijven levert het argument in
voor de telling. De toets staat verderop in deze paragraaf en gaat over de vorm, niet over het
aantal.

| dichtheid | indicatie | gemeten aan |
|---|---|---|
| spreekdeck | 50 tot 60 | `maatstaf/13` (50) en `14` (59) |
| licht leave-behind | 90 tot 110 | `maatstaf/12` (99) |
| leave-behind | 120 tot 145 | `maatstaf/11` (141), `04` (proza in twee kolommen) |

- **Spreekdeck** — er praat iemand bij en het deck gaat daarna niet mee, dus de slide is de
  achtergrond bij dat verhaal. Wat de spreker zegt hoort niet op de slide; daar staat alleen wat
  het verhaal draagt, en de toelichting blijft bij de spreker in plaats van ergens in het
  bestand. Dit is het strakke eind. `13` en `14` zijn een plot op schaal en een schema, en beide vullen de zone (§6), want
  weinig woorden is geen lege slide.
- **Licht leave-behind** — leesbaar zonder spreker, maar met één boodschap per slide en zonder
  uitgeschreven spreektekst. Dit register is er bijgekomen omdat de meting het aanwees: het
  gemeten spreekdeck zat op gemiddeld 85 woorden per contentslide met een piek van 101, en dat
  is voor een spreekdeck te dicht terwijl het voor een leave-behind te dun is. Het was geen
  mislukt spreekdeck maar een register zonder naam. `12` is de vorm die erbij hoort — een tabel
  met verzadigde rijlabels, waar elk woord in een cel staat en de toelichting per rij één regel
  is. Bij twijfel tussen de twee andere is dit de keuze.
- **Leave-behind** — de slide moet zonder spreker te lezen zijn (`voice.md`, de bindende
  toets), en mag dus dicht zijn. Een prozaslide met twee goed gezette kolommen is hier een
  volwaardige exhibit; `maatstaf/04` is precies dat. `11` — vier fasekaarten van ongeveer
  dertig woorden elk — is van de vier reconstructies de sterkste. 141 woorden is dus geen
  defect.

**De dichtheid geldt deckbreed, en een slide die ervan afwijkt heeft toestemming nodig.** Eén
slide dichter of dunner dan de rest is geen vormfout op zichzelf — een tabel is nu eenmaal
dichter dan een plot — maar het besluit per slide opnieuw nemen is precies waar de gemeten deck
op stukliep. Wijkt een slide bewust af, dan staat dat in de outline bij die slide, en het mag
alleen als de gebruiker in het vragenvuur heeft gezegd dat dit mag (skill, stap 1).

**De toets per slide is niet "hoeveel woorden" maar "staat hier tekst waar een vorm had
gemoeten".** De hoogste meting, 255 woorden op één slide, was vier kolommen met per kolom
dezelfde twee vetgezette labels — acht keer `Hoe het gaat` en `Wat er nu gemeten wordt`.
Repeteert dezelfde aanhef op elke kolom, dan zijn die labels een rijkop en is de vorm een
tabel (§12): dáár zit het defect van die slide, niet in het aantal woorden. Dezelfde toets van
de andere kant: `11` haalt zijn 141 woorden doordat elk woord in een vorm staat — per fase een
kaart met een badge, een datumregel en één alinea.

**De verkeerde lezing ligt voor de hand: "minder woorden".** Wie uit de meting van 255 tien
slides van negentig woorden maakt, heeft het defect verplaatst en niet opgelost — versnipperen
is precies de reden dat er op deze telling geen drempel staat. De reductie die wél telt is de
vorm herzien: een tabel, een schema, of twee slides met elk één boodschap, met per geschrapte
bewering een reden die op te schrijven is.

---

## 14. Een icoon teken je zelf, en het draagt iets

Er is geen iconenbibliotheek in deze plugin en die komt er niet. Geen gedownloade set, en ook
niet de iconengalerij van PowerPoint: die staat niet in het sjabloon en sleept een andere
lijnentaal mee dan de merktekens uit §12. Wat er wél is: `icoon()` in `shapes.py`, dat een eigen
icoon tekent op een raster van 24 bij 24 eenheden en de discipline afdwingt — één schachtdikte,
één hue, geen vulling, ronde uiteinden, alles binnen het vierkant, en het geheel als één groep.
De zes in `proeven/09` zijn zo getekend: document, mensen, kringloop, euro, doel, klok.

**Eerst de vraag die vóór het tekenen komt: draagt het icoon iets wat de tekst niet al draagt?**
`proeven/10` zet dezelfde drie stappen twee keer neer, boven met een icoon per rij en onder
zonder, en de onderste helft is de rustigere van de twee: naast een kop die `VERZAMELEN` zegt
voegt een poppetje niets toe. Een icoon verdient zijn plek in drie gevallen:

- **het codeert een soort** die de lezer moet vergelijken — geld tegenover tijd tegenover mensen,
  in een set waar dat onderscheid het punt is
- **het markeert iets dat terugkomt** over meerdere slides, zodat de lezer het herkent zonder de
  kop te lezen
- **het vervangt een zin in een schema**, waar een woord de vorm zou breken

Buiten die drie is het decoratie, en decoratie valt onder de regel van §8: een gekleurd vlak dat
alleen kleur is gaat eruit, en dat geldt net zo voor een lijntekeningetje. De kneepoefening van §1
is ook hier de toets — blijven de icoontjes over in plaats van de boodschap, dan waren ze
navigatie.

**De zetting, nagemeten in `proeven/09`:**

| wat | waarde |
|---|---|
| raster | 24 bij 24 eenheden; 12 is het midden, 8 en 16 de derden, 4 de marge |
| schachtdikte | 1,5pt. 1,0 leest als een schets, 2,0 gaat met de kop van 18pt concurreren |
| maat naast een kop van 18pt | 0,72 in; in een rij 0,60; als drager van de slide 1,10 |
| ondergrens | 0,44 in — daaronder lopen de lijnen in elkaar en is een streep of een label beter |
| bovengrens onderdelen | 12; daarboven is het een tekening en hoort het in `sfnl-infographic` |
| vulling | geen, met één uitzondering: één gevulde stip als het centrum iets betekent |

**De hue: navy, tenzij de kleur iets codeert.** Een icoonlijn van 1,5pt in oranje haalt 2,6 op wit
(§3) en leest daardoor als een suggestie in plaats van als een teken; op `proeven/10` staan de
drie iconen in oranje en ze zijn merkbaar lichter dan hun eigen kop ernaast. Draagt de rij een
hue, dan mag het icoon die hue hebben — dan is het één element in dezelfde codering. Op een
volle navy of royal vulling is het icoon wit.

**Eén meting die een ronde kostte, en die generiek is voor gebogen vormen:** een boog met een
pijlkop erop moet je uitrekenen, niet op het oog plaatsen. Het eindpunt van een boog om
`(cx, cy)` met radius `r` op hoek `graden` is `(cx + r·cos, cy + r·sin)` — met de klok mee, nul
naar rechts, y naar beneden — en de kop staat op de tangens, 90 graden terug. De eerste
kringloop had zijn kop op geschatte coördinaten en die zweefde los van de boog: op de render
duidelijk te zien, in de code niet.

---

## Wat hier niet staat

Geen patroonnamen. Geen verplichte afsluitband. Geen maximum aantal tekstgroottes per slide.
Geen tabel met kaartbaselines op vaste y-waarden. Geen minimumafstand die een script afdwingt.

En geen belofte dat dit genoeg is. Meerdere van de veertien voorbeelden in `assets/maatstaf/`
dragen zelf een defect — `LEESMIJ.md` somt ze per slide op. De drie oudste gevallen: op `01` en `06` staat het grote getal over zijn eigen label, en op `01` is de
onderste helft van de vier kaarten leeg. Kijk daar naar de vier hues en naar de brede panelen
eronder, niet naar de kaarthoogte. En op `04` staan Montserrat SemiBold en Lato Light in
dezelfde alinea — nagemeten, zie §9 — wat sinds die paragraaf niet meer mag. Kijk op `04` naar
de twee hues voor een tegenstelling, naar proza als exhibit en naar de bronregel per kolom, niet
naar de letter van de aanhef. De lat is de compositie van die slides, niet hun uitvoering.

De render blijft het enige oordeel over de vorm.
