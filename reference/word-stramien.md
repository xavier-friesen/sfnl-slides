# Word-stramien — wat er in `SFNL_Word_sjabloon.dotx` staat

De feiten van de Word-route, nagemeten op `assets/word/SFNL_Word_sjabloon.dotx` op
27 augustus 2026. Elk getal hieronder komt uit het bestand en niet uit een handboek.

**Het sjabloon is een stijlendrager en geen voorbeeldpagina.** De body van
`word/document.xml` bestaat uit één lege alinea en een `sectPr`. Er is niets om na te
tekenen: er staat geen voorblad in, geen voorbeeldkop, geen voorbeeldtabel. Alles wat het
sjabloon te bieden heeft zit in `styles.xml`, `theme1.xml`, `numbering.xml` en de vijf kop- en
voetteksten. De bouwroute componeert het document dus zelf uit die stijlen.

Daaruit volgt de bouwregel: **erven, niet herdefiniëren.** Je begint van het `.dotx`, laat elk
onderdeel byte-voor-byte staan en schrijft alleen een nieuwe body. Dat is hetzelfde principe
als `add_slide.py` in de deckroute, waar de layout de opmaak levert en het script alleen de
tekst. Wie in plaats daarvan een vers `.docx` opbouwt en de stijlen nabouwt, verliest het
thema, de kop- en voetteksten, het logo en de nummering, en merkt dat pas op papier.

De kleuren en de letterfamilies staan in `reference/merk.md`; dit bestand herhaalt ze alleen
waar het de gemeten waarde ín het sjabloon rapporteert. Voor de scripts komen ze uit
`scripts/gedeeld/merk.py` en nooit uit een letterlijke waarde in de code.

---

## 1. Het blad

| wat | waarde in het bestand | omgerekend |
|---|---|---|
| `w:pgSz` | `w=11900 h=16840` twips | 209,9 × 297,0 mm |
| `w:pgMar` boven/onder/links/rechts | `1440` twips elk | 25,40 mm rondom |
| `w:pgMar w:header` / `w:footer` | `708` twips | 12,49 mm |
| zetspiegel breed | 11900 − 2 × 1440 = 9020 twips | 159,10 mm |
| zetspiegel hoog | 16840 − 2 × 1440 = 13960 twips | 246,20 mm |
| `w:defaultTabStop` | `720` twips | 12,70 mm |
| `w:titlePg` | aanwezig | eerste pagina heeft eigen kop en voet |
| `w:cols w:space` | `708` twips | één kolom |
| `w:docGrid w:linePitch` | `360` | — |

En let op wat een renderer daarmee doet: **LibreOffice rondt de bladmaat af naar exacte A4**
(595,3 × 841,9 pt, nagemeten op een gedrukte PDF), Word niet. Een PDF die je maakt om ernaar te
kijken is dus 0,1 mm breder dan het document. Dat is prima om te kijken en het is de reden dat
zo'n PDF geen drukwerk is.

**A4 is het niet precies.** Word schrijft echte A4 als `11906 × 16838`; hier staat
`11900 × 16840`. Dat is 0,11 mm smaller en 0,04 mm hoger dan A4. Op papier onzichtbaar, maar
het is de reden dat een zetspiegel van 159,10 mm uitkomt en niet van 159,20 mm, en een script
dat de zetspiegel narekent uit "A4 min marges" komt er 0,1 mm naast. Reken uit `pgSz`, niet
uit A4.

## 2. Kop- en voetteksten, en welke waar staat

Vijf onderdelen voor drie posities. Dit is de plek waar de bestandsnamen misleiden: `header2`
is de **eerste** pagina en `header1` de rest.

| `sectPr`-verwijzing | onderdeel | inhoud |
|---|---|---|
| `headerReference type="first"` | `header2.xml` | het logo als **PNG**, links, met een reeks harde spaties ervoor |
| `footerReference type="first"` | `footer3.xml` | een tabel van 3 × 3005 twips (53,0 mm per cel), alle cellen leeg |
| `headerReference type="default"` | `header1.xml` | één lege alinea in `Koptekst`. Niets |
| `footerReference type="default"` | `footer2.xml` | het logo als **JPG**, plus het paginanummer rechts in een frame |
| `footerReference type="even"` | `footer1.xml` | het paginanummer rechts, zonder logo |

