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

`merktekens.md` staat ernaast: tien merktekens uit bestaande SFNL-decks, met per stuk wat het
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
tussen 28 en 40pt, via `drager()` in `shapes.py`; Gotham Bold gebruik je nooit in de
contentzone, want dat is de titelletter en die erf je uit de layout.

**Op de andere slides is de drager niet groot maar zwaar en gekleurd.** Dit is waar het in de
praktijk misgaat, want de neiging is om te denken dat een slide zonder groot getal geen drager
kán hebben. Dat kan wel: een kolomkop van 18pt Montserrat SemiBold in een accentkleur op wit
terwijl de rest navy is, één rij die als enige een volle kleur draagt, een rangnummer, of de
compositie zelf. Op de sterkste referentieslide zonder cijfers is de drager 18pt Montserrat
SemiBold in emerald tegenover 18pt in grapefruit, op wit — verder niets.

De toets die overal geldt: is de drager minstens **tweeënhalf keer de bodymaat** op diezelfde
slide, of onderscheidt hij zich in gewicht en kleur? Loopt je hele slide op 16pt navy, dan is
er geen hiërarchie maar een verzameling.

De kneepoefening blijft de eindtoets: klein of onscherp bekeken moet de drager overblijven.
Blijven de pijltjes of de kadertjes over, dan is de navigatie luider dan de boodschap.

## 2. Vier maten per deck, en niet meer

Leg vóór de eerste slide vier getallen vast en gebruik overal die vier:

| rol | richting | waarvoor |
|---|---|---|
| **drager** | 28 tot 40pt Montserrat Light | het getal of begrip dat de slide draagt, op ten hoogste één slide op drie |
| **kop** | 18pt Montserrat SemiBold | kolomkop, kaartkop, rolnaam |
| **body** | 16pt Lato Light | alles wat gelezen wordt |
| **voetnoot** | 11pt | bron, eenheid, peildatum |

De letter op de slide is licht: Lato Light voor wat gelezen wordt, Montserrat Light voor een
drager of een citaat, en Montserrat SemiBold voor een kop, een label, een rolnaam of een
kolomkop — dus voor wat lósstaat en op zijn eigen regel begint. Een aanhef bínnen een
doorlopende regel is `Lato Semibold`, want één regel is één familie (§9). Gotham Bold
staat alleen in de titel, en die schrijf je niet zelf — hij komt uit de layout. Schrijf je hem
toch in de contentzone, dan weigert `run()` het en blokkeert `qa_text.py` de deck.

12pt is de dichte variant voor een kaartenrij van drie of meer of een tabelcel, en de vloer.
14pt is het kapitaallabel. 10pt gebruik je niet meer.

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

**Eén accent, tenzij kleur iets te coderen heeft.** Dit is de andere kant van hetzelfde en het
gaat even vaak mis. Kies voor de deck één accentkleur naast navy en houd die vast; een tweede
of derde hue komt er alleen bij wanneer er iets te onderscheiden is dat de lezer apart moet
houden — categorieën, werkstromen, stappen in een proces, of twee kanten van een afweging.

De toets is één vraag, en je stelt hem per kleur: **wat codeert deze hue, in één woord?** Kun
je dat niet zeggen, dan gaat de kleur eruit en wordt het het accent van de deck.

Waar het misgaat: twee kaarten naast elkaar die samen één werkstroom vormen — "opslaan" links
en "terugvinden" rechts — met een emerald kop op de een en een royal kop op de ander. Er is
niets tegengesteld aan die twee, de lezer leest ze achter elkaar en hoeft ze nooit te
vergelijken. Twee hues suggereren daar een tegenstelling die er niet is. Één accent op beide
koppen zegt hetzelfde en leest rustiger. Twee hues zijn wél op hun plek bij kost tegenover
baat, nu tegenover straks, of een set van vier categorieën die door de hele deck terugkomt.

**Rol naar hue, één keer en dan vasthouden.** Heb je besloten dat kleur iets codeert, schrijf
dan op welke categorie welke kleur krijgt, en beslis er daarna niet meer over. Dezelfde rol die
op slide 4 sky draagt en op slide 11 emerald, betekent dat de kleur decoratie is geworden. De
vaste laag: grapefruit is kost of waarschuwing, emerald is baat, navy is structuur en totaal,
oranje is het resultaat en het punt waar het om gaat. Sky en royal zijn vrij voor categorieën
zonder eigen lading.

Twee categorieën in dezelfde set krijgen nooit dezelfde hue. En één hue voor alles is het
defect uit de afgekeurde deck — maar let op de verkeerde lezing daarvan: dat defect was één
lichte tint over vier slides die vier verschillende dingen deden, niet één accent dat consequent
één ding betekent.

Deze keuze hoort in de outline, bij de slides waar kleur iets doet. Daar is hij te overzien en
te herzien voordat er iets gebouwd is; op de render is hij alleen nog te repareren.

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

## 5. Een deck heeft twee registers

Gemeten aandeel wit, tint en verzadigd per slide. De afgekeurde deck: 44 tot 53 procent wit, 42
tot 54 procent tint, 1 tot 7 procent verzadigd — op élke contentslide dezelfde band. De
referentie heeft twee registers en geen enkele slide in het midden: bijna helemaal wit (85 tot
88 procent) óf echt verzadigd (20 tot 37 procent).

Dat middengrijs is precies wat een deck karakterloos maakt. Er is nergens iets leeg en nergens
iets vol, dus er is geen contrast tussen de slides onderling.

Wijs de registers dus toe. In een deck van vijf contentslides staat er minstens één **op wit**:
geen kaartvulling, alleen gekleurde koppen, proza en misschien een haarlijn. En minstens één is
**echt verzadigd**: volle vlakken met de drager erin. De rest ligt ertussen.

