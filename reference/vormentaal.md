# Vormentaal

Dit is de maatstaf. Geen catalogus met patronen om uit te kiezen, en geen drempels waar een
script op afkeurt: wat een SFNL-slide goed maakt, geordend van meeste naar minste effect, zodat
je je eigen compositie eraan kunt toetsen.

Elke regel hieronder is nagemeten. Waar er een getal staat, komt dat uit de XML of de render van
de vijf decks die de blinde vergelijking wonnen, of uit de deck die het niet haalde. Waar een
regel eerder verkeerd te lezen bleek, staat de verkeerde lezing er expliciet bij — dat is geen
overbodige uitleg, dat zijn fouten die daadwerkelijk gemaakt zijn.

Lees dit één keer voordat je de eerste slide bouwt, samen met de tien voorbeelden in
`assets/maatstaf/`.

---

## 1. Elke slide heeft één drager, en die is groot

De drager is het element dat de boodschap draagt: één getal, één verhouding, één kernbegrip,
één zin. Al het andere ondersteunt.

**De maat is de helft van het werk.** In de winnende decks staat op vijf van de tien slides
iets tussen 44 en 56pt. In de deck die het niet haalde is het grootste element in de
contentzone 19pt. Dat is het verschil tussen een slide met een ingang en een slide die je moet
gaan lezen om te weten waar je moet beginnen.

Twee toetsen, en je doet ze tijdens het bouwen en niet pas op de render:

- Staat er in de contentzone iets van **40pt of groter**? De geërfde titel van 24pt telt niet
  mee: die staat op elke slide en onderscheidt dus niets.
- Is de drager minstens **tweeënhalf keer de bodymaat** op diezelfde slide? Loopt je hele
  slide tussen 14 en 19pt, dan is er geen hiërarchie maar een verzameling.

**Ook zonder getal is er een drager.** Dit is waar het in de praktijk misgaat, want de neiging
is om te denken dat een conceptuele slide geen drager kán hebben. Dat kan wel: een kernbegrip
van 28pt in de hue van zijn categorie, een rangnummer van 40pt, één rij die als enige een volle
kleur draagt, of een kolomkop van 18pt SemiBold in een accentkleur op wit terwijl de rest navy
is. Op de sterkste referentieslide zonder cijfers is de drager niet groot maar zwaar en
gekleurd: 18pt Montserrat SemiBold in emerald tegenover 18pt in grapefruit, op wit.

De kneepoefening blijft de eindtoets: klein of onscherp bekeken moet de drager overblijven.
Blijven de pijltjes of de kadertjes over, dan is de navigatie luider dan de boodschap.

## 2. Vier maten per deck, en niet meer

Leg vóór de eerste slide vier getallen vast en gebruik overal die vier:

| rol | richting | waarvoor |
|---|---|---|
| **drager** | 40 tot 60pt | het getal of begrip dat de slide draagt |
| **kop** | 18pt Montserrat SemiBold | kolomkop, kaartkop, rolnaam |
| **body** | 16pt Lato Light | alles wat gelezen wordt |
| **voetnoot** | 11pt | bron, eenheid, peildatum |

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
accent als **tekstkleur op wit**: een kolomkop van 18pt SemiBold in emerald naast een van 18pt
in grapefruit, een getal van 44pt in oranje, een toelichtingsregel in de kleur van de rij waar
hij bij hoort. De afgekeurde deck had 31 gevulde vlakken en nul gekleurde letters.

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
vanaf ongeveer 40pt mag wit ook op emerald, oranje en sky, want daar leest het cijfer als vorm
en niet als tekst. Dat is een bewuste keuze die je op de render controleert, geen default.

**Rol naar hue, één keer en dan vasthouden.** Schrijf op welke categorie welke kleur krijgt
zodra je die keuze de eerste keer maakt, en beslis er daarna niet meer over. Dezelfde rol die
op slide 4 sky draagt en op slide 11 emerald, betekent dat de kleur decoratie is geworden. De
vaste laag: grapefruit is kost of waarschuwing, emerald is baat, navy is structuur en totaal,
oranje is het resultaat en het punt waar het om gaat. Sky en royal zijn vrij voor categorieën
zonder eigen lading.

Twee categorieën in dezelfde set krijgen nooit dezelfde hue. En één hue voor alles is het
defect uit de afgekeurde deck.

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
4. Meet de vulgraad: teksthoogte gedeeld door blokhoogte. Onder 0,6 kijk je opnieuw, onder 0,5
   is het fout.

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
- **Twee gewichten in één alinea.** Montserrat SemiBold als aanhef van twee tot vier woorden,
  Lato Light voor de rest, op dezelfde maat. Zo haalt de referentie twee hiërarchieniveaus
  binnen één tekstregel, zonder tweede kolom en zonder tweede vak. Gebruik dit in plaats van
  Lato Light met `b="1"`, want dat is nepvet.
- **Insets** 0,2 links en rechts en 0,15 boven en onder op een vak met vulling; 0 op een
  tekstvak zonder vulling, zodat de tekst met de vakrand uitlijnt en dus met de rest van de
  kolom.
- **Centreren** tot ongeveer 3 in breed, daarboven links uitgelijnd. Cursief niet.
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
één zo'n band per vier slides. De andere slides sluiten af doordat de laatste rij zelf de
conclusie is, doordat één cel vol gekleurd is, doordat de sluitregel op wit staat, of doordat er
niets af te sluiten valt.

Variatie zit niet in het layoutnummer. Zes contentslides op layout 19 met zes verschillende
composities is goed. Maar kies de layout ook niet standaard: een tweeluik is layout 22, waar de
kolomkoppen geërfde placeholders zijn die je mag herkleuren en verzwaren; doorlopende tekst is
20; een schema over de volle hoogte zonder titel is 17. Vier contentslides op 19 achter elkaar
is de eenvormigheid waarop de vergelijking verloren is.

## 11. Een cijfer draagt zijn herkomst mee

Eén regel van 11pt Lato Light in navy op 70 procent dekking, zonder vulling, insets 0, direct
onder de doos waar hij bij hoort en over de breedte van die doos — niet onder de slide. Twee
beelden op één slide krijgen twee bronregels.

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

---

## Wat hier niet staat

Geen patroonnamen. Geen verplichte afsluitband. Geen maximum aantal tekstgroottes per slide.
Geen tabel met kaartbaselines op vaste y-waarden. Geen minimumafstand die een script afdwingt.

En geen belofte dat dit genoeg is. Twee van de tien voorbeelden in `assets/maatstaf/` dragen
zelf een defect: op `01` en `06` staat het grote getal over zijn eigen label, en op `01` is de
onderste helft van de vier kaarten leeg. Kijk daar naar de vier hues en naar de brede panelen
eronder, niet naar de kaarthoogte. De lat is de compositie van die slides, niet hun uitvoering.

De render blijft het enige oordeel over de vorm.