**`footer1.xml` wordt nooit getoond.** Een `even`-verwijzing werkt alleen als
`w:evenAndOddHeaders` in `settings.xml` staat, en dat staat er niet. Het onderdeel is dood
gewicht — nuttig om te weten wanneer je zoekt waarom een wijziging in de voettekst niets doet.

Wat dat samen oplevert: **pagina 1 draagt het grote logo in de kopregel en een lege
contactstrook in de voet; pagina 2 en verder dragen een lege kopregel en het kleine logo met
het paginanummer in de voet.** Pagina 1 heeft dus geen paginanummer, en dat is correct.

**Het logo op pagina 1 staat er met spaties.** `header2` is één alinea in `Koptekst` met
`jc="both"` (uitgevuld), daarin **49 harde spaties** verdeeld over vier runs en dan het beeld.
De horizontale positie van het logo is dus de breedte van 49 spaties in Lato Light 12 pt.
Nagemeten in de render van een gebouwd document, met de echte Lato Light geïnstalleerd: de
zichtbare inkt loopt van **68,7 tot 122,1 mm** vanaf de linkerbladrand, dus 53,4 mm breed
binnen een kader van 59,9 mm (de rest is transparante rand in de PNG). Links blijft 68,7 mm
over en rechts 88,0 mm: het logo staat **9,7 mm links van het midden** van het blad, en dat is
niet gecentreerd en ook niet links uitgelijnd. Wie de kopregelstijl aanraakt, of op wiens
machine een andere letter wordt gesubstitueerd, ziet het logo verschuiven. De bouwroute laat de
kopregel byte-voor-byte staan en raakt dit dus niet aan; bij de volgende sjabloonrevisie hoort
hier een tab of een uitlijning te staan in plaats van spaties.

De tabstops van `Koptekst` en `Voettekst` staan op `center 4680` en `right 9360` twips
(82,6 en 165,1 mm). Die 9360 hoort bij een zetspiegel van 9360 twips en niet bij de 9020 van
dit blad: **de rechtertabstop valt 6,0 mm buiten de zetspiegel.** `header2` en `footer2`
repareren dat elk apart met een `w:tab w:val="clear"` en een eigen positie (4536 en 9020). Wie
zelf een tab in de voettekst zet, moet hetzelfde doen of hij eindigt in de rechtermarge.

## 3. De stijlen

55 stijlen. `styleId` is **Nederlands**, `w:name` Engels. Word adresseert op `styleId`, dus
`<w:pStyle w:val="Kop1"/>` werkt en `<w:pStyle w:val="Heading1"/>` niet — dat laatste valt stil
terug op `Standaard`, zonder foutmelding, en je ziet het pas aan de regelval.

### De galerij: 20 stijlen met `qFormat`

| `styleId` | `w:name` | letter | corps | kleur | verder |
|---|---|---|---|---|---|
| `Standaard` | Normal | Lato Light | 12 pt | erft (zwart) | `lang=nl-NL`, géén alinea-afstand |
| `Titel` | Title | Montserrat SemiBold | 28 pt | `#21145F` | spatiëring −0,5 pt, `kern 28`, `contextualSpacing` |
| `Ondertitel` | Subtitle | Montserrat Light | 11 pt | `#21145F` | spatiëring +0,75 pt, 8 pt eronder |
| `Kop1` | heading 1 | **Gotham Bold Regular** | 22 pt | `#21145F` | vet, spatiëring **+1,0 pt**, 12 pt erboven, `keepNext`+`keepLines` |
| `Kop2` | heading 2 | Montserrat Light | **14 pt** (sjabloon: 18) | `#21145F` | 2 pt erboven, `keepNext`+`keepLines` |
| `Kop3` | heading 3 | Montserrat Light | **12 pt** | `#21145F` (accent3) | 2 pt erboven |
| `Kop4` | heading 4 | Montserrat Light | **12 pt** | `#21145F` | cursief |
| `Kop5`, `Kop6` | heading 5, 6 | Montserrat Light | **12 pt** | `#21145F` | — |
| `Kop7` | heading 7 | Montserrat Light | **12 pt** | `#21145F` | cursief |
| `Kop8` | heading 8 | Montserrat Light | **10,5 pt** | `#21145F` | — |
| `Kop9` | heading 9 | Montserrat Light | **10,5 pt** | `#21145F` | cursief |
| `Citaat` | Quote | erft Lato Light | 12 pt | `#404040` | cursief, **gecentreerd**, 15,2 mm in aan beide kanten, 10 pt boven / 8 pt onder |
| `Duidelijkcitaat` | Intense Quote | erft Lato Light | 12 pt | `#21145F` | cursief, **gecentreerd**, 15,2 mm in, 18 pt boven en onder, **oranje lijn van 0,5 pt boven en onder** (`#FF7F40`, accent1) |
| `Lijstalinea` | List Paragraph | erft | 12 pt | erft | 12,7 mm in, `contextualSpacing` |
| `Nadruk` | Emphasis | Lato Light | — | erft | cursief (tekenstijl) |
| `Zwaar` | Strong | Lato Light | — | erft | vet (tekenstijl) |
| `Subtielebenadrukking` | Subtle Emphasis | Montserrat Light | — | `#404040` | cursief |
| `Intensievebenadrukking` | Intense Emphasis | Lato Light | — | `#21145F` | cursief |
| `Subtieleverwijzing` | Subtle Reference | Lato Light | — | `#5A5A5A` | — |
| `Intensieveverwijzing` | Intense Reference | Lato Light | — | `#21145F` | vet, spatiëring +0,25 pt |
| `Titelvanboek` | Book Title | Lato Light | — | erft | vet cursief, spatiëring +0,25 pt |

