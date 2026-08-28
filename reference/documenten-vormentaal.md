# De vormentaal van een SFNL-document

Wat een document goed maakt, en waaraan je ziet dat er een model achter zat. De feiten — maten,
klassen, kleuren — staan in `documenten-stramien.md`; dit gaat over de beslissingen.

De metingen komen uit het SFNL-jaarrapport 2025, de casespread Civitates, en uit de vijf pagina's
die met deze skill zijn gebouwd en in `assets/documenten/maatstaf/` staan.

---

## 1. Het raster komt eerst, altijd

Dit is de enige volgorde die werkt: eerst de marge en de kolommen, dan de hiërarchie, dan de
flow. Wie ze door elkaar oplost, lost geen van drie op.

De reden dat het raster eerst komt is niet netheid maar meetbaarheid. Een kolom van 86 mm zet
ongeveer 52 tekens op een regel bij 10 pt Lato Light. Dat getal bepaalt hoeveel woorden er op een
pagina passen, en dus hoeveel er te zeggen valt, en dus hoeveel pagina's het worden. Wie de tekst
eerst schrijft en dan een raster zoekt, komt altijd één pagina tekort of één te veel.

**De verticale kant heet het basisraster en hij is er om één reden.** Elke sprong tussen blokken
is een veelvoud van de regelafstand (17,33 px), zodat twee kolommen naast elkaar op dezelfde
lijnen blijven zitten. Zonder dat schuiven de regels van de linker- en rechterkolom een halve
regel uit elkaar, en dat is precies zo goed te zien als het klinkt — de lezer weet niet waarom
het rommelig oogt, maar hij ziet het.

---

## 2. Eén drager per pagina

Elke pagina heeft één element dat de boodschap draagt, en de rest is er om dat element te laten
staan. Vijf soorten, en meer zijn er niet:

- **een getal op displaymaat** — 44 procent minder spoedeisende hulp
- **de compositie zelf** — drie routes naast elkaar, waarbij het náást elkaar staan de boodschap is
- **een uitspraak** — de zin die blijft hangen, groot gezet over de maat
- **een kleurvlak** — een hele pagina in mint of oranje, waar de kleur het hoofdstuk markeert
- **een beeld** — een foto die aflopend over de bovenste helft staat

Twee dragers op één pagina is geen dubbele nadruk maar geen nadruk. En een pagina zonder drager
is een pagina die de lezer doorbladert.

**Grote letter is de duurste drager en dus de zeldzaamste.** Displaymaat op meer dan een derde van
de inhoudspagina's is geen nadruk meer maar een toon.

---

## 3. Witruimte is verdeeld, een gat is opgehoopt

Dit is het defect dat op het eerste gebouwde document op alle vier de pagina's zat, en het is het
snelst zichtbare verschil tussen ontworpen en opgemaakt.

Witruimte is wat er tussen elk paar blokken zit, in verhoudingen die je hebt gekozen. Een gat is
wat er overblijft als je twee blokken naar de randen duwt en de lucht op één plek laat vallen. Ze
zijn even groot in px en volstrekt verschillend om naar te kijken.

De twee bronnen:

- `justify-content: space-between` op de zetspiegel. Op een omslag met drie blokken is dat precies
  goed, want dan zijn er drie ankers. Op een inhoudspagina met twee blokken is het altijd fout.
- `margin-top: auto` op het laatste blok, om het naar beneden te duwen. Dat werkt één keer; zet
  je hem twee keer, dan verdeel je de lucht juist niet.

**Het antwoord is nooit het gat verkleinen.** Het is meer inhoud, grotere elementen, of een
kortere pagina. Een pagina die op driekwart ophoudt, is een pagina die te weinig te zeggen heeft
voor deze maat — en dan is A5 het antwoord, of één pagina minder.

`qa_document.py` meet dit als `gat` (het grootste lege vlak over de volle breedte) en als
`vulgraad` (hoe ver de inhoud naar beneden komt). Boven de 170 px gat op een pagina met meer dan
zeventig woorden meldt hij het. Onder de zeventig woorden meldt hij niets, want dan is de leegte
de compositie.

---

## 4. Uitvullen met afbreking, of helemaal niet

Het rapport zet zijn lopende tekst uitgevuld met automatische afbreking, in kolommen van 55 tot
86 mm. Dat is geen smaak: zonder afbreking vallen er in een uitgevulde kolom van 55 mm gaten van
vier spaties, en dan is vlaggend links beter.

