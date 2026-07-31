# Vormentaal

Dit is de maatstaf, niet de catalogus. Er staat geen patroon in dat je kunt kiezen en geen
recept dat je kunt invullen. Er staat wat een SFNL-slide goed maakt, zodat je je eigen
compositie eraan kunt toetsen zodra je hem op de render ziet.

Lees dit één keer voordat je de eerste slide bouwt, samen met de tien voorbeelden in
`assets/maatstaf/`. Die voorbeelden komen uit echte decks die de vergelijking hebben
gewonnen. Ze zijn er niet om na te tekenen; ze zijn er om te weten waar de lat ligt.

## Het vlak is 13,33 bij 7,5 inch en de inhoud vult het

De contentzone begint op 1,93 in en loopt tot 6,93 in. Het eerste element van je compositie
staat tegen die bovenrand aan, niet een centimeter eronder en niet een derde van de slide
naar beneden. De onderrand is een ondergrens en geen suggestie: als je compositie op 4,5 in
ophoudt, staat er twee en een halve inch niets onder je argument.

Dit is het defect dat in de meting het vaakst terugkwam en het meest opviel. Op acht van de
twaalf slides van de afgekeurde deck begon de inhoud pas rond 2,8 in, met een band leeg wit
tussen de oranje dash en het eerste blok. De lezer ziet dan een slide die halfleeg is,
ongeacht hoe goed de inhoud is.

Heb je weinig te zeggen op een slide, dan worden de elementen groter. Niet het gat. Een getal
dat de slide draagt mag 48pt of 60pt zijn en de hele bovenhelft nemen. Twee kolommen proza
mogen tot de onderrand doorlopen. Wat je niet doet is drie kleine kaartjes bovenaan hangen en
de rest wit laten.

**"Groter" betekent grotere letters en meer inhoud, niet hogere dozen.** Dit is de val, en hij
is bij het bouwen makkelijker in te lopen dan hij klinkt: je maakt de blokken zo hoog dat ze de
zone vullen, laat de tekst bovenin staan, en levert vier kaarten af waarvan de onderste helft
leeg gekleurd vlak is. Op de render leest dat als een onafgemaakte slide, en het is precies
hetzelfde defect als een kale onderkant — alleen nu ín de blokken.

Dus: **een gevuld blok is zo hoog als zijn inhoud**, plus marge. Vult de compositie de zone
daarmee niet, dan is het antwoord niet een hoger blok maar een andere compositie. Vier korte
definities vullen geen vijf inch in vier kolommen; als vier rijen over de volle breedte doen ze
het wel. Staat er tekst in een blok dat toch ruimer is dan zijn inhoud, anker die tekst dan
verticaal in het midden: dan is de overgebleven lucht padding en geen gat.

## Kleur benoemt een categorie

Dit is waar de afgekeurde deck het echt verloor, en het is subtieler dan overvloed of
soberheid. Die deck had één vulling als default — een bleke lavendel — en gebruikte hem op
zes van de twaalf slides voor elk blok. Alles wat de slides van elkaar had moeten
onderscheiden, was dezelfde kleur. Dat leest niet rustig maar onverschillig.

De decks die wonnen, gebruiken kleur om te labelen. Twee kolommen die tegengestelde dingen
zeggen krijgen tegengestelde hues: teal voor wat werkt, koraal voor wat knelt. Drie
scenario's krijgen drie koppen in drie kleuren. Drie kerncijfers staan op navy, teal en
oranje, en juist doordat ze verschillen ziet de lezer dat het drie verschillende soorten
uitspraken zijn.

De vraag is dus niet of kleur mag, maar of hij iets zegt. Zou de lezer informatie kwijtraken
als het verschil wegviel? Dan is het verschil er terecht. Zo niet, dan is één accent genoeg
en houd je de rest neutraal.

Er is een betekenislaag die vastligt en die je aanhoudt: grapefruit is kost of waarschuwing,
emerald is baat of positieve waarde, navy is structuur en totaal, oranje is resultaat en het
punt waar het om gaat. Sky en royal zijn vrij voor categorieën zonder eigen lading.