Buiten de galerij, maar wel bruikbaar: `Koptekst`, `Voettekst`, `Hyperlink` (`#425CC7`
themekleur `hyperlink`, enkel onderstreept), `TableGrid1` en `Tabelraster`.

### Vier dingen aan de stijlen die stil misgaan

1. **`Kop3` tot en met `Kop7` zijn even groot als de lopende tekst.** Geen `w:sz`, dus 12 pt
   uit `docDefaults`. Het onderscheid met een alinea is dan alleen de navy kleur en bij `Kop4`
   en `Kop7` de cursief. `Kop8` en `Kop9` zijn met 10,5 pt zelfs *kleiner* dan de tekst
   eronder. Praktisch: **de kopladder van het sjabloon is 28 – 11 – 22 – 18 – 12**, en houdt
   daarmee op — maar `bouw.py` verzet er twee van, zie hieronder. Meer dan
   drie niveaus onder de titel valt niet meer als hiërarchie te zien; wie een vierde niveau
   nodig heeft, heeft een indeling nodig en geen stijl.
2. **Alleen `Kop3` is aan het thema gebonden.** `#21145F` staat 26 keer in `styles.xml`, en
   maar 2 daarvan (`Kop3` en `Kop3Char`) dragen `w:themeColor="accent3"`. De andere 24 zijn de
   letterlijke hexwaarde. Wie het themapalet vervangt, verschuift dus `Kop3` en niets anders,
   en het document loopt intern uit elkaar.
3. **`Standaard` heeft geen alinea-afstand en geen regelafstand.** Geen `w:pPr`, dus 0 pt
   boven, 0 pt onder, regelafstand enkel. Twee alinea's achter elkaar raken elkaar. Zie §7.
4. **`Citaat` en `Duidelijkcitaat` zijn gecentreerd.** Dat is Word's eigen keuze uit het
   Office-thema en niet een SFNL-besluit; in een werkdocument leest een gecentreerd citaat van
   vier regels slechter dan een links uitgelijnd citaat. `Duidelijkcitaat` is wel de enige
   plek in het hele sjabloon waar de merkoranje voorkomt (de twee randlijnen), en daarmee het
   enige merkteken dat je uit een stijl kunt halen in plaats van te tekenen.

### En één ding aan de tekenstijlen

`Zwaar` (Strong) is **Lato Light plus `w:b`**, en er is geen Lato Light Bold. Word en
LibreOffice moeten dus iets: een synthetische verzwaring, of de dichtstbijzijnde snede van de
familie. Nagemeten op een render met de echte letters geïnstalleerd: LibreOffice pakt **Lato
Regular** (400), en dat is één stap boven Light in plaats van vier. Vet leest daardoor als
"iets minder licht" en niet als nadruk. Het is de stijl van het sjabloon en de bouwroute
gebruikt hem; wie in een werkdocument écht nadruk nodig heeft, heeft er beter een kop of een
`Duidelijkcitaat` voor.

### Acht stijlen zijn `semiHidden` en staan dus niet in de galerij