Dus: `text-align: justify` plus `hyphens: auto` plus `lang="nl"` op het document. Die derde
vergeten is de stille fout — Chromium breekt dan op Engelse regels af en zet "gezond-heidsbevor-
dering" waar "gezondheids-bevordering" hoort.

Vlaggend links (`.tekst--links`) gebruik je voor een kolom onder 50 mm, voor een bijschrift, en
voor alles op een donker of gekleurd veld: daar zijn de gaten van het uitvullen zichtbaarder dan
op wit.

---

## 5. De aanhef vervangt de opsomming

Het rapport heeft vrijwel geen bullets. Wat het wél heeft is de aanhef: de eerste woorden van een
alinea vetgezet, zodat de scannende lezer de structuur ziet zonder dat de tekst uiteenvalt in
losse punten.

> **Het geld staat op de verkeerde plek.** Nederland geeft ruim 100 miljard euro per jaar uit aan
> zorg, waarvan minder dan drie procent aan preventie.

Dat leest als proza en scant als een lijst. Een opsomming met drie bullets van elk anderhalve
regel is dezelfde informatie met meer wit en minder samenhang.

**Wanneer een opsomming wél het antwoord is:** als de volgorde niet uitmaakt en de items echt
losstaan (een programma, een lijst deelnemers, vier eisen). Dan is het een echte lijst, met de
`.lesmarkering` of een `.badge` ervoor, en niet een alinea met streepjes.

**En de toets die het vaakst iets oplevert:** staat op elk item dezelfde vetgezette aanhef, dan
zijn die aanheffen een kolomkop en is het antwoord een tabel.

---

## 6. Aflopend werk is wat drukwerk van een document scheidt

Een vlak of een foto die de snijrand raakt kost één klasse en het is het goedkoopste signaal dat
er een ontwerper aan te pas kwam. Een document waarin élk element netjes binnen de marge blijft,
leest als Word, hoe goed de typografie ook is.

Drie plekken waar het vanzelf goed valt: een kleurband onderaan de laatste pagina, een foto over
de bovenste helft, en een tonale bol die half buiten het blad valt.

**De tonale bol verdient een aparte waarschuwing.** Dat is een cirkel in dezelfde kleur, iets
lichter, half buiten de pagina — het geeft een vol kleurvlak diepte zonder een tweede kleur binnen
te halen. Maar hij moet subtiel zijn. Op de eerste gebouwde omslag stonden er twee, waarvan één in
navy op 7 procent, en die maakte het oranje vuil in plaats van diep. Eén bol, in de eigen kleur,
op 10 tot 16 procent.

---

## 7. De spread is de eenheid, niet de pagina

Een lezer ziet twee pagina's tegelijk. Dus beoordeel je ze samen, en daarom zet `render.py` het
contactblad als spreads neer: pagina 1 alleen rechts, dan 2-3, 4-5.

Wat je alleen zo ziet:

- Twee pagina's die allebei met een grote kop linksboven beginnen. Los kloppen ze; naast elkaar
  is het een dubbele opening.
- Twee kleurvlakken die elkaar over de rug raken en samen één groot vlak worden.
- Een tabel links en een tabel rechts. Dat is niet twee tabellen, dat is een spread zonder
  afwisseling.
- Een kop die op de linkerpagina op 88 px begint en op de rechter op 104. Op de spread is dat een
  scheve horizon.

**De omslag telt niet mee in dit ritme**, want die staat alleen. Pagina 2 is de eerste die met
iets tegenover zich moet kloppen — en dat is meestal pagina 3.

---

## 8. Kleur codeert of hij markeert, en nooit allebei tegelijk

Oranje is het merk. Het staat op de labels, de streep, de badge en de kicker, en het betekent
daar niets anders dan "dit is van SFNL".

Een tweede accent — mint, violet, periwinkel, emerald — betekent wél iets, en dan schrijf je in
één woord op wat. Mint is uitkomst, violet is de case, grapefruit is waarschuwing. Dat woord
staat bovenaan de outline en het geldt voor het hele document. Twee categorieën in dezelfde reeks
krijgen nooit dezelfde kleur, en twee blokken die samen één ding zijn krijgen nooit twee
verschillende.

**Wat er niet gebeurt is een derde accent erbij omdat er drie kaarten zijn.** Drie kaarten die
hetzelfde soort ding zijn, krijgen dezelfde kleur; wat ze onderscheidt is hun inhoud en niet hun
vulling.

---

## 9. Een document van een tot drie pagina's is een ander soort stuk

Niet een korter document maar een ander soort, en dat is de gewone praktijk: een one-pager, een
tweeluik, een notitie van drie. Drie dingen vallen weg en dat verandert de opbouw.