Verzadigde vlakken mogen. Een volle navy kaart met een wit getal erop, een volle oranje
accentbalk, een teal kolomkop: dat is de taal van de winnende decks. Wat niet werkt is
verzadiging zonder onderscheid, en wat ook niet werkt is één bleke tint over alles heen.

## Eén drager, en die is groot

Elke slide heeft één element dat de boodschap draagt. Eén getal, één zin, één beeld, één
verhouding. Al het andere ondersteunt dat.

De toets: bekijk de render kleiner of met samengeknepen ogen. Het element dat overblijft moet
de drager zijn. Springt er niets uit, dan is de slide een verzameling en geen argument.
Springen er twee dingen uit, dan is er geen nadruk maar ruis.

Een dragend getal is echt groot. In de winnende decks staan getallen van 48pt naast elkaar in
een rij, en een enkel getal dat de slide draagt gaat naar 60pt. Een getal van 20pt in een
kaartje van 12pt tekst draagt niets.

## Variatie over de deck

Twee opeenvolgende slides dragen niet dezelfde vorm, tenzij het bewust een reeks is die de
lezer als reeks moet zien.

De afgekeurde deck had op negen van de twaalf slides dezelfde afsluiting: een navy band
onderaan met één regel conclusie. Dat is een goed instrument en het is één keer sterk. Negen
keer is een gewoonte, en de lezer leest hem de derde keer al niet meer.

Kijk in `assets/maatstaf/` wat de breedte van het repertoire is: een rij grote getallen, twee
kolommen met gekleurde koppen, een stroomschema over twee rijen, een genummerd raster, een
tabel naast een native grafiek, een citaat over een foto, een adviesslide met een getinte
band boven en een besluitband onder. Dat zijn geen tien recepten maar tien bewijzen dat er
veel meer kan dan een kaartenrij.

## Proza mag de exhibit zijn

Twee goed gezette kolommen met een conclusie eronder is een compositie, geen tekstslide. Twee
van de sterkste slides in de maatstaf zijn precies dat: kop links teal, kop rechts koraal,
onder elke kop drie korte alinea's, onderaan één regel die het samenvat.

De eis is niet dat er een diagram op staat. De eis is dat er een vorm is die het argument
draagt. Een bulletlijst in een placeholder is dat niet; twee gezette kolommen met een
kleurcode en een sluitregel wel.

## Typografie erft

Het sjabloon zet de titel op 24pt Gotham Bold in kapitalen en de subregel op 14pt Montserrat
in kapitalen. Daar blijf je af, want dat komt uit de layout en niet van jou.

In je eigen vormen: Montserrat voor labels, kolomkoppen en getallen, Lato Light voor alles wat
gelezen wordt. Gotham Bold schrijf je nooit zelf. Elke run in een eigen vorm krijgt een
expliciete `<a:latin/>`, anders staat er Calibri (zie `sjabloon.md`, Valkuilen).

Ondergrenzen: bodytekst niet onder 12pt, en 10pt alleen voor een voetnoot in themagrijs.
Navy op verzadigd oranje pas vanaf 14pt, en niet voor een lange alinea. Wit staat op navy en
royal; op oranje, grapefruit, sky en emerald staat navy, want die vullingen zijn te licht voor
witte tekst.

Er is geen maximum aan het aantal tekstgroottes per slide. Er is wel een verschil tussen een
hiërarchie en een verzameling: als je niet kunt uitleggen waarom een maat afwijkt, wijkt hij
niet af.

## Wat hier niet staat

Geen patroonnamen om uit te kiezen. Geen verplichte afsluitband. Geen minimale vulverhouding
per blok, geen maximale regelbreedte, geen maximum aantal tekstgroottes. Geen tabel met
kaartbaselines.

Die regels bestonden en ze hebben de decks niet mooier gemaakt. Wat de decks mooier maakt is
dat iemand naar de render kijkt en ziet dat het nog niet goed is.