`Standaardalinea-lettertype`, `Standaardtabel`, `Geenlijst`, `Paginanummer`,
`Verwijzingopmerking`, `Onderwerpvanopmerking`, `OnderwerpvanopmerkingChar`,
`Onopgelostemelding`. Ze werken wel: `footer1` en `footer2` gebruiken `Paginanummer`, en
`Standaardtabel` levert de celmarges van elke tabel.

`latentStyles` staat op `defSemiHidden="0"` met 376 uitzonderingen, dus Word toont daarnaast
zijn eigen ingebouwde stijlen zodra iemand ze gebruikt. Dat betekent ook: **er zijn geen
stijlen voor een inhoudsopgave, een bijschrift of een voetnoottekst gedefinieerd.** Gebruik je
ze, dan maakt Word ze aan uit zijn eigen ingebouwde definitie, met Aptos of de themaletter, en
niet in de huisstijl.

## 4. Het thema

`theme1.xml`, `a:theme name="SFNL themakleuren word"`, `clrScheme name="SFNL themakleuren"`,
`fontScheme name="Custom 3"`.

| slot | waarde | rol in `merk.md` |
|---|---|---|
| `accent1` | `FF7F40` | oranje |
| `accent2` | `FF595A` | grapefruit |
| `accent3` | `21145F` | navy |
| `accent4` | `66C9BA` | emerald |
| `accent5` | `425CC7` | royal |
| `accent6` | `FFFFFF` | wit |
| `hlink` en `folHlink` | `425CC7` | royal |
| `dk1` / `lt1` | `windowText` / `window` | zwart / wit |
| `dk2` / `lt2` | `44546A` / `E7E6E6` | Office-standaard, niet SFNL |

Twee dingen die hieruit volgen.

**`hlink` en `folHlink` zijn dezelfde waarde.** Een bezochte link is niet van een onbezochte
te onderscheiden. Dat is een keuze die in het sjabloon staat en die de bouwroute niet
ongedaan maakt.

**`majorFont` en `minorFont` zijn béide `Lato Light`.** Er is dus geen thema-koptletter.
Montserrat en Gotham hangen uitsluitend aan de stijlen: `Titel`, `Ondertitel` en `Kop1`–`Kop9`
zetten `w:rFonts w:ascii` letterlijk. Gevolg: **wie een stijl overschrijft of de letter van een
alinea "op standaard" zet, valt terug op Lato Light en niet op Montserrat.** Dat is de
mechanische reden dat een kop in een doorgetypt document soms plotseling in de broodletter
staat.

`w:themeFontLang` in `settings.xml` staat op `en-US`, terwijl `Standaard` zelf `nl-NL` zet.
Alles wat van `Standaard` erft is dus Nederlands; een run die de taal zelf zet of een stijl die
niet van `Standaard` erft, krijgt Engels.

## 5. De lijsten

`numbering.xml` is 94 kB en draagt **32 `abstractNum` met 32 `num`**, zonder één
`lvlOverride`. Van die 32 zijn er maar **zes verschillende vormen**; de rest is
kopieerafval uit documenten waar het sjabloon uit is gegroeid.

| vorm | `numId` | niveau 1 | niveau 2 | niveau 3 |
|---|---|---|---|---|
| Word-standaardbullet | 12–32 (21×) | `•` in **Symbol** | `o` in Courier New | `▪` in Wingdings |
| **streepje** | **2**, 5 | `-` in **Lato Light** | `o` in Courier New | `▪` in Wingdings |
| ronde bullet | 3, 4 | `•` in **Arial** | `•` in Arial | `•` in Arial |
| decimaal | 6, 7, 8 | `1.` | `a.` | `i.` |
| decimaal, zonder letterhint | 9, 10, 11 | `1.` | `a.` | `i.` |
| decimaal met sluitboog | 1 | `1)` | `a.` | `i.` |

Alle niveaus staan op `ind left=720/1440/2160` met `hanging=360` (12,7 / 25,4 / 38,1 mm, met
6,35 mm uithang); alleen niveau 3 van de decimale vormen hangt 180 twips (3,2 mm).

**Neem `numId 2` voor een opsomming en `numId 6` voor een genummerde lijst.** `numId 2` is de
enige vorm waarvan het opsommingsteken in de broodletter staat; de andere 26 halen hun teken
uit Symbol, Arial of Wingdings, en dat is een tweede letter op de pagina die niemand heeft
gekozen. Er staat geen kleur in `numbering.xml`, dus elk teken erft de kleur van de alinea.