**Er is geen buitenste pagina.** In een document van vier is pagina 4 de plek voor alles wat apart
moet staan, en daarmee is het uit de weg. Op twee pagina's bestaat die plek niet, dus wat daar
anders had gestaan moet ergens tussendoor: onderaan de laatste pagina onder een haarlijn, of in
de aflopende band. Dat is een compositiebesluit en geen restje — en wát daar komt te staan volgt
uit het materiaal, niet uit wat er gewoonlijk op een achterkant staat.

**Er is geen aanloop.** Op vier pagina's mag pagina 2 het probleem schetsen en pagina 3 het
antwoord geven. Op twee pagina's is de eerste zin meteen de boodschap. Wie hier een aanloop
schrijft, heeft de helft van zijn document opgemaakt aan opwarmen.

**Het voorblad wordt duur.** Een voorblad kost op één blad alles, op een tweeluik de helft en op
drie pagina's een derde. Daarom is onder de vier pagina's de titelbalk meestal het antwoord
(besluit 5): een kwart pagina, en de titel staat er net zo goed op.

**Wat er niet wegvalt is het kader.** Dezelfde marge, hetzelfde raster, dezelfde maatladder,
hetzelfde aflopende werk. Een one-pager die er goedkoop uitziet, is bijna altijd een one-pager
waarop iemand de marge heeft ingekort om er meer op te krijgen. Dan is er te veel tekst, en dat
los je op in de tekst.

---

## 10. De opening is eenmalig; de hoofdstukopening is iets anders

Twee vragen die op elkaar lijken en het niet zijn.

**De opening** gaat over de dektitel: hoe komt de naam van het stuk op het document te staan. Dat
gebeurt één keer, op pagina 1, en het is besluit 5 in het vragenvuur.

- **Titelblad.** Pagina 1 is helemaal de titel. Wat elk SFNL-drukwerk doet, en het is de pagina
  waaraan iemand het stuk later terugkent. Het kost een hele pagina, en op een document van vier is
  dat een kwart van je ruimte.
- **Titelbalk.** Geen aparte pagina: een aflopende band bovenaan pagina 1 draagt de dektitel en
  de inhoud begint eronder. Ongeveer een kwart pagina, en de eerste pagina wordt voller.
- **Gewoon titel.** De dektitel staat in de zetspiegel met een streep eronder en de tekst loopt
  door. Vrijwel gratis, en op één blad is het de enige die kan.

De afweging is dus ruimte tegen herkenbaarheid, en die valt anders uit naar buiten dan naar
binnen. Een uitnodiging die de deur uit gaat verdient zijn voorblad; een interne notitie van
vier pagina's die alleen gelezen wordt, houdt liever vier pagina's inhoud over dan drie.

**De hoofdstukopening** gaat over iets anders: hoe begint een hoofdstuk binnen het document. Die
vraag bestaat pas vanaf acht pagina's — onder dat aantal zijn er geen hoofdstukken maar pagina's
met een titel erboven, en er valt niets terug te vinden. Je beslist hem in de outline en niet in
het vragenvuur.

**De regel die hier geldt is consistentie, en die geldt alleen binnen elke vraag apart.** Alle
hoofdstukken openen op dezelfde manier: hoofdstuk 1 met een band en hoofdstuk 2 met alleen een
kop leest als een fout. En als er een band is, heeft hij één hoogte — 190 px op de ene pagina en
260 op de volgende laat de tekst per pagina op een andere hoogte beginnen, en op de spread is dat
een scheve horizon.

Wat géén fout is: een document dat met een voorblad begint en daarna per hoofdstuk een band
draagt. Dat zijn twee besluiten over twee verschillende dingen, en de lezer leest ze ook zo — de
eerste zegt "dit is het stuk", de tweede zegt "hier begint een deel".

---

## 11. Een infographic is een beeld dat rekent, geen versiering

Het onderscheid dat ertoe doet: een infographic laat een verhouding, een volgorde of een afstand
zien die je in tekst zou moeten uitleggen. Drie gekleurde vlakken met een woord erin doen dat
niet — dat is een lijst met vulling.

De toets die het vaakst iets oplevert: **haal het beeld weg en lees de pagina.** Mist er niets,
dan was het versiering. `maatstaf/03` doorstaat die toets — de stippellijn die nergens aankomt is
het hele argument van de pagina, en in tekst kost dat een alinea.

**Drie dingen die stil misgaan, en de eerste is de vervelendste.**