**En reken na hoeveel "verzadigd" is, want de schatting zit er structureel naast.** Dit besluit
neem je vóór het bouwen en het is het enige van de zes dat je tijdens het bouwen niet ziet. Op
een deck dat net met deze skill is gebouwd waren twee slides als verzadigd aangewezen en maten
ze 7 en 12 procent: één emerald blok van 3,94 bij 1,15 in, en vier rijlabels van 3,00 in breed.
Beide voelden tijdens het bouwen als "die slide is de volle". Een slide is 13,33 bij 7,5 in, dus
100 vierkante inch, en de band van 20 tot 37 procent betekent dat er 20 tot 37 vierkante inch
vol moet staan — een blok van 8 bij 2,5 in, of vier rijen over de volle breedte. Toen slide 12
in dat deck volledig verzadigd werd gemaakt, kwam hij op 23 procent.

Meet het dus, in dezelfde ronde als de render: `qa_tellingen.py --renders` geeft het aandeel
wit, tint en verzadigd per slide. Zonder die meting blijft besluit 5 een intentie, en dat is
nagemeten: het middengrijs uit de afgekeurde deck ontstond niet doordat iemand besloot dat elke
slide in het midden mocht liggen.

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

**Een streep scheidt lichter dan een vlak.** Onder een label, tussen twee registers, boven een
sluitregel.

**Eén kaarttaal per deck.** De hoekvorm en de vullingssoort van je eerste kaart gelden voor
elke kaart. Afgerond of recht is vrij; halverwege wisselen is het defect dat het snelst opvalt,
ook als beide varianten los goed zijn. En dat is gebeurd: drie slides afgerond, de vierde recht.

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
- **Eén familie per regel, en twee gewichten binnen die familie.** Een aanhef van twee tot
  vier woorden haalt twee hiërarchieniveaus binnen één tekstregel, zonder tweede kolom en
  zonder tweede vak. Staat die aanhef binnen een doorlopende regel, dan is hij **Lato
  Semibold** op een rest in Lato Light, op dezelfde maat. Niet Lato Light met `b="1"`, want
  dat is nepvet en de renderer kiest zelf wat hij ervan maakt; `Lato Semibold` bestaat als
  eigen familienaam in de fontlijst en is een echt gewicht. Nagemeten op de render, dezelfde
  zin op 16pt met elk Lato-gewicht als aanhef naast Lato Light: `Lato` regular en `Lato
  Medium` zetten een verschil dat je pas ziet als je het weet, `Lato Heavy` gaat met de kop
  erboven concurreren, `Lato Semibold` zet de sprong die je wil. `aanhef()` in `shapes.py`
  doet dit; `para()` weigert een alinea met een Montserrat- én een Lato-run.
  Montserrat SemiBold blijft voor wat **lósstaat en op zijn eigen regel begint**: een kop, een
  kapitaallabel, een rolnaam, een kolomkop. Montserrat Light is de dragerletter en staat
  altijd alleen.

  **De verkeerde lezing, en die kwam uit dit document.** Hier stond tot nu toe dat de aanhef
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
- **De sluitregel op wit.** Eén regel zonder vulling, aanhef in Lato Semibold, hooguit een
  streep erboven (§8). Zegt precies wat de band zegt, zonder het vlak.
- **Er valt niets af te sluiten.** In titelmodus A draagt de titel de bewering al; een slide
  die zijn boodschap boven heeft staan hoeft haar onderaan niet te herhalen. De compositie
  eindigt waar de inhoud eindigt en vult de zone met inhoud (§6), niet met een band.

De band die dan overblijft is de slide waar de conclusie werkelijk een eigen zin is die nergens
anders op de slide staat — op `maatstaf/11` komt hij precies één keer voor, onder het
beslismoment.

Variatie zit niet in het layoutnummer. Zes contentslides op layout 19 met zes verschillende
composities is goed. Maar kies de layout ook niet standaard: een tweeluik is layout 22, waar de
kolomkoppen geërfde placeholders zijn die je mag herkleuren en verzwaren; doorlopende tekst is
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

**Het dichtheidsbesluit: spreekdeck of leave-behind.** Dit is een ander onderscheid dan de
twee registers van §5 — dat gaat over kleurbezetting per slide, dit over woorden per deck —
en het is het eerste deckbrede besluit in de outline (skill, stap 2).

- **Spreekdeck** — de slide is de achtergrond bij iemand die praat. Wat de spreker zegt hoort
  niet op de slide; daar staat alleen wat het verhaal draagt, en de toelichting gaat naar de
  presentatornotities. Dit is het strakke eind. Gemeten: de twee lichtste maatstafslides,
  `13` en `14`, staan op 50 en 59 woorden inclusief titel — een plot op schaal en een schema,
  en beide vullen de zone (§6), want weinig woorden is geen lege slide. Het gemeten
  spreekdeck zat op gemiddeld 85 woorden per contentslide met een piek van 101, en dat is
  voor deze dichtheid nog steeds te dicht: daar stond uitgeschreven wat de spreker zou
  zeggen.
- **Leave-behind** — de slide moet zonder spreker te lezen zijn (`voice.md`, de bindende
  toets), en mag dus dicht zijn. Een prozaslide met twee goed gezette kolommen is hier een
  volwaardige exhibit; `maatstaf/04` is precies dat. Gemeten: `12` en `11` staan op 99 en 141
  woorden inclusief titel, en `11` — vier fasekaarten van ongeveer dertig woorden elk — is
  van de vier reconstructies de sterkste. 141 woorden is dus geen defect.

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