**Nesten kost je de broodletter.** Niveau 2 van `numId 2` is een `o` in Courier New. Eén
niveau opsomming is dus de vorm die het sjabloon aankan; wie twee niveaus nodig heeft, heeft
een kop nodig.

## 6. De tabel

Twee tabelstijlen, `TableGrid1` (`customStyle`) en `Tabelraster`. `TableGrid1` heeft
`w:next="Tabelraster"`, dus wie in Word na een tabel doorwerkt krijgt de andere.

| wat | `TableGrid1` | `Tabelraster` |
|---|---|---|
| randen | enkel, `sz=4` (0,5 pt), kleur `auto` | idem |
| corps | **11 pt** (`w:sz 22`), `lang=nl-NL` | erft (12 pt) |
| celmarges | uit `Standaardtabel`: links/rechts 108 twips (1,90 mm), boven/onder 0 | idem |

Dat de 11 pt van `TableGrid1` het ook echt haalt boven de 12 pt van `Standaard`, komt door
`w:compatSetting name="overrideTableStyleFontSizeAndJustification" w:val="1"` in
`settings.xml`. Zonder die vlag zou de tabel 12 pt zijn.

De randen zijn `auto`, dus **zwart en niet navy**, en er is geen kopregelopmaak: geen vulling,
geen vet, geen `tblLook`-band. Een kopregel maak je zelf, met `Zwaar` op de runs en
`w:tblHeader` op de rij zodat hij over een paginagrens meegaat. Celmarges boven en onder zijn
0, dus tekst raakt de rand; 57 twips (1,0 mm) erbij is het minimum om dat leesbaar te maken.

## 7. Wat het sjabloon niet regelt, en wat de bouwroute daarom zelf zet

`Standaard` heeft geen `w:pPr`: **0 pt boven, 0 pt onder, regelafstand enkel.** Twee alinea's
achter elkaar raken elkaar en er is geen witlijn tussen. Het sjabloon levert dus een muur
tekst, en dat is geen vormgeving maar een gat.

Daar komt de maat van de regel bij. De zetspiegel is 159,10 mm en de broodletter is Lato Light
12 pt. Nagemeten op een gebouwd document van twee pagina's, over de zestien volle regels lopende
tekst: **91 tekens in de langste regel, gemiddeld 84.** Het leesbare bereik is 65–75 tekens;
84 zit daar een vijfde boven. De marges van
25,4 mm liggen vast — dat is het sjabloon — dus wat er overblijft is de interlinie.

De bouwroute zet daarom precies twee dingen bij, in de stijl `Standaard` zelf en niet als
directe opmaak op elke alinea:

| wat | waarde | waarom |
|---|---|---|
| `w:spacing w:after` | `160` twips = **8 pt** | een witlijn tussen alinea's, tweederde van de corpsgrootte |
| `w:spacing w:line` = `276`, `lineRule="auto"` | **1,15 ×** = 13,8 pt op 12 pt | 84 tekens per regel vragen meer interlinie dan enkel |

Het gaat in `Standaard` en niet op de alinea, om drie redenen: het erft door naar `Kop1`–`Kop9`
(die alleen `before` zetten, dus ze krijgen er ruimte onder bij), het overleeft doortypen in
Word, en het staat op één plek in het bestand in plaats van bij elke alinea. Dat de `rPr` van
`Standaard` daarbij ongemoeid blijft is de reden dat Lato Light en `nl-NL` niet sneuvelen.

Wat de bouwroute **niet** bijzet:

- **Geen `w:autoHyphenation`.** `settings.xml` heeft wel een `hyphenationZone` van 425 twips
  maar geen `autoHyphenation`, dus afbreken staat uit. Bij links uitgelijnde tekst is dat de
  goede stand. Wie uitvult, zet het aan of hij krijgt gaten van vier spaties.
- **Geen `w:evenAndOddHeaders`.** Dat zou `footer1` tot leven brengen en de voettekst op
  linkerpagina's veranderen. Een werkdocument wordt enkelzijdig gelezen.
- **Geen ingesloten letters.** Zie §8.

## 7b. De kopladder die deze route werkelijk zet

Het sjabloon is niet gewijzigd; `bouw.py` schrijft twee dingen om in `styles.xml` van de kopie.
Beide staan als constante in `KOPLADDER` en worden per bouw in het verslag gemeld, zodat er geen
maat verzet wordt die niemand heeft gezien.