1. **Een SVG schaalt álles mee, ook zijn letters.** Teken op schaal 1:1: de `viewBox` even breed
   als het kader in px. Een beeld dat op 680 is getekend en in een kader van 340 staat, zet zijn
   13,33 px-tekst op 6,7 px, en dat is onder de vloer zonder dat er iets in de markup fout staat.
   Meer hoogte nodig: laat de `viewBox` in de hoogte groeien en houd de breedte gelijk. Gemeten:
   de infographic van `maatstaf/03` groeide van 268 naar 372 in de hoogte en de letters bleven.
2. **De maatladder geldt ook binnen de SVG.** Nagemeten: dezelfde infographic voerde 12, 13 en
   15 px in naast de zes van de ladder, en `qa_document.py` telde acht maten op het document. Gebruik
   dezelfde getallen als op de pagina.
3. **Een leeg kader leest als witruimte.** Zet `beeldkader--leeg` met een `data-wat` neer zolang
   het beeld er nog niet is, dan staat er een gemarkeerd vlak en zie je op de render dat er iets
   ontbreekt. Blijft dat staan, dan gaat het mee de PDF in; `qa_document.py` telt ze.

**De kleuren coderen, net als elders.** Oranje is de investering, emerald de opbrengst,
grapefruit de waarschuwing, navy de structuur. Schrijf per kleur in één woord op wat hij
betekent, en houd dat voor het hele document aan.

**En de herkomst staat in het bijschrift, niet in het beeld.** Elk getal draagt zijn eenheid,
periode en bron; die staan in de `figcaption` eronder, zodat het beeld schoon blijft en de lezer
toch kan nagaan waar het vandaan komt.

---

## 11b. Kleur een kader, niet het blad — en nooit twee velden op één pagina

Een heel blad in een kleur is de zwaarste vorm die dit drukwerk kent. Het is niet verboden — een
executive summary opent op navy en dat is een regel — maar het is een besluit dat je één keer per
pagina neemt, en meestal helemaal niet.

**Twee aflopende kleurvelden op één pagina is een blokkade.** Gemeten op een executive summary van
vier pagina's: de laatste pagina was navy over het volle blad, met een oranje band van 270 px
onderaan die het logo en één bronregel droeg, en daar bovenop een wit paneel. Drie oppervlakken,
en de tekst hoorde bij geen van drieën meer thuis. Het blad had geen rust en de band had geen
inhoud — die was zo hoog omdat er ruimte over was, niet omdat er iets in stond.
`qa_document.py` meldt dit als `kleurveld-stapeling` en het is `critical`.

Wat telt als een aflopend veld: een vlak dat over de volle bladbreedte loopt, aan minstens één
rand raakt, en een andere kleur heeft dan het papier. De pagina zelf telt mee zodra hij niet wit
is. Een paneel dat binnen de marge blijft telt niet — dat is precies het alternatief.

**Het alternatief is het kader, en dat is bijna altijd beter.** Zet de kleur op een `.paneel` en
laat het blad wit. Dan doet de kleur wat kleur hoort te doen — hij wijst iets aan — in plaats van
de achtergrond te zijn waar alles op ligt. Een pagina kan meerdere gekleurde panelen dragen zonder
dat het luid wordt, want ze staan náást elkaar in plaats van óver elkaar.

De volgorde waarin je het overweegt:

1. **Wit blad, gekleurd paneel.** De gewone vorm. De kleur wijst aan.
2. **Wit blad, meerdere panelen.** Ook prima, zolang de kleuren iets coderen (§8).
3. **Gekleurd blad, geen tweede veld.** De opening, een scheidingsblad, een pagina die apart
   staat. Eén keer per document, hooguit.
4. **Gekleurd blad met een band erover.** Nooit.

### De titel die half over de kaderrand hangt

Een titel die half in en half boven zijn paneel staat, is een echt merkteken en het drukwerk doet
het — het rapport zet zijn portret zo, half buiten het vlak. Het werkt om dezelfde reden als daar:
het bindt twee dingen aan elkaar die anders los zouden staan.

**Maar het is een nadrukmiddel en geen opmaak.** Gebruik het alleen wanneer het kader zelf de
nadruk draagt: één paneel op de pagina dat de kern van het stuk bevat, met de titel eraan
vastgeklonken. Twee overhangende titels op één pagina is er één te veel, en op een pagina met drie
panelen is het ruis. De klasse is `.paneel--overhang` en de titel erin is `.paneel__overhangtitel`;
`stijl.css` §8.10a heeft de maten.

## 12. De weigerlijst

Veertien dingen die maken dat een document eruitziet alsof een model het heeft gemaakt. Ze staan
hier omdat ze allemaal, stuk voor stuk, de eerste inval zijn.