| stijl | sjabloon | deze route | waarom |
|---|---|---|---|
| `Kop2` | 18 pt | **14 pt** | 18 tegen een brood van 12 is een sprong van anderhalf. Op een notitie van twee of drie pagina's, waar drie of vier secties op één blad staan, leest dat als een rapportkop. Op 14 houdt de kop zijn rang en neemt hij geen regel meer dan hij nodig heeft |
| `Kop3`, `Kop4` | erven 12 pt | **12 pt, ingeschreven** | de maat verandert niet, de herkomst wel. Ze droegen geen eigen `w:sz` en erfden van `docDefaults`; verzet iemand ooit de standaardmaat, dan schuift de hele kopladder mee zonder dat er aan de koppen iets is veranderd |

**En `Kop1` is de titelrang en geen sectiekop.** Een werkdocument heeft één ding op dat niveau en
dat is de titel; alles daaronder is een sectie. `#` uit de bron wordt daarom een `Kop2`, `##` een
`Kop3`, en zo verder tot de bodem van het sjabloon bij `Kop9`.

Dat was niet zo, en het defect was op de pagina te zien en in de XML niet: `#` werd een `Kop1` van
22 pt, en op een gespreksnotitie van drie pagina's stonden er vier van — elk zo luid als de titel,
dus vier titels op één stuk. De ladder die de lezer nu ziet is 28 voor de titel, 11 voor de
ondertitelregel, 14 voor een sectie en 12 voor een subsectie, met het brood ook op 12.

Wat daaruit volgt voor `Kop3`: die is even groot als de lopende tekst en onderscheidt zich door
zijn familie (Montserrat Light tegen Lato Light) en door navy, niet door zijn corps. Dat is een
smalle marge en het is een bewuste keuze. Wie een derde niveau nodig heeft dat écht als kop moet
lezen, heeft meestal geen derde niveau nodig maar een tweede sectie.

## 8. De letters, en waarom Gotham het probleem is

`settings.xml` heeft **geen `w:embedTrueTypeFonts` en geen `w:saveSubsetFonts`**. De letters
reizen dus niet mee in het bestand: Lato Light, Montserrat Light, Montserrat SemiBold en
Gotham Bold Regular moeten op de machine van de lezer staan. `fontTable.xml` noemt er elf:
`Aptos`, `Arial`, `Courier New`, `Gotham Bold Regular`, `Lato`, `Lato Light`,
`Montserrat Light`, `Montserrat SemiBold`, `Symbol`, `Times New Roman`, `Wingdings`.

`Aptos` staat erbij zonder in één stijl te worden gebruikt. Het is de standaardletter van
Word 365 en het is binnengekomen via de ene lege alinea in `document.xml`, die als directe
opmaak `w:rFonts w:eastAsia="Aptos"`, `w:kern 2`, `w:sz 22` en `w14:ligatures` draagt. Dat is
het derde ding om te weten over die alinea: **hij staat op 11 pt en niet op de 12 pt van
`Standaard`.** Wie het sjabloon opent en in die alinea begint te typen, typt in 11 pt Lato
Light met directe opmaak eroverheen. De bouwroute gooit de alinea daarom weg en schrijft verse
alinea's zonder directe opmaak.

**Gotham Bold Regular is de letter van `Kop1` en is commercieel (Hoefler&Co).** Hij mag de
plugin niet in — zie `merk.md` §2 — en hij staat niet in een sandbox en niet op de machine van
een klant. Word en LibreOffice substitueren dan stil: geen melding, wel een andere breedte, en
dus een andere regelval en een kop die van één naar twee regels springt. Bij een kop van 22 pt
over 159 mm is dat het verschil tussen een pagina die klopt en een pagina die scheef staat.

De letternaam in het sjabloon is `Gotham Bold Regular` en niet `Gotham Bold` — vier keer, in
`Kop1` en `Kop1Char`, als `w:ascii` en `w:hAnsi`, plus één keer in `fontTable.xml`. Wie op
`Gotham Bold` zoekt, vindt hem niet.

De terugval is **Montserrat SemiBold**, de letter die `Titel` ook al gebruikt. Die keuze wordt
expliciet in het bestand geschreven en niet aan Word overgelaten, en bij de oplevering staat
erbij wélke van de twee erin staat.

## 9. Het logo, twee keer, en één keer te veel

| plek | bestand | pixels | `wp:extent` | `a:ext` | dpi | bytes |
|---|---|---|---|---|---|---|
| `header2` (pagina 1) | `media/image2.png` | 934 × 251, RGBA | 59,88 × 16,03 mm | 61,00 × 16,33 mm | 396 | 10.268 |
| `footer2` (pagina 2+) | `media/image1.jpg` | 934 × 251, RGB | 37,58 × 10,06 mm | 38,24 × 10,23 mm | 631 | 52.399 |

De interne naam van de PNG is `logo_SFNL_transparant_kleur.png`, die van de JPG
`logo_SFNL_kleur.jpg`. Zelfde 934 × 251 pixels, zelfde tekening.

**De JPG hoort er niet te zijn.** Hij is 5,1 × zo groot als de PNG voor dezelfde tekening, hij
heeft geen alfakanaal en hij is progressief gecomprimeerd met een kwantisatietabel. Een logo
is een vlakke tekening met harde randen op wit: precies de inhoud waar JPEG ringing om de
randen legt, en dat zie je op 631 dpi in druk. De PNG is RGBA en 42 kB kleiner. Bij de
volgende sjabloonrevisie gaat `image1.jpg` eruit en verwijst `footer2` naar `image2.png`.

**En de twee maten in elk beeld verschillen.** `wp:extent` is wat Word voor de opmaak
gebruikt; `a:ext` in `pic:spPr` is de eigen transformatie van het beeld. Ze lopen 1,87 % (PNG)
en 1,74 % (JPG) uit elkaar, dus het beeld wordt in zijn kader geperst. Daarnaast is de
verhouding van de pixels 3,7211 en die van het kader 3,7365: **0,41 % horizontaal uitgerekt.**
Niet zichtbaar, wel meetbaar, en het is de reden dat de gemeten 61,0 × 16,3 mm uit `a:ext`
niet gelijk is aan de 59,9 × 16,0 mm die er op papier staat.

De bouwroute raakt geen van beide beelden aan. Ze zitten in de kop- en voettekst, die
byte-voor-byte wordt overgenomen.

## 10. Voor de scripts

Wat een bouwscript moet doen om van het `.dotx` een `.docx` te maken, in de volgorde waarin
het misgaat als je het overslaat:

1. **`[Content_Types].xml`.** De override voor `/word/document.xml` staat op
   `application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml`. Zolang
   dat er staat, is het bestand een sjabloon, hoe je het ook noemt. Vervang `template.main`
   door `document.main`. Dit is de enige verplichte wijziging buiten de body.
2. **De openingstag van `w:document` en de hele `w:sectPr` letterlijk overnemen.** Die tag
   draagt 30 namespace-declaraties waar `w14`, `wp14` en `mc:Ignorable` bij horen; die zelf
   opschrijven is een lijst die je fout krijgt. De `sectPr` draagt de vijf kop- en
   voetverwijzingen, `pgSz`, `pgMar` en `titlePg` — vijf dingen die je niet wil hertypen.
3. **De ene lege alinea weggooien.** Zie §8: hij draagt directe opmaak op 11 pt.
4. **Alle andere onderdelen ongewijzigd doorgeven**, in dezelfde volgorde in het zip-archief.
   Dat is wat "erven" hier concreet betekent: `styles.xml`, `theme1.xml`, `numbering.xml`,
   `settings.xml`, de vijf kop- en voetteksten, beide beelden, `fontTable.xml` en de drie
   `customXml`-onderdelen.
5. **`docProps/core.xml` leegmaken.** Er staat een naam in (`dc:creator` en
   `cp:lastModifiedBy`) en een `cp:lastPrinted` van 19 april 2024. Een gegenereerd document
   dat naar buiten gaat hoort niet de auteursnaam van het sjabloon te dragen.
6. **Alleen dan de twee toegestane patches**, en elk gemeld in het bouwverslag: de
   alinea-afstand in `Standaard` (§7) en, als Gotham ontbreekt, de vier `Gotham Bold Regular`
   in `Kop1` en `Kop1Char` (§8).

Er is geen `python-docx` en geen `lxml` voor nodig. Een `.docx` is een zip met XML erin;
`zipfile` en `xml.etree` uit de stdlib doen het, en dan is meteen duidelijk uit welk onderdeel
welk stuk komt. Dat is dezelfde afweging als in `scripts/rapport/lees_docx.py`, en de reden
staat in `requirements.txt`.