1. **Drie gelijke kaarten met een icoon, een vetgezette kop en twee regels grijze tekst.** Dit is
   de duidelijkste tell die er is. Als de drie dingen echt vergelijkbaar zijn, is het een tabel.
   Als ze het niet zijn, horen ze niet in drie gelijke dozen.
2. **Slagschaduwen.** Op papier bestaat geen schaduw. Een kaart krijgt een haarlijn in zijn eigen
   kleur. `qa_document.py` meldt elke niet-inset `box-shadow`.
3. **Afgeronde hoeken overal.** De radius is één waarde voor het hele document, en nul is een prima
   waarde. Vier verschillende radii in één document is geen ontwerp.
4. **Emoji als icoon.** Die zetten een tweede lettertype op de pagina en lezen als een
   chatbericht. Teken het icoon zelf in SVG op het raster van 24, of laat het weg. Dit blokkeert.
5. **Body op 16 px met regelafstand 1,6 en één brede kolom.** Dat is een webpagina. Drukwerk is
   10/13 in kolommen.
6. **Verlopen die je zelf verzint.** Er is één huisverloop en het is gemeten. Een tweede verloop
   is een tweede huisstijl.
7. **Alles gecentreerd.** Centreren is voor een uitspraak of een omslag. Lopende tekst, labels en
   koppen staan links, en dan staan ze op één lijn.
8. **Generieke koppen.** "Inleiding", "Achtergrond", "Conclusie", "Belangrijkste inzichten". Een
   kop is een bewering: "Preventie loont, maar niet voor wie ervoor betaalt".
9. **Kleur als versiering.** Een vlak dat een kwart van de pagina beslaat en vier woorden draagt,
   is geen accent maar een luide leegte.
10. **Een tabel met randen rondom elke cel en een grijze kopbalk.** Dat is de Word-tabellook. Een
    lijn onder de kop, een haarlijn per rij, verder niets.
11. **Vier of meer letterafmetingen die niemand heeft gekozen**, ontstaan doordat elk element zijn
    eigen inline `font-size` kreeg. De ladder heeft er zes; `qa_document.py` telt ze.
12. **Wit op oranje voor lopende tekst.** Contrast 2,6. Het ziet er op een scherm nog net uit en
    op papier is het weg.
13. **Een lege onderste helft met een zin in het midden**, omdat de pagina vol moest en er niets
    meer was. Dan is er één pagina te veel.
14. **Elk element netjes binnen de marge.** Geen enkel aflopend vlak, geen enkele overlap. Dat is
    een document, geen drukwerk.
15. **Een infographic die niets uitrekent.** Drie gekleurde vlakken met een woord erin, of een
    stel iconen op een rij. Haal het beeld weg: mist er niets, dan hoorde het er niet.
16. **Hoofdstukken die elk anders openen**, of een band die per hoofdstuk van hoogte verandert.
    Dan begint de tekst op elke pagina ergens anders, en op de spread is dat een scheve horizon.
17. **Een rubriek die de gebruiker nooit heeft genoemd.** Een programma op een uitnodiging, een
    contactblok onderaan, een "belangrijkste inzichten" naast de tekst die dat al zei. Een model
    weet wat er meestal in zo'n document staat en vult dat in; dan staat er inhoud in het document
    die niemand heeft geschreven. De vorm is van de skill, de inhoud van het materiaal — de
    SKILL heeft er een eigen hoofdstuk voor onder *De grens die deze skill bewaakt*.
18. **Een verzonnen feit waar een gat zat.** Een datum, een bedrag, een naam die aannemelijk
    genoeg is om niet op te vallen. Zet er een zichtbare markering neer — `[DATUM]` — want die
    vindt de gebruiker wel en een plausibel getal niet.

---

## 13. Wat er niet in staat

Geen paginabibliotheek en geen sjablonen. `stijl.css` geeft het kader, het raster, de maatladder,
de kleurregels en de merktekens; wat je ermee bouwt is elke pagina opnieuw jouw beslissing.

Dat is een keuze en hij komt uit dezelfde meting als bij `sfnl-slides`: een route waarin de vorm
uit een catalogus wordt gekozen, levert documenten op die geen van alle fout zijn en geen van
alle goed. Wie zo bouwt, kiest niet meer maar vult in.

Wat er wel is als je vastloopt: `assets/documenten/voorbeeld/` heeft vijf gebouwde pagina's als kale
fragmenten, en `assets/documenten/maatstaf/` heeft dezelfde vijf gerenderd. Kijk ernaar om te weten
waar de lat ligt, niet om na te tekenen.
