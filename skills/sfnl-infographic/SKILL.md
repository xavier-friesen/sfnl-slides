---
name: sfnl-infographic
description: >
  Bouw een losse infographic in de huisstijl van Social Finance NL: zonder titel, zonder
  omlijning, als SVG of als kant-en-klare PowerPoint-slide — blanco, in de contentzone van een
  getitelde slide, of als kolom van een tweeluik. De
  compositie ontwerp je per infographic zelf, met een primitievenlaag die de kleur-, maat- en
  uitlijnregels van SFNL afdwingt, en met een renderloop die het resultaat echt bekijkt.
  Gebruik deze skill wanneer de gebruiker een infographic, visual, schema, tijdlijn,
  processchema, verdeling, cijferbeeld of dataviz voor SFNL wil maken. Trigger op "maak een
  infographic", "SFNL infographic", "visual in huisstijl", "schema van dit proces", "beeld
  van deze cijfers", "zet dit in een plaatje", "visualiseer dit", "svg in onze stijl", of
  wanneer iemand een los beeld wil dat in een deck, rapport, Word-document of mail wordt
  geplakt. Het beeld gaat ook rechtstreeks de zusterskills in: als exhibit in een
  HTML-document van `sfnl-design-documents`, als figuur in een gezet rapport van
  `sfnl-rapport-opmaak`, of op een slide van `sfnl-slides`. Voor een hele presentatie
  gebruik je `sfnl-slides`, voor kort drukwerk `sfnl-design-documents`, voor een lang
  rapport `sfnl-rapport-opmaak`, voor een rapportspread in Affinity `sfnl-rapport`, en
  voor een HTML-dashboard of Word-document `sfnl-design`.
---

# SFNL-infographic

Een losse visual bouwen die ergens ánders in komt te staan. Dat is de hele opdracht, en het is
wat deze skill onderscheidt van sfnl-slides: er is geen titel, geen oranje dash en geen kader,
want die draagt de container. Wat er overblijft is de compositie, en die is elke keer opnieuw
een ontwerpbeslissing.

Er is geen patroonbibliotheek en geen validator die je vorm afkeurt voordat je hem gezien hebt.
Wat er wel is: een maatstaf om aan te toetsen, een primitievenlaag die de kleur-, contrast- en
uitlijnregels afdwingt en die echt kan meten, en een renderloop die het enige oordeel over de
vorm geeft.

**Eén onderscheid loopt door de hele skill heen, dus hier eerst.** Een **figuur** is een vorm
waarin een meting een coördinaat, een lengte, een dikte of een hoek bepaalt: de x van een
moment is zijn datum, de lengte van een staaf is zijn waarde, de dikte van een stroom is zijn
aandeel. Verandert het getal, dan verandert de tekening. Een **rooster** is een rij of een
raster dozen: kaarten, kolommen, banden. Daar bepaalt geen enkele meting iets, dus de tekening
blijft hetzelfde welk getal je er ook in zet.

Vijfenveertig van de zesenveertig vormen in het woordenboek zijn een figuur. Een rooster staat
er niet in — het is een manier om tekst te ordenen, en dat is soms precies goed, maar het is
geen antwoord op een vraag naar hoeveel, wanneer of waarheen. De stappen hieronder zijn er
grotendeels op gebouwd dat de figuur de gewone uitkomst is en het rooster de bewuste.

**Alle paden in dit document staan vanaf de plugin-map**, dus `${CLAUDE_PLUGIN_ROOT}` — niet
vanaf de map waarin dit bestand staat en niet vanaf het project. `reference/infographic-vormentaal.md`
is dus `${CLAUDE_PLUGIN_ROOT}/reference/infographic-vormentaal.md`, en `svg.py` staat in
`${CLAUDE_PLUGIN_ROOT}/scripts/infographic/`.

**Deze skill deelt zijn plugin met drie andere**, en dat verandert twee dingen ten opzichte van
de losse versie. De scripts van `sfnl-slides` liggen ernaast in `${CLAUDE_PLUGIN_ROOT}/scripts/`,
dus de PowerPoint-route van stap 4B is er altijd en er is niets op te zoeken. En de huisstijl-
letters liggen er ook: `assets/documenten/fonts/` draagt Montserrat en Lato als woff2 voor de
drukroutes, en `svg.py` leest diezelfde bestanden als metriekbron. De regelafbreking is dus
gemeten en niet geschat, ook op een kale machine zonder netwerk — wat vóór de plugin het gewone
geval was.

## Voordat je begint

Lees dit één keer voor de hele opdracht, niet per infographic:

1. `reference/infographic-vormentaal.md` — de maatstaf. Wat een titelloze, kaderloze
   SFNL-visual goed maakt, en de dertien regels op volgorde van effect.
2. `assets/infographic/vormen/vormenwoordenboek.png` — **dit is de belangrijkste**. Zesenveertig vormen,
   structureel, zonder kleur en zonder opmaak, geordend naar de vraag die ze beantwoorden.
   Kijk ernaar vóór je een vorm kiest, elke keer. De indeling volgt de Visual Vocabulary van
   de Financial Times; de tekeningen zijn van deze skill.
3. `reference/infographic-vormkeuze.md` — de vormtoets: welke vorm past bij déze opdracht, wat elke vorm
   aan gegevens eist, hoeveel erin past en welk canvas hij wil. Dit bestand maakt stap 2
   uitvoerbaar; zonder die tabel is de vormkeuze een gevoel.
4. De docstrings van `scripts/infographic/svg.py` en `scripts/infographic/schets.py` — de primitieven waarmee je tekent
   en schetst, en waarom ze er zo uitzien. Lees de docstrings, niet de hele bestanden. In
   `schets.py` staan twee routes: `schets_vrij()` met zes figuurhelpers, en `schets()` met
   rijen en kolommen. De eerste is de gewone. Onderaan staat hoe de schetsen als canvas
   worden voorgelegd.
5. `assets/infographic/maatstaf/` — vijf afgemaakte infographics. Dit **is** de norm voor het eindresultaat:
   zo ziet een opgeleverde SFNL-infographic eruit. **Kijk naar één of twee**, en kies op vorm en
   register: `m1` sankey op wit, `m2` tijdlijn op schaal, `m3` divergerende staaf met twee
   coderende hues, `m4` rasterplot op vierkant, `m5` waterval op een PowerPoint-slide. Lees ook
   `assets/infographic/maatstaf/LEESMIJ.md` — daar staat in één alinea wat ze gemeen hebben.
6. `assets/infographic/voorbeeld/*.py` — de bouwscripts. In elke docstring staat wat er in de eerste
   versie misging en waarom de tweede anders is. Lees er één, van het voorbeeld dat je bekeek.

**Kijk niet naar alles.** De zeven PNG's samen kosten ongeveer 8k tokens, meer dan de halve
SKILL.md. Het vormenwoordenboek plus één of twee maatstaven is genoeg, en dat is de bedoeling.

Draai dan:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/infographic/preflight.py --herstel
```

Dat zegt of de meting echt is, of er een renderer is, of de deckscripts en het sjabloon
ernaast liggen, en of node plus de canvashelper voor de conceptkeuze er zijn. Zonder renderer
bouw je blind; dat staat onderaan onder **Als iets ontbreekt**.

Twee dingen om te weten bij de uitkomst. `meting_echt` is niet "er is een fontbestand": het
ingesloten Montserrat is een woff2, en zonder `brotli` krijg je dat bestand niet open — dan
staat er een pad in `fonts` en is de afbreking tóch geschat. Daarom meet `preflight.py` het
echt na en zet `--herstel` `brotli` erbij. En `sfnl_slides_scripts` is een bestaanscontrole en
geen zoekactie: die scripts horen in dezelfde plugin te staan, dus staat er `null`, dan is de
checkout niet compleet.

## Stap 1 — Intake: de inhoud, dan twee widgets

Weet je een antwoord al uit de opdracht, sla die vraag over. Vraag nooit iets wat er al staat.

### Eerst de inhoud, in gewone tekst

- **Wat moet de lezer hieraan overhouden, in één zin?** Dit is de belangrijkste vraag en de enige
  die je niet kunt overslaan. Zonder antwoord weet je niet wat de bewering draagt, en dan wordt
  de infographic een verzameling.
- **Waar komt hij te staan, en draagt die plek een titel?** Een slide met een titel erboven, een
  rapportpagina, een Word-document, een mail, of los rondgaand. Dit antwoord bepaalt of er een
  sluitregel nodig is. Draagt de plek geen titel, dan is dat geen opdracht om er zelf een te
  tekenen; de bewering komt dan uit de figuur zelf, uit een drager of uit een sluitregel
  (vormentaal §1).

  **En vraag dóór als die plek een van de zusterskills is.** Komt het beeld in een document van
  `sfnl-design-documents` of in een rapport van `sfnl-rapport-opmaak`, dan is dit niet alleen
  een vraag over de titel maar over het **canvas en de maatladder**: het kader daar is 680, 537
  of 325 px breed, en een beeld dat op 960 pt is getekend krimpt daarin met factor 1,9 — zijn
  labels van 11 pt komen op 5,9 pt uit, onder de leesvloer, zonder dat er iets in de markup
  fout staat. Dat repareer je niet achteraf. Lees `reference/samenstellen.md` vóór stap 2, want
  dit antwoord bepaalt daar de canvastoets.
- **Welke cijfers, en waar komen ze vandaan?** Vraag naar eenheid, periode en bron. Zonder
  eenheid en peildatum gaat een getal er niet op.

### Dan de telling, en die is een poort

**Tel de categorieën en de perioden vóór je verder gaat.** Twee uitkomsten betekenen dat dit
geen getekende infographic wordt, en dat weet je nu of pas na het bouwen:

| wat je telt | dan is het | route |
|---|---|---|
| meer dan zes categorieën, of een echte reeks over tijd | een **native grafiek** | stap 4C |
| drie perioden of meer × twee grootheden of meer | een **tabel** | stap 4C |
| allebei waar | grafiek, tenzij de lezer exacte waarden moet kunnen aflezen — dan tabel, of grafiek plus tabel | stap 4C |

Acht gemeenten × drie jaar is beide. Een getekend staafje is geen grafiek: het veroudert
zonder dat iemand het merkt en niemand kan het bijwerken. Zeg dit tegen de gebruiker vóór de
brainstorm, want het verandert wat er te schetsen valt.

### Widget 1 — formaat en maat

`AskUserQuestion`, twee vragen. Deze twee eerst, want ze bepalen wat er in stap 2 te schetsen
valt: een band van 960 × 320pt en een hele slide van 13,33 × 7,50 in vragen een andere
plattegrond.

1. **In welk formaat?**
   - *SVG* — schaalt oneindig, tekst blijft tekst, te bewerken in Affinity of Illustrator. Je
     krijgt een SVG plus een PNG op 2×, en op verzoek een PDF.
   - *PowerPoint-slide* — één slide op het SFNL-sjabloon, te kopiëren in elk deck en daarna in
     PowerPoint zelf te bewerken. Welk vlak dat wordt, staat in vraag 2: het blanco canvas is
     niet de enige plek waar een infographic op een slide past, en het is vaak de slechtste.
   - *Exhibit in een document of rapport* — het beeld komt in een HTML-document van
     `sfnl-design-documents` of in een gezet rapport van `sfnl-rapport-opmaak`. Dat is nog steeds
     een SVG, maar op het canvas van die route en met hún maatladder, en de oplevering is een
     fragment of een figuren-regel in plaats van een los bestand. Kies dit zodra de gebruiker
     zegt dat het beeld in zo'n stuk komt te staan; de rest van de keten staat in
     `reference/samenstellen.md` en de maat staat vast in vraag 2.
2. **Welke maat?** Drie lijsten, want de routes hebben een ander vlak.

   **Bij SVG** is dit antwoord **voorlopig**: het canvas gaat in stap 2 mee met de vorm die
   wint, niet andersom. Zeg dat erbij in de vraag, anders leest de keuze als vast en verlies je
   in de canvastoets precies de vormen die een ander vlak willen — de naaf, de ring, de radar,
   het rasterplot, de geordende staaf met acht items.
   - *Band, 960 × 320pt* — een strook onder een titel of tussen twee alinea's. De meest bruikbare.
   - *Contentzone, 901 × 360pt* — vult exact de contentzone van een SFNL-slide.
   - *Hele slide, 960 × 540pt* — 16:9, voor een beeld dat de slide vult.
   - *Staande kolom, 460 × 500pt* — naast een tekstkolom in een rapport of in Word.

   - *Vierkant, 560 × 560pt* — voor een naaf, een cirkel of één figuur; ook voor mail en social.

   Staande kolom (460 × 500 of 640pt) en rapportspread (1191 × 780pt) staan ook in `CANVAS`;
   noemt iemand die via "Other", dan gelden ze. En de maat is geen keuze voor het leven: past
   de compositie in stap 5 niet in de hoogte, dan verander je éérst de hoogte (vormentaal §5).

   **Bij een exhibit in een document of rapport ligt het vlak vast**, want het is het kader van
   die route en niet een keuze van dit beeld. Zes maten, en ze staan als `CANVAS`-sleutel klaar.
   **Ze zijn in px en niet in punten**, want dat is de eenheid van de container en van zijn
   meetapparaat — zie stap 4D:
   - *`doc-breed`, 680 × 372 px* — de volle zetspiegel van een SFNL-document. De gewone, en het
     is de maat van het gemeten voorbeeld in `documenten-vormentaal.md` §11.
   - *`doc-kolom2`, 325 × 244 px* — één van twee kolommen.
   - *`doc-kolom3`, 207 × 207 px* — één van drie kolommen. Weinig ruimte: hier past één figuur
     en geen samenstel.
   - *`rap-breed`, 650 × 366 px* — de volle zetspiegel van een gezet rapport.
   - *`rap-kolom`, 537 × 302 px* — de tekstkolom in het layoutmodel `breed`.
   - *`rap-dubbel`, 310 × 233 px* — een kolom in het model `dubbel`.

   De hoogte mag groeien en de breedte niet — dat is de hele regel. Meer inhoud nodig: rek de
   `viewBox` in de hoogte en houd de breedte gelijk, precies zoals de infographic van
   `documenten-vormentaal.md` §11 van 268 naar 372 px ging en zijn letters hield. En zet de
   maten met `Maten.voor("document")` of `Maten.voor("rapport")` en niet met de hand: die
   presets dragen de ladder van de container én zetten de eenheid, want een beeld dat zijn eigen
   16pt-body meeneemt, zet een zevende maat op een pagina die er zes heeft.

   **Bij PowerPoint** ligt het vlak wél vast zodra je het gekozen hebt, en er zijn er drie. Ze
   staan hier op volgorde van hoe vaak ze het goede antwoord zijn, en dat is niet de volgorde
   waarin je ze zou verwachten:
   - *Contentzone van een getitelde slide, layout 19 — 12,52 × 5,00 in op x 0,48, y 1,93.* De
     slide draagt zijn eigen titel, subregel en oranje dash uit de layout, en de infographic
     staat eronder in de contentzone. **Dit is meestal de goede.** Een band die het in SVG doet,
     past hier één op één: 12,52 × 5,00 in is 901 × 360pt, precies `CANVAS["contentzone"]`. En
     het lost vormentaal §1 op de rustigste manier op — de bewering staat in de titel van de
     slide, dus de infographic hoeft er zelf geen te dragen. Vraag dan wel de titeltekst uit.
   - *Blanco slide, layout 17 — 13,33 × 7,50 in.* Geen titel, geen dash, geen logo. Voor een
     beeld dat de hele slide ís. Weet wat je koopt: een hele slide vraagt ongeveer twee keer de
     inhoud van een band, en zonder titel moet de infographic de bewering zelf dragen.
   - *Eén kolom van een tweeluik, layout 21 of 22 — 5,91 × 5,00 in op x 0,48 of x 6,82.* Voor
     een beeld dat naast een tekstkolom komt te staan. 5,91 × 5,00 in is 425 × 360pt, dus dit is
     een staand vlak en geen band: een naaf, een ring, een rasterplot of een geordende staaf
     passen hier, een tijdlijn of een sankey niet.

   Dit stond hier eerder niet, en dat was een echte beperking. De PowerPoint-route kende alleen
   het blanco vlak, dus iedere infographic die in een deck terechtkwam werd een hele slide —
   ook de bandvormige, die dan de onderste helft leeg liet. Dat is dezelfde fout als dood wit
   onderin een blok, alleen een verdieping hoger.
3. **Wachten of doorbouwen?**
   - *Ik kies het concept* — je krijgt in stap 2 drie schetsen voorgelegd en er wordt gewacht.
     De default, en de goedkoopste: een verkeerd concept corrigeren kost daarna een herbouw.
   - *Bouw door* — je krijgt de schetsen en de aannames in één bericht mee terwijl er gebouwd
     wordt. Voor als je niet bij je scherm zit.

   Deze vraag stel je expliciet. De doorbouwmodus stond eerder alleen in stap 2 beschreven,
   werd nergens uitgevraagd, en dus nooit bewust gekozen.

### Widget 2 — stijl

`AskUserQuestion`, vier vragen, direct na widget 1. Dit zijn de vier knoppen die het meest
uitmaken voor hoe het beeld eruitkomt, en zonder ze neem je die keuzes zelf — en blijkt het
verschil met wat de gebruiker in gedachten had pas op de render.

1. **Hoeveel uitleggende tekst?**
   - *Geen* — alleen labels, getallen en eenheden. Het beeld doet het alleen; de container of de
     spreker vertelt de rest. **Dit is de default.**
   - *Eén regel per element* — een korte toelichting per kolom of rij, maximaal ongeveer één zin.
   - *Volledige toelichting* — twee tot drie regels per element, voor een leave-behind of een
     rapport dat zonder spreker gelezen wordt.
2. **Wat doet kleur?**
   - *Eén accent naast navy* — één hue, consequent, en die betekent één ding. De default.
   - *Kleur codeert categorieën* — meer hues, en elke hue staat voor een rol, een fase of een
     kant van een afweging. Alleen kiezen als de lezer ze apart moet houden.
   - *Alleen navy en wit* — monochroom; hiërarchie komt uit gewicht en maat. Voor een beeld dat
     naast een al kleurrijke omgeving staat, of voor zwart-witdruk.
3. **Hoeveel vlak?** Let op wat deze vraag niet is: hij gaat over de **vulling** van de
   elementen en niet over de plattegrond. "Kaarten" betekent dat een vlak een lichte vulling
   met een haarlijn krijgt, niet dat de compositie een rij kaarten wordt. Een sankey met een
   gevulde kaart eronder is nog steeds een sankey. De plattegrond kies je in stap 2.
   - *Bijna helemaal wit* — geen vulling, alleen gekleurde koppen, haarlijnen en tekst. Het
     lichte register, en waar SFNL-werk het sterkst in staat. Alle vijf de maatstaven staan
     hierin en geen van de vijf heeft één containervulling. Dit is de default op papier en op
     scherm.
   - *Kaarten* — containervullingen van 7 tot 12 procent met een haarlijn in de eigen hue. Op
     een slide met een projector achter je werkt dit beter dan het lichte register. Er is geen
     maatstaf in dit register; je hebt dus geen voorbeeld en bouwt op de vormentaal.
   - *Verzadigd* — volle vlakken met de drager erin, of een volle band die de compositie sluit.
4. **Bronvermelding?**
   - *Bronregel in het beeld* — 11pt onder de doos waar hij bij hoort, met eenheid en peildatum.
     De default zodra er cijfers op staan.
   - *De container draagt de bron* — dan blijft het beeld kaal. Noem dit bij de oplevering, zodat
     iemand het niet vergeet als het beeld los gaat rondgaan.
   - *Geen bron beschikbaar* — dan staat er geen cijfer op dat als vaststelling leest, of het
     staat er als expliciete aanname.

Vul bij vraag 3 en 4 het `preview`-veld met een schets van vier of vijf regels in tekst, want
"kaarten" en "bijna helemaal wit" betekenen voor niemand hetzelfde tot je ze naast elkaar ziet.

Antwoordt iemand niet: SVG op de band, geen uitleggende tekst, één accent, bijna helemaal wit,
bronregel in het beeld. De eerste stand stond hier eerst op "één regel per element" en dat was
een fout: dan krijgt elk element een zin die niemand besteld heeft, terwijl een beeld dat wél
toelichting nodig heeft dat op de render zelf laat zien. Het laatste register stond
hier eerst op "kaarten" en dat was ook een fout: het spreekt de default in de vraag zelf tegen,
het spreekt alle vijf de maatstaven tegen, en een stilzwijgende kaartendefault is precies hoe
een compositie een rooster wordt zonder dat iemand dat gekozen heeft.

### Wat er op het vlak komt

Dit is de volledige inventaris van een opgeleverde SFNL-infographic. Er staat niets op dat hier
niet in voorkomt:

1. de compositie — de vorm die de vormtoets haalde;
2. labels, getallen en eenheden bij de elementen;
3. één bronregel, als er cijfers op staan;
4. uitleggende tekst per element, in de stand die de gebruiker koos;
5. hoogstens één drager — een getal, verhouding, kop of begrip op displaymaat;
6. hoogstens één sluitregel onderaan.

**De eerste drie zijn er altijd, de laatste drie zijn keuzes.** Punt 5 en 6 bestaan om de
bewering te dragen, en dat hoeft alleen als de figuur hem niet zelf draagt (vormentaal §1).
Doet hij dat wel — de staaf die er twee keer zo lang uit ziet, de stroom die zichtbaar op één
post uitkomt — dan komt er geen getal op displaymaat naast en geen zin eronder. Een infographic
die alleen uit 1, 2 en 3 bestaat is een volwaardige oplevering, en vaak de rustigste.

De grens ligt bij de herhaling. Staat het getal van de drager ergens anders op het vlak ook,
dan draagt hij niet maar herhaalt hij, en dan gaat er één van de twee uit. Dat is nagemeten op
een waterval waar links `41` op displaymaat stond en boven de laatste staaf `41` op 18pt.

Een titel boven het beeld staat er niet in, een ondertitel eronder niet, en een inleidende
alinea onder de tekening ook niet. Die draagt de container. Wil de gebruiker er tóch een
kopregel op, dan vraagt hij daarom en dan geldt vormentaal §1 punt 3.

## Stap 2 — Vormkeuze: de vraag, de kandidaten, de toets

Nu weet je wat erop moet en hoe het eruit mag zien. Wat je nog niet weet is welke vorm de
boodschap wil, en dat is het enige wat er echt te ontwerpen valt. **Dit is de stap waar het het
vaakst misgaat**, en niet doordat er te weinig wordt nagedacht maar doordat de vorm al vaststond
voordat het denken begon.

Lees `reference/infographic-vormkeuze.md` erbij; daar staat de tabel met wat elke vorm eist. Werk deze vier
stappen expliciet af en schrijf ze op. Bouwen doe je pas na D.

### 2A — Wat is de vraag?

Schrijf in één zin op welke vraag de infographic beantwoordt. Niet het onderwerp, de vraag. "De
businesscase van het SIB" is een onderwerp; "houden we er onder de streep iets aan over" is een
vraag, en die stuurt je naar een waterval.

Wijs de vraag toe aan een van de negen categorieën uit het woordenboek: verandering,
rangschikking, deel van geheel, grootte, afwijking, stroom, verband, structuur, verdeling. Past
hij in twee, dan zijn dat twee kandidatenrijen. Past hij in geen enkele, dan is dit waarschijnlijk
proza of een tabel en niet een infographic.

### 2B — Minstens zes kandidaten, uit minstens drie categorieën, en minstens vier figuren

**Ga het vormenwoordenboek langs en noteer minstens zes vormen die kandidaat zijn, uit minstens
drie verschillende categorieën.** Dit is een harde ondergrens.

De reden staat in `infographic-vormkeuze.md`: met drie kandidaten uit één categorie kies je tussen varianten
van hetzelfde beeld en is de brainstorm een formaliteit. Er staan zesenveertig vormen in dat
woordenboek en de meeste komen nooit vanzelf op — een venn, een marimekko, een bulletgrafiek, een
zwembanenschema. Die zie je alleen als je kijkt.

Noteer per kandidaat de vorm, de categorie, in één regel waarom hij kandidaat is, en **welke
meting welke maat bepaalt**: "de x is de datum", "de lengte is het bedrag", "de dikte is het
aandeel", "het aantal stippen is het aantal mensen". Die laatste kolom is niet decoratief. Kun
je hem niet invullen, dan is de kandidaat een rooster en telt hij niet mee voor het quotum
hieronder.

**Minstens vier van de zes zijn een figuur.** Dat is de tweede harde ondergrens en hij staat er
omdat de zwaartekracht de andere kant op werkt: een rooster past altijd, eist niets van de
gegevens en valt daarom nooit af, dus zonder quotum is hij de laatste die overblijft. Vier van
de zes halen betekent gewoon het woordenboek gebruiken; er staan er vijfenveertig in.

### 2C — De vormtoets, en dit is de poort

Elke kandidaat langs vier toetsen. Eén nee is genoeg om af te vallen, en je schrijft op welke
toets hij niet haalde.

1. **Datatoets** — heb je wat de vorm eist? Een sankey eist dat de delen optellen tot het geheel.
   Een venn eist dat je de ómvang van de overlap kent, niet alleen de twee verzamelingen. Een
   tijdlijn eist echte datums. Heb je die niet, dan suggereert de vorm iets wat je niet weet, en
   dat is erger dan een saaie staafgrafiek. De eis per vorm staat in de tabel.

   **Valt een figuur hierop af, vraag dan één keer door voor je hem doorstreept.** Welk gegeven
   ontbreekt precies, en heeft de gebruiker het misschien wel? Vier van de vijf keer is het
   antwoord "dat kan ik opzoeken", en dan is de vorm er alsnog. Streep je hem meteen door, dan
   valt er in deze toets stelselmatig een figuur af en nooit een rooster — een rooster eist
   namelijk niets — en dat is de weg waarlangs een kaartenrij wint zonder ooit gekozen te zijn.
2. **Aantallentoets** — past het aantal erin? Een ring gaat stuk boven vier delen, een venn boven
   drie verzamelingen, een sankey boven ongeveer zes stromen. Ook de ondergrens telt: een
   verdeling met twee categorieën is een verhouding en geen verdeling.
3. **Boodschapstoets** — draagt de vorm de bewering uit de intake, of verstopt hij hem in een
   detail? Dit is de toets die het vaakst een favoriet sloopt, en dat hoort zo.
4. **Canvastoets** — welk canvas wil de vorm? Radar, venn, ring en cyclus willen vierkant;
   tijdlijn, sankey en marimekko willen breed; een geordende staaf met acht items wil hoog.

   **Deze toets laat niemand afvallen.** Hij noteert alleen wat de vorm vraagt, en pas bij de
   conceptkeuze in 2D verandert het canvas mee met de winnaar. Zo stond het hier eerst niet —
   het was "past de vorm op het canvas uit widget 1", en dat maakte van een voorlopig antwoord
   in een intakewidget een hek waar de helft van het woordenboek achter bleef staan: op een
   band van 960 × 320 valt alles af wat vierkant of hoog wil, en wat overblijft zijn brede
   vormen en het rooster.

   **In de PowerPoint-route ligt het vlak wél vast, maar er zijn er drie**, en de toets kiest
   tussen die drie in plaats van kandidaten te vellen. Wil de winnaar breed, dan is dat de
   contentzone van layout 19; wil hij de hele slide vullen, layout 17; wil hij staand of
   vierkant, dan een kolom van layout 21 of 22. Pas als geen van de drie past valt de vorm af,
   en dan noteer je welke maat hij wél had gewild — dat is een argument voor de SVG-route en
   niet voor samenpersen.

   **In de exhibitroute ligt de breedte vast en de hoogte niet**, en dat is de zuinigste van de
   drie: de kolom of de zetspiegel van de container bepaalt de breedte, en wat de vorm in de
   hoogte wil mag hij hebben. Een vorm valt hier dus alleen af op de bréédte — een sankey met
   zes stromen in een kolom van 310 px, een tijdlijn met vijf momenten in 207 px — en dan is de
   uitweg het bredere kader van dezelfde route en niet een kleinere letter. Op één na: een vorm
   die vierkant wil, wil in een smalle kolom een hoogte die de kolom niet heeft, en dan is de
   volle zetspiegel het antwoord. Noteer welk kader je nam; dat is het besluit dat `insluiten.py`
   in stap 6 naremeet.

Leg dit neer als tabel: kandidaat, de meting die de vorm draagt, vier kolommen, slotoordeel. Zo:

| kandidaat | meting → maat | data | aantal | boodschap | canvas | oordeel |
|---|---|---|---|---|---|---|
| Waterval | mutatie → staaflengte | ja, mutaties met teken | 5 stappen | ja, het saldo is de kneep | wil breed | **door** |
| Naaf | rol → plek op de omloop | ja | 5 satellieten | ja | wil vierkant | **door**, canvas wordt vierkant |
| Venn, twee | overlap → oppervlak | nee, overlap onbekend | 2 | — | — | valt af op data |
| Ring | aandeel → hoek | ja | 6 delen, te veel | — | — | valt af op aantal |
| Vier kaarten | geen | n.v.t. | 4 | zegt wie, niet hoeveel | past overal | rooster, alleen als terugval |

Drie tot vijf overlevers is gezond, en **minstens twee ervan zijn een figuur**. Blijft er één
over, dan was de lijst te kort. Overleeft alleen het rooster, dan is dat geen uitkomst maar een
signaal: ga terug naar de datatoets en kijk welk ontbrekend gegeven je in één vraag aan de
gebruiker kunt ophalen. Vallen ze allemaal af, dan klopt de vraag uit 2A niet of ontbreken er
gegevens — meld dat en vraag ernaar, in plaats van de zwakste kandidaat alsnog te bouwen.

### 2D — Schetsen van de overlevers, dan kiezen

Van drie overlevers maak je wireframes met `scripts/infographic/schets.py`. Een schets heeft geen echte
tekst, geen accentkleur en geen getal, alleen de meetkunde en de rol die erin komt — precies
zodat de gebruiker de plattegrond beoordeelt en niet de opmaak.

**Ten hoogste één van de drie is een rooster.** Overleefden er figuren de vormtoets, dan schets
je die als figuur, met de meetkunde erin: de stroom heeft dikte, de tijdlijn heeft ongelijke
gaten, de staven hebben lengte. Dit is de belangrijkste regel van deze stap. `schets.py` kon
eerst alleen rijen en kolommen tekenen, dus een brainstorm die met een sankey, een naaf en een
helling begon leverde drie keer hetzelfde roosterbeeld op — de gebruiker koos een rooster omdat
er niets anders te kiezen viel, en wat er daarna gebouwd werd was een rij dozen. Kijk naar
`assets/infographic/maatstaf/schetsen-drie-concepten.png`: twee figuren en één rooster, en je ziet meteen
dat het rooster minder zegt.

Schrijf per schets vier regels op:

- **de plattegrond in vier woorden** — "stroom die opsplitst", "tijdlijn met vijf momenten",
  "vier kolommen met kopband"
- **welke meting welke maat bepaalt** — "dikte is het aandeel", "x is de datum". Staat er bij
  één van de drie "geen", dan is dat het rooster, en dat mag er één zijn.
- **wat de boodschap draagt** — welk element de bewering op het beeld zet, en "de figuur
  zelf" is een geldig antwoord
- **wat het kost** — wat er in dit concept niet op past. Deze regel maakt de keuze mogelijk; een
  concept zonder prijs is een verkooppraatje. Bij een rooster is de prijs altijd dezelfde en je
  noemt hem hardop: dit beeld zegt wie of wat, en niet hoeveel of wanneer.

```python
import sys; sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/scripts/infographic")
from schets import (Cel, Rij, as_op_schaal, canvas_manifest, contactblad, naaf, raster,
                    rol, schets, schets_vrij, seed_helper, staven, stroom, wig)
from svg import CANVAS

c = CANVAS["breed"]
# figuur: de zes helpers geven lijsten vormen terug, dus je plakt ze achter elkaar
a = stroom(x1=230, x2=640, y=40, h=150, aandelen=[0.52, 0.26, 0.14, 0.08])
a += [rol("drager", 30, 70, 180), rol("sluitregel", 30, 250, 520)]
p_a = schets_vrij("uitvoer/concept-a.svg", c, "A — geldstroom", a,
                  artboard_="uitvoer/canvas/Main.dc.html")
# rooster: hooguit één van de drie
p_c = schets("uitvoer/concept-c.svg", c, "C — vier kolommen", rijen_c,
             artboard_="uitvoer/canvas/ConceptC.dc.html")
```

De zes helpers zijn `as_op_schaal` (afstand), `staven` (lengte), `stroom` (dikte), `naaf`
(middelpunt en omloop), `raster` (aantal) en `wig` (hoek). Alles wat daar niet in staat — een
venn, een marimekko, een kwadrant, een treemap — teken je met `vlak()`, `cirkel()`, `pad()` en
`lijn()` uit `svg.py` in de schetskleur en zet je door `schets_vrij()`. Dat kost drie regels
meer en het is nog steeds een tiende van een gebouwde infographic.

### Eerst kijk je zelf

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/infographic/render_svg.py "uitvoer/concept-*.svg" --wit --schaal 1
```

`schaal 1` en niet 2: een wireframe beoordeel je op plattegrond, niet op scherpte, en de helft
van de resolutie is hier de helft van de kosten. Zet ze met `contactblad()` onder elkaar in één
PNG en kijk ernaar — dit is jouw controle, niet die van de gebruiker, en je legt niets voor wat
je zelf niet gezien hebt. Let op: `schets()` geeft **SVG**-paden terug en `contactblad()` wil
**PNG**-paden, dus de suffix moet mee:

```python
contactblad([str(p.with_suffix(".png")) for p in paden], "uitvoer/drie-schetsen.png")
```

### Dan leg je de keuze voor op een canvas

De `artboard_=` uit het bouwscript hierboven schreef naast elke SVG ook een `.dc.html`. Zet er
een manifest bij en laat de design-skill er een canvas van maken:

```python
canvas_manifest("uitvoer/canvas/canvas.json", [
    {"bestand": "uitvoer/canvas/Main.dc.html", "canvas": c, "titel": "A — geldstroom",
     "regels": ["Plattegrond: stroom die opsplitst",
                "Meting: dikte is het aandeel",
                "Drager: de inleg, links op displaymaat",
                "Kost: de volgorde in de tijd verdwijnt"]},
    # ... B en C ...
])
```

```bash
python -c "import sys; sys.path.insert(0,'${CLAUDE_PLUGIN_ROOT}/scripts/infographic'); from schets import seed_helper; print(seed_helper())"
node <helper> --template <helperdir>/payload.template.html \
  --out drie-concepten-<onderwerp>.html --title "Drie concepten — <onderwerp>" \
  --artboard Main.dc.html --artboard ConceptB.dc.html --artboard ConceptC.dc.html \
  --canvas canvas.json
node <helper> --check drie-concepten-<onderwerp>.html
```

Publiceer dat bestand met de `Artifact`-tool en stuur de link. Het eerste artboard **moet**
`Main.dc.html` heten — dat is een eis van de helper — en de leesbare naam ("A — geldstroom")
zet je in het manifest. Roep de `design`-skill één keer aan als je niet weet waar de helper
staat: hij wordt per sessie onder een versienummer uitgepakt, dus het pad is niet vast en
`seed_helper()` zoekt hem op.

Waarom dit het contactblad vervangt, in drie punten. **De vier regels staan naast hun eigen
schets** in plaats van in de `description` van een keuzemenu dat één keer voorbijkomt — en de
regel die de keuze mogelijk maakt is "wat het kost", dus die hoort naast het beeld te blijven
staan. **Drie concepten met verschillende canvasmaten passen naast elkaar op ware verhouding**;
op een contactblad moet alles even breed zijn, en dan verliest een naaf van een band op een
eigenschap die na de keuze verdwijnt. En **de gebruiker kan rondkijken en aanwijzen** in plaats
van een van drie opties aan te vinken.

Stuur de vormtoetstabel mee in hetzelfde bericht: die laat zien wat er is afgevallen en waarom,
en dat is minstens zo nuttig als wat er overbleef. Twee concepten combineren is een goed
antwoord en vaak het beste — zeg erbij dat dat kan.

**Terugval, en die is echt.** Geen `node`, geen design-skill gevonden, of de publicatie wordt
niet goedgekeurd: dan lever je het contactblad en leg je de keuze voor met `AskUserQuestion`,
met de drie schetsen als opties en de vier regels in de `description`. Dat werkt onverkort en
kost minder; wat je opgeeft is dat de prijs van elk concept weer in een menu staat. Meld welke
route je liep. De canvasroute leunt op een preview-onderdeel dat per sessie wordt uitgepakt, dus
reken erop dat de terugval regelmatig aan de beurt is.

Wint het rooster, dan is dat een prima uitkomst — mits het gekozen is tegen twee figuren die
er echt naast lagen. Noteer dan in één regel waarom, want dat is een ontwerpbesluit en de
oplevering hoort het te noemen.

Bouw niet vóór er een keuze is. Koos de gebruiker in widget 1 voor doorbouwen, dan stuur je de
toetstabel en de schetsen mee in het bericht waarin je zegt dat je begint — dan kan iemand
ingrijpen zonder dat je wacht. Het denkwerk sla je nooit over.

Gaat de tekst op de infographic naar een klant, laat `sfnl-humanizer` er dan over vóór je bouwt.
Tekst die ná het bouwen verandert, betekent opnieuw bouwen.

## Stap 3 — De vijf besluiten

Het gekozen concept omzetten in getallen. Schrijf ze op vóór de eerste vorm; neem je ze niet
vooraf, dan neem je ze per element opnieuw en dan verspringt de infographic zonder dat iemand
kan zien waarom.

1. **De maten.** Kop 18 Montserrat SemiBold, body 16 Lato Light, voetnoot 11, en drager 28–40
   Montserrat Light als besluit 2 er een oplevert. Eén maat per rol. Op een smal canvas mag body
   14 en kop 17, maar dan voor alles. Koos de gebruiker "volledige toelichting", dan is body de
   maat die het meest telt en ga je niet onder 14. Geen drager betekent `Maten(drager=None)`, en
   dat is de stand van het veld.

   **Gaat het beeld in een document of een rapport, dan neem je dit besluit niet zelf.** Dan
   geldt de maatladder van de container en zet je hem in één regel: `Maten.voor("document")` of
   `Maten.voor("rapport")`. Dat is brood 13,33, kop 16 en noot 10,67 of 9,33 — **in px**, want
   dat is de eenheid van die route (stap 4D). In punten is het 10, 12 en 8 of 7.

   **En de default is dan géén drager.** Het window van de drager is 28 tot 40 pt en dat is niet
   verlaagd, want een getal daaronder leest niet als drager maar als een groot label. Op een
   documentpagina is 28 pt luider dan de titelmaat van die pagina zelf (20 pt), dus een drager
   in een exhibit is daar het luidste element na de dektitel. Dat kan een goede keuze zijn —
   maar dan is het er één, en niet iets wat je meeneemt omdat het in een losse infographic ook
   zo staat. De gewone uitkomst in deze route is dat de figuur zelf de bewering draagt en de
   pagina de woorden. Zie `reference/samenstellen.md`.
2. **Wat de bewering draagt.** Niet "welke drager", maar wélk element de zin uit de intake op
   het beeld zet. Schrijf het op in één regel, want dit besluit bepaalt of er een drager en een
   sluitregel bij komen — en niet andersom.

   Vier antwoorden, in volgorde van voorkeur (vormentaal §1):

   | het draagt | dan | en dan geen |
   |---|---|---|
   | de figuur zelf | direct labelen en verder niets | drager, sluitregel |
   | een getal of verhouding dat nergens anders staat | drager op 28–40pt | sluitregel, meestal |
   | de figuur zegt het half | sluitregel onderaan | drager |
   | alleen als de gebruiker erom vroeg | kopregel bovenaan | — |

   **De toets voor het eerste antwoord doe je hardop, want het is het antwoord waar je jezelf
   het makkelijkst mee voor de gek houdt.** Wijs de plek aan waar het oog het eerst komt en zeg
   in één zin wat de lezer daar afleest. Is dat de zin uit de intake, dan draagt de figuur hem.
   Is het "dat je het moet vergelijken", dan niet, en ga je naar rij twee of drie.

   **En de dubbeltoets.** Kies je een drager, kijk dan of zijn getal ergens anders op het vlak
   ook staat. Zo ja, dan herhaalt hij en gaat er één van de twee uit.

   **Zijn er geen cijfers, of is het beeld monochroom?** Dan valt "een getal" weg, en dan is de
   drager **één woord of begrip op displaymaat**, met de vorm eromheen als tweede laag: de enige
   gesloten vorm op het vlak, de dikste lijn, of het enige element in het midden.

   **Geen cijfers betekent ook dat de sluitregel verplicht is.** Een schema zonder getallen kan
   de bewering niet in een lengte of een dikte leggen, dus de zin onderaan is dan de infographic.
   Zeg bij de oplevering dat het beeld zonder die regel een schema is en geen uitspraak.
3. **De kaarttaal.** Volgt uit widget 2 vraag 3. Rechte hoeken of één hoekradius in punten, en
   welke vullingssoort de default is.
4. **Het accent, en of er meer dan één is.** Volgt uit widget 2 vraag 2. Koos de gebruiker
   "kleur codeert categorieën", schrijf dan hier per hue in één woord op wat hij betekent, en
   beslis er daarna niet meer over.
5. **Wat de compositie afsluit.** Een volle band tegen de onderrand, een haarlijn boven een
   sluitregel, of niets omdat de laatste rij zelf de conclusie is. Een kader is het niet.

Dit is geen tweede poort. De poort was de conceptkeuze in stap 2; deze vijf regels schrijf je op
en dan bouw je.


## Stap 4A — Bouwen als SVG

Zet de bouw meteen in één herbouwbaar script, niet in losse aanroepen. De renderloop is per
definitie meerdere ronden, dus je hebt een script nodig dat je onbeperkt kunt herhalen.

```python
import sys; sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/scripts/infographic")
from svg import (CANVAS, Canvas, Maten, blok, bron, cirkel, cols, container, drager,
                 hoogte_van, kop, label, lijn, op_schaal, pad, regels, schrijf, tekst,
                 tekst_op, vlak, vulgraad)

c = CANVAS["breed"]                       # of Canvas("eigen", 700, 420)
m = Maten(body=14, kop=18, drager=36, voetnoot=11)   # de vier maten, één keer

X, W, RIJ = 300, 480, 34                  # nullijn, volle lengte, staafhoogte
POSTEN = [("Begeleiding", 0.52), ("Taal", 0.26), ("Meting", 0.14), ("Rente", 0.08)]

vormen = [blok("Drager", 30, 60, 240, [drager("€ 1,2 mln", m.drager, "oranje")])]
for i, (naam, aandeel) in enumerate(POSTEN):
    y = 60 + i * (RIJ + 10)
    vormen += [
        vlak(f"Staaf {i}", X, y, aandeel * W, RIJ,        # lengte = de informatie
             vulling="oranje" if i == 0 else ("navy", 0.16), lijn_=None),
        blok(f"Label {i}", X + aandeel * W + 12, y + RIJ / 2, 220,
             [kop(f"{naam}  {aandeel:.0%}", m.body)], anchor="c"),   # direct gelabeld
    ]
schrijf("uitvoer/naam.svg", c, vormen, beschrijving="wat er te zien is")
```

Een rooster bouw je met `cols()`, `vlak(vulling=container(...))` en `blok()`. Dat is een
kaartenrij en die kun je in vier regels neerzetten, wat precies het probleem is: hij is
goedkoper te tekenen dan elke figuur en daarom komt hij eruit rollen als je niet oplet. Hij
hoort er alleen te staan als hij de conceptkeuze in stap 2 heeft gewonnen.

Wat de laag voor je regelt: de containerdekking per hue, de haarlijn in dezelfde hue als de
vulling, de tekstkleur die bij een vulling en een puntgrootte hoort, echte regelafbreking op de
fontmetriek van Montserrat en Lato, de baseline op de juiste plek, escaping, en de weigering van
Gotham Bold en van een drager buiten 28–40pt. `hoogte_van` en `vulgraad` zijn er om de val uit
vormentaal §5 te vermijden: eerst meten hoe hoog de inhoud is, dan pas beslissen hoe je de
restruimte verdeelt.

**Draagt afstand informatie, gebruik dan `op_schaal()`.** Op een tijdlijn is de x-positie van
een moment `breedte × (t − t0) / (t1 − t0)`, en die reken je niet met de hand:

```python
maand = lambda j, m: (j - 2024) * 12 + (m - 1)
x = op_schaal(maand(2025, 9), 0, maand(2027, 12), c=c)      # 408.51
```

`cols()` staat er voor gelijke kolommen en maakt daarmee het fóute antwoord het makkelijkst:
vier gelijke banden zijn geen tijdlijn. Op een tijdlijn is de x het gerekende getal en zijn de
y's juist vaste ankers — dan geldt de volgende regel dus omgekeerd.

**Houd een optische marge van ongeveer 30pt aan**, en laat alleen volvlakken afbloeden. Los
tekstwerk tegen de canvasrand leest als een schermafbeelding die er niet helemaal op past. Dit
staat als regel in vormentaal §2 en alle vijf de maatstaven doen het.

Drie dingen die je zelf doet, en die geen functie voor je oplost:

- **Reken de y-posities door in plaats van ze te typen** — in een compositie die van boven naar
  beneden loopt. `m1` doet dat met één lopende `y`, en daardoor kan een langere regel
  nooit over het blok eronder vallen. Uitzondering: composities met een vaste as of een raster
  (tijdlijn, naaf, matrix) hebben juist vaste y-ankers, en daar is de x of de hoek het
  gerekende. De regel gaat over welke as de informatie draagt, niet over de letter y.
- **Zet wat op één baseline moet in een eigen blok op een vaste y.** Een getal dat als derde
  alinea in hetzelfde blok als de toelichting staat, zakt mee met de regelval van die
  toelichting. Nagemeten: 15,7pt verschil tussen twee kolommen die naast elkaar staan.
- **Benoem in delen wat los moet kunnen bewegen.** `Kaart 1 label`, `Kaart 1 getal`,
  `Kaart 1 toelichting` in plaats van één vorm met drie alinea's. Dan is een latere wijziging
  chirurgisch.

Renderen:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/infographic/render_svg.py uitvoer/naam.svg --wit --schaal 2
```

## Stap 4B — Bouwen als PowerPoint-slide

Drie layouts, en welke het wordt kwam uit widget 1 vraag 2. Ze verschillen in meer dan hun maat:
in wie de titel draagt, in of `blanco.py` eraan te pas komt, en in welke placeholders je vult.

| gekozen vlak | layout | vak in inches | titel | `blanco.py` |
|---|---|---|---|---|
| contentzone van een getitelde slide | 19 | `0,48 / 1,93 · 12,52 × 5,00` | de slide draagt hem | nee |
| blanco slide | 17 | `0 / 0 · 13,33 × 7,50` | geen | ja |
| kolom van een tweeluik | 21 of 22 | `0,48 of 6,82 / 1,96 · 5,91 × 5,00` | de slide draagt hem | nee |

**Layout 19 is de gewone en layout 17 de bijzondere**, en dat is precies andersom dan deze skill
het eerder had staan. Op layout 19 erft de slide titel, subregel, oranje dash, logo en
paginanummer, staat de infographic in de contentzone eronder, en is vormentaal §1 opgelost door
de container zelf — geen sluitregel nodig, geen kopregel die als titel gaat lezen, en meestal
ook geen drager (vormentaal §1 en §4). Je vult dan placeholder 0 met de titel en 1 met de
subregel; placeholders die je niet vult, verwijder je van de slide. Vullen gaat met
`set_text.py --json '{"title": "...", "subtitle": "..."}'`.

**En let op wie op deze layouts de bewering draagt: de titel.** `add_slide.py` noemt idx 0
letterlijk "titel — de bewering van de slide, ALL CAPS". Dat is de rolverdeling van het
sjabloon en die overrule je niet. Vraag dus in de intake niet alleen óf de plek een titel
draagt maar ook wélke, en leg de bewering daar neer in plaats van eronder. Past hij niet in
caps op één regel, dan gaat hij naar de subregel en houdt de titel het onderwerp.

**Nagemeten: deze keten draait.** Layout 19 is end-to-end gebouwd met een waterval in de
contentzone — `pack.py` valideerde schoon, `render.py` gaf geen fontsubstitutie, en titel,
subregel, dash, logo en paginanummer kwamen alle vijf uit de layout.

Layout 17 is het blanco canvas: geen placeholders, geen titel, geen oranje dash. Kies hem alleen
als het beeld de hele slide ís en de bewering zelf draagt.

**Maar leeg is hij niet vanzelf.** Layout 17 is zelf leeg — 969
bytes, nul vormen — maar `slideMaster2.xml` tekent er het SFNL-logo linksonder en een
paginanummer rechtsonder bij. Dat zie je alleen op de render en niet in de XML van de slide. In
een eerdere versie van `m5` liep de sluitregel dwars door het logo.

**`scripts/infographic/blanco.py` haalt ze allebei weg** door `showMasterSp="0"` op de layout te zetten, en
die stap staat hieronder in de keten. `add_slide.py --no-page-number` uit de plugin weigert dat
op deze layout, omdat de vlag ook het logo meeneemt en dat voor een deck vrijwel nooit de
bedoeling is; voor een losse infographic is het dat wél. Draai `blanco.py` daarom nooit op een
bestand met meer dan één slide op die layout — het script waarschuwt als het er meer ziet.

Wil de gebruiker het logo juist wél op de slide, sla die stap dan over. Zeg er dan bij dat de
onderste 0,6 in gereserveerd is: links ongeveer 1,7 in voor het logo, rechts ongeveer 0,7 in
voor het nummer. Het canvas is 13,33 × 7,50 in en de infographic mag afbloeden tot de
rand.

**Op layout 19, 21 en 22 draai je `blanco.py` niet.** Dat zijn gewone deckslides en die horen
hun logo en paginanummer te houden; een infographic die tussen andere slides komt te staan en
als enige geen nummer draagt, valt op om de verkeerde reden. Daar geldt de contentzone als
werkvlak, en boven `y = 1,93` blijf je weg — daar staat de geërfde header.

Deze route gebruikt de scripts van de **sfnl-slides** plugin; `preflight.py` zegt waar die
staan. Ontbreekt de plugin, meld dat en bied de SVG-route aan.

```bash
P=${CLAUDE_PLUGIN_ROOT}          # uit preflight.py, sleutel sfnl_slides_scripts
cd <builddir>                   # werk in een lege map; prepare_template.py pakt hier uit
python $P/scripts/prepare_template.py . --template $P/assets/sfnl-sjabloon.potx

# -- variant A: contentzone van een getitelde slide (layout 19). De gewone.
python $P/scripts/add_slide.py unpacked slideLayout19.xml --only 0,1
#   ... titel in placeholder 0, subregel in 1; laat je 1 leeg, verwijder hem dan ...
#   ... componeren binnen 0,48 / 1,93 · 12,52 x 5,00 ...

# -- variant B: blanco slide (layout 17)
python $P/scripts/add_slide.py unpacked slideLayout17.xml --bare
python ${CLAUDE_PLUGIN_ROOT}/scripts/infographic/blanco.py unpacked slideLayout17.xml
#   ... componeren over de volle 13,33 x 7,50 ...

# -- variant C: kolom van een tweeluik (layout 21 of 22)
python $P/scripts/add_slide.py unpacked slideLayout21.xml --only 0,1,12
#   ... idx 12 is de LINKER kolom en 13 de rechter. Houd de kolom die tekst wordt en laat
#   ... de andere weg -- daar teken je zelf overheen. Dus: figuur rechts -> --only 0,1,12.

python $P/scripts/clean.py unpacked
python $P/scripts/office/pack.py unpacked infographic.pptx --original $P/assets/sfnl-sjabloon.potx
#   ... alleen als er een native grafiek of tabel op moet: stap 4C, ná het inpakken ...
python $P/scripts/render.py infographic.pptx png
```

`--bare` hoort bij layout 17 en alleen daarbij: zonder die vlag krijg je placeholders op een
layout die er geen hoort te hebben, en die moet `clean.py` daarna weer opruimen. Op 19, 21 en 22
wil je die placeholders juist wél, want daar staat de titel in — dus daar geen `--bare`, maar
`--only` met precies de idx'en die je vult. De rolnamen per idx staan in de JSON die
`add_slide.py` teruggeeft.

Componeren doe je met `shapes.py` van de deckroute, niet met `svg.py`: dat is de primitievenlaag
die de OOXML-valkuilen afhandelt. De maten zijn daar inches in plaats van punten; de vier maten
uit besluit 1 blijven punten.

```python
import sys; sys.path.insert(0, f"{P}/scripts")
from shapes import Deck, drager, hoogte_van, label, para, run, vlak, write
D = Deck(body=16, kop=18, label=14, display=36)
vormen = [vlak("Rij 1", 0.55, 0.80, 12.23, 1.45, vulling="container:emerald",
               lijn=("emerald", 1))]
write("unpacked/ppt/slides/slide1.xml", vormen)
```

**`Deck` heeft geen `sluit`, en wél een `kop`.** De velden zijn `body, kop, label, display,
voetnoot`, plus `hoek` en `rol_kleur`. Hier stond eerder het omgekeerde — "geen `kop`, wel
`sluit`" — en dat is een `TypeError` op de eerste regel van het bouwscript, dus nagemeten op de
keten van layout 19. De sluitregel heeft geen eigen veld en dat is opzet: die staat op bodymaat,
want een eigen maat voor de laatste regel is precies het defect waar `Deck` tegen bestaat. Let
ook op de andere naam: de drager heet hier `display` en niet `drager`, met dezelfde grenzen van
28 tot 40pt. `label` is de kapitaalregel van 14.

**De schrijfwijze verschilt van route 4A.** Hier `vulling="container:emerald"` als string en
`lijn=`; in `svg.py` `vulling=container("emerald")` en `lijn_=`. Twee lagen, twee conventies —
wissel je van route, wissel dan ook van schrijfwijze.

**En de dekking rekent hier in honderdduizendsten.** `("navy", 7000)` is 7 procent; in `svg.py`
is dezelfde dekking `("navy", 0.07)`. Dit is de gevaarlijkste van de twee verschillen, want de
verkeerde eenheid gaf hier geen fout: `int(0.16)` is 0, dus alpha nul, dus een vorm die er
volledig doorzichtig op staat. Nagemeten op deze keten — drie van de vier staven waren er niet
en `pack.py` valideerde schoon. `shapes.py` weigert nu een waarde tussen 0 en 1000 met die
uitleg erbij, dus je krijgt hem tegenwoordig te horen. Wil je de gekalibreerde
containerdekking, gebruik dan `"container:navy"` en reken niets uit.

**`spc_voor` is in honderdsten van een punt.** `spc_voor=600` is 6pt; `spc_voor=14000` is
140pt en zet je alinea anderhalve inch lager, dwars door de vorm eronder. Dat kostte een
renderronde. `regelafstand=112000` is wél een promillage, en die twee lijken op elkaar.

Wat alleen in deze route geldt:

- **Het canvas staat vast, dus of de inhoud groeit of het vlak wordt kleiner.** Een hele slide op
  layout 17 vraagt ongeveer twee keer de inhoud van een band van 960 × 320pt. Dezelfde drie
  kaarten die een band vullen, laten op zo'n slide de onderste 2,9 in leeg. In `m5` is dat
  gerepareerd met een andere plattegrond — drie rijen over de volle breedte in plaats van drie
  kolommen — en dat blijft een goed antwoord. Het goedkópere antwoord staat er sinds kort naast:
  ga naar layout 19, waar de contentzone 12,52 × 5,00 in is en een band er precies in past. Kies
  de plattegrond dus pas nadat je het vlak hebt gekozen, en niet andersom.
- **`streep()` kent geen dekking.** Wil je een haarlijn op 20 of 30 procent — een
  verbindingslijn in een waterval, een spoor onder een staaf — teken die dan als een
  `vlak()` van 0,01 in hoog met een alpha-vulling. In `svg.py` gaat dat met `dekking=`,
  hier niet, en dat is het soort verschil dat je pas op de render ziet.
- **Een vak zonder vulling heeft insets 0**, dus tekst begint exact op de vormrand. Zet zo'n vak
  op `x + 0,2`, anders hangt de eerste letter over de rand van de kaart waar hij in staat.
- **Eén script dat de builddir weggooit en opnieuw begint.** `write()` voegt vormen toe vóór
  `</p:spTree>` en `add_slide.py` hangt een slide achteraan, dus een tweede run op een bestaande
  map verdubbelt alles.
- **Grafieken en tabellen ná het inpakken** — dat is stap 4C hieronder, en die staat ná
  `pack.py` en vóór `render.py`. Een `pack` daarna sloopt ze.
- **Het bestand weegt ruwweg 5,5 MB**, ook voor één slide, want het sjabloon draagt de foto's
  van alle 27 layouts mee. Gaat de slide de mail in, lever dan ook een lichte kopie:
  `unpack.py` → `clean.py slim --drop-unused-layouts` → `pack.py`. Zeg erbij wat de gebruiker
  opgeeft: in de lichte versie kan een collega alleen nog de layouts kiezen die erin zitten.

Er is geen `fit_title.py` en geen `qa_text.py`-poort nodig, want er is geen titel en geen
placeholder. Wat wél blijft: `pack.py` moet schoon valideren.

## Stap 4C — Een native grafiek of tabel

Kwam de telling in stap 1 hierop uit, dan is dit de route. Een native grafiek is een echt
PowerPoint-object: de cijfers zitten erin, een collega werkt ze bij zonder jou, en de kleuren
komen uit het SFNL-thema. Een getekend staafje kan dat allemaal niet.

Dit kan alleen in de PowerPoint-route. Vroeg de gebruiker om SVG, zeg dat dan: `svg.py` kan
geen native grafiek, en de eerlijke keuzes zijn een PowerPoint-slide, of **sfnl-excel** als het
model erachter belangrijker is dan het beeld. Een SVG met handgetekende staafjes is de
uitkomst die je niet levert.

```bash
python $P/scripts/add_chart.py infographic.pptx --slide 1 --data chart.json \
    --box 5.4,1.0,7.4,4.6 --series-colors navy,sky,oranje
python $P/scripts/add_table.py infographic.pptx --slide 1 --box 0.55,1.0,12.2,3.2 \
    --data tabel.json
```

`chart.json` is `{"categories": [...], "series": {"Naam": [...]}}`, `tabel.json` is
`{"columns": [...], "rows": [...]}`. Lees de docstring van `add_chart.py` vóór gebruik; hij
heeft meer vlaggen dan hier passen.

Vier dingen die hier misgaan:

- **Geef altijd `--box`.** Zonder `--box` valt de grafiek in de contentzone van een getitelde
  slide (0,48 / 1,93 / 12,52 / 5,00). Op layout 19 is dat toevallig precies goed; op layout 17
  is het de zone die er niet is, en dan krijg je 1,9 in dood wit erboven en wordt een grafiek die
  tot de onderrand loopt stilzwijgend ingekort. Typ hem dus uit in plaats van erop te gokken.
- **Zet er geen kaart omheen.** Een containervlak met een haarlijn om een grafiek leest als een
  schermafbeelding die erin geplakt is — precies wat vormentaal §2 wil vermijden. De grafiek
  staat op wit.
- **De legenda wint hier van vormentaal §9.** Direct labelen kan niet bij drie reeksen, dus er
  komt een legenda. Dat is de prijs van een native grafiek en je noemt hem bij de oplevering.
- **`--highlight` werkt op één reeks.** "Deze ene gemeente oranje, de rest navy" kan dus alleen
  als je één reeks tekent — bijvoorbeeld het verschil tussen begin en eind in plaats van alle
  jaren. Dat is een inhoudelijke keuze en hij hoort in de brainstorm, niet in de bouw.

De rest van de keten is die van 4B, en de renderloop van stap 5 geldt onverkort.

## Stap 4D — Bouwen als exhibit in een document of rapport

Dit is route 4A met drie dingen vastgezet: het canvas, de maatladder en **de eenheid**. De rest
— de vormkeuze, de vijf besluiten, de primitieven, de renderloop — is onverkort dezelfde, en dat
is het punt van deze route: een exhibit is geen ander soort beeld, het is hetzelfde beeld op het
vlak van zijn container.

```python
import sys; sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/scripts/infographic")
from svg import CANVAS, Maten, blok, bron, kop, label, lijn, schrijf, tekst, vlak

c = CANVAS["doc-breed"]              # of doc-kolom2, rap-breed, rap-kolom, rap-dubbel
m = Maten.voor("document")           # zet de ladder én de eenheid: brood 13,33 px = 10 pt
# ... componeren als in 4A, maar in px en met een kleine binnenmarge ...
schrijf("uitvoer/exhibit.svg", c, vormen, beschrijving="wat er te zien is")
```

**Hier wordt in px gerekend en niet in punten, en dat is geen conventiekwestie.** Het
meetapparaat van de containers leest de **opgegeven** maat uit de SVG en niet de gerenderde:
de `te-klein`-regel van `qa_document.py` neemt `getComputedStyle(el).fontSize`, en dat getal
staat in het lokale coördinatenstelsel. Een `viewBox` die de inhoud opschaalt, ziet die regel
dus niet. Nagemeten: een beeld van 510 pt breed in een kader van 680 px rendert zijn 10-punts
brood keurig op 13,33 px, en `qa_document.py` meldde er elf `critical` over — acht keer
`te-klein`, en geen ervan was een echt defect. Op `doc-breed` gebouwd komt hetzelfde beeld
schoon door: **geen bevindingen.**

`Maten.voor("document")` en `Maten.voor("rapport")` zetten de eenheid mee, dus in de praktijk
merk je er alleen dit van: de getallen in je bouwscript zijn een derde groter dan je van route
4A gewend bent. Vergeet je de maten en zet je zelf `Maten(...)` neer, dan weigert `schrijf()`
en zegt hij welke eenheid het canvas wil. En `bron()` vraagt hier om een maat in plaats van er
een te verzinnen: geef `m.voetnoot`, dat is de noot van de container.

**De binnenmarge is klein, en dat is de tweede correctie op je reflex.** De 30pt uit vormentaal
§2 is er om los tekstwerk van de canvasrand te houden op een beeld dat zelf de hele slide vult.
Een exhibit staat al binnen de zetspiegel van zijn pagina, dus die witruimte is er al: 30 px
binnenmarge telt er bovenop en duwt de figuur zichtbaar naar binnen. Houd het op ongeveer 10 px,
of nul waar de figuur zijn eigen lucht heeft. Volvlakken mogen nog steeds afbloeden.

Renderen doe je zoals in 4A. En dan de stap die deze route eigen is:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/infographic/insluiten.py uitvoer/exhibit.svg \
    --doel document --kader breed --uit uitvoer/fragment.html
```

`insluiten.py` leest de `viewBox` en alle `font-size`-waarden uit de SVG, rekent uit wat er met
die maten gebeurt in het kader van de bestemming, en **weigert** als de kleinste tekst door de
leesvloer zakt — 7,8pt in een document, 6pt in een rapport, 12pt op een slide. Die eerste is
niet afgerond: het is exact de vloer van 10,4 px die `qa_document.py` zelf handhaaft, want twee
bijna-gelijke vloeren zijn erger dan één. Zegt hij nee, dan is het antwoord niet `--toch` maar
opnieuw tekenen op het juiste canvas. Nagemeten: `m1` uit de maatstaf is een band van
960 × 320pt, en in het documentkader van 680 px krimpt hij met factor 0,53 — zijn voetnoot van
10pt komt op 5,31pt uit. Dezelfde compositie op `doc-breed` gebouwd haalt factor 1,0.

Hij doet nog één ding, en dat is de tweede meting van deze route. `svg.py` schrijft
`font-family="Lato Light, Lato, sans-serif"`: de snede vooraan, de familie als terugval. In een
document telt `qa_document.py` de **eerste** naam als de letterfamilie, dus zo staan er drie
families op de pagina — Lato, Lato Light en Montserrat — waar de regel er twee toestaat, en dat
is één `critical`. `insluiten.py` haalt de snede daarom uit de naam: het gewicht draagt hem al,
en `fonts.css` declareert `'Lato'` op 300, dus de letter blijft exact dezelfde. Hij meldt hoeveel
waarden hij aanpaste.

Wat er uit komt, verschilt per bestemming, en dat komt doordat de containers het beeld anders
plaatsen:

| doel | oplevering | waarom |
|---|---|---|
| `document` | een `.beeldkader` met de SVG **inline** | de artboards van `sfnl-design-documents` zijn met de hand gecomponeerde HTML; tekst blijft tekst en de PDF houdt hem selecteerbaar |
| `rapport` | een **PNG op 2×** plus de regel voor de `figuren`-JSON | `bouw.py` plaatst beeld als `<img src>` uit die JSON; factor 2 is bedoeld voor 192 dpi en blijft onder de krimpgrens van 2,5 |
| `slide` | een **PNG op 2×** met de breedte in inches erbij | om te plakken. Wil je een slide die in PowerPoint bewerkbaar blijft, dan is dat route 4B en niet dit |

Bij `--doel rapport` geef je `--na <blok-id>` mee: dat is het blok waar het beeld achter komt,
en `lees_docx.py` van de rapportskill geeft die id's. Zonder id weet de zetmotor niet waar het
beeld hoort en moet iemand het achteraf verzinnen.

**Het bijschrift is van de container en niet van het beeld.** In een document staat de herkomst
in de `figcaption` onder het kader, in een rapport in `exhibit__titel` en `exhibit__bron`. Zet
er dus geen tweede bronregel in de SVG bij als de container hem al draagt — dat is dezelfde
keuze als "de container draagt de bron" uit widget 2 vraag 4, en hier is het bijna altijd het
goede antwoord.

## Stap 5 — De renderloop, ten hoogste drie ronden

Dit is niet overslaanbaar. Het is de enige plek waar de vorm beoordeeld wordt.

**Render naar een pad waar je er zelf bij kunt, en kijk er echt naar.**

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/infographic/render_svg.py uitvoer/naam.svg --wit --schaal 1 --knijp
```

`--schaal 1` in de loop en `--schaal 2` pas bij de oplevering: op ware grootte zie je elke fout
die er te zien is, en het kost een kwart. `--knijp` schrijft er `naam-knijp.png` naast op een
kwart — dat is de kneepoefening uit vormentaal §4, en die overschrijft je oplever-PNG niet.

In de PowerPoint-route schrijft `render.py` altijd `slide_01.png` in de opgegeven map, dus geef
per ronde een eigen map mee (`png1`, `png2`).

Ronde 1 rendert, en je repareert **alles** wat je ziet in één keer — niet de helft. Ronde 2
rendert opnieuw en beoordeelt opnieuw. Komt die schoon terug, dan ga je
door. Zo niet, dan is er nog één ronde 3, en daarna houdt het op: je meldt wat er nog staat en
vraagt of er nog een ronde moet komen.

Staat er ná ronde 2 nog overloop, overlap of tekst buiten zijn vak, dan is dat geen restpost die
je afmeldt: twee ronden zijn genoeg om dat weg te krijgen, dus de compositie is te vol. Zeg dat
zo, en stel voor de infographic te splitsen of de tekst in te korten in plaats van hem nog een
ronde bij te schaven.

Wat je in de eerste ronde zelf al gaat zien, en wat geen regel voor je oplost:

- **Dood wit onder de compositie.** Het canvas is een keuze: maak hem korter, of zet er meer
  inhoud in. Nooit de blokken hoger.
- **Een label dat over twee regels loopt terwijl de buurlabels dat niet doen.** Dan staan de
  getallen eronder niet meer op één lijn. Kort het label in of geef alle labels een vaste hoogte.
- **Een blok met lucht onderin**, ook als `vulgraad` een net getal gaf. De meting rekent
  strakker dan de renderer zet, dus onder 0,9 is het een bevinding en geen grensgeval.
- **Een lijn die niets codeert**, een pijl die in het wit staat, of een gekleurd vlak zonder
  inhoud. Die gaan eruit.
- **Tekst die links of rechts buiten het canvas valt.** `schrijf()` meldt dit nu zelf met
  `BUITEN HET CANVAS` en de kant erbij, dus lees die regel voordat je rendert. Wat hij niet
  ziet: `pad()` heeft geen doos, dus paden en pijlen controleer je met het oog.
- **Twee hues die hetzelfde zeggen.** Vraag per kleur wat hij codeert; kun je het niet in één
  woord zeggen, dan wordt het het accent.

- **Een figuur die onderweg een rooster is geworden.** Dit is de sluipende: je koos een sankey
  en op de render staan vier gelijke banden, of je koos een tijdlijn en de momenten staan op
  gelijke afstand omdat het zo netter uitkwam. De toets is één vraag aan het beeld: **welk
  getal zou deze tekening veranderen?** Kun je er geen noemen, dan tekent de compositie niets
  meer en is er een figuur naar een rooster gezakt. Dat is geen bijschaafwerk maar terug naar
  het bouwscript.

Is de loop schoon, doe dan één keer de laatste toets: **dek de omgeving af.** Zegt de infographic
zonder titel eromheen nog wat de lezer moet overhouden? Zo niet, dan is dat geen opmaakfout en
gaat het terug naar besluit 2, niet naar de render.

## Stap 6 — Opleveren

Bij de SVG-route lever je twee bestanden, en een derde alleen voor drukwerk:

| bestand | waarvoor |
|---|---|
| `naam.svg` | het origineel. Schaalt oneindig, te openen in Affinity, Illustrator en de browser, tekst blijft tekst. Doorzichtige achtergrond. |
| `naam.png` op 2× | om in PowerPoint, Word of een mail te plakken. Dit is wat in de praktijk het meest gebruikt wordt. Render hem één keer op `--schaal 2`, ná de loop. |
| `naam.pdf` | alleen als het naar drukwerk gaat (`--pdf`). |

Bij de PowerPoint-route lever je de `.pptx` met de ene slide erin. Koos de gebruiker layout 17,
zeg er dan bij dat hij die slide kopieert naar het deck waar hij hoort en de titel daar van de
omliggende slide krijgt; koos hij 19, 21 of 22, dan draagt de slide zijn eigen titel al en is
dat niet nodig.

Bij de exhibitroute lever je de SVG, het fragment of de `figuren`-regel uit `insluiten.py`, en
de meting die eronder stond: op welk kader hij past, met welke factor, en welke maten er na het
plaatsen op staan. Die drie regels zijn de oplevering, want ze zijn wat iemand nodig heeft om
het beeld ergens ánders neer te zetten zonder de fout uit §11 te maken. Gaat het beeld in een
rapport, noem dan ook dat de PNG op 2× staat en waarom: dat is factor 2 op 192 dpi, ruim onder
de krimpgrens van 2,5 waar de zetmotor een beeld naar de volle zetspiegel promoveert.

### En bij de SVG-route: leg hem op een canvas

Draai je in Claude Code en vond `preflight.py` node plus de canvashelper, publiceer de afgemaakte
SVG dan als één artboard met de vormtoetstabel als notitie ernaast. Dat is dezelfde beweging als
bij de schetsen in stap 2D en om dezelfde reden: de redenering staat naast het beeld in plaats
van in een bericht dat wegscrollt. De ontvanger ziet niet alleen wat het geworden is, maar ook
wat er is afgevallen en waarop.

```python
import sys; sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/scripts/infographic")
from schets import artboard, canvas_manifest, seed_helper

artboard("uitvoer/canvas/Main.dc.html", c, vormen)     # dezelfde vormen als schrijf()
canvas_manifest("uitvoer/canvas/canvas.json", [
    {"bestand": "uitvoer/canvas/Main.dc.html", "canvas": c, "titel": "<onderwerp>",
     "regels": ["Vraag: <de zin uit 2A>",
                "Vorm: <de winnaar> — <welke meting welke maat bepaalt>",
                "Afgevallen: <kandidaat> op <toets>, <kandidaat> op <toets>",
                "Drager: <wat de boodschap draagt>"]},
])
```

Seeden en publiceren gaat als in stap 2D, met `seed_helper()` voor het pad. Dit is een
**opleverblad en geen bewerkomgeving** — dat onderscheid is nagemeten en het is de reden dat deze
stap er zo kort uitziet. Dezelfde infographic is een keer naast elkaar gebouwd, als SVG en als
bewerkbaar `.dc.html`-artboard, en de twee renders waren niet van elkaar te onderscheiden. Wat de
canvasversie extra bood was met de muis kunnen schuiven; wat ze inleverde was de contrasttoets
van `svg.py`, de echte fontmetriek, en een SVG die in Affinity opengaat. De SVG is zelf al
bewerkbaar — tekst blijft tekst, elke vorm is een los object — dus die ruil is niet de moeite.
**Bouw het eindbeeld dus nooit als `.dc.html`.** Het canvas draagt hier alleen de SVG en de
redenering.

Ontbreekt node of de helper, of wordt de publicatie niet goedgekeurd, dan sla je dit over en
lever je de bestanden uit de tabel hierboven. Meld welke route je liep. Bij de PowerPoint-route
doe je dit niet: daar is de `.pptx` de oplevering en voegt een canvas er niets aan toe.

De fonts zitten **niet** in de SVG. Montserrat en Lato staan op SFNL-computers en in elke
browser via Google Fonts, maar op een machine zonder die fonts substitueert de weergave. Gaat de
SVG naar buiten, lever dan de PNG mee — of zeg dat de PNG de veilige versie is.

Zeg er bij de oplevering bij dat het beeld geen titel en geen uitleggende tekst per element
heeft, en vraag of er een kopregel of een toelichtingsstand bij moet. Dan kiest de gebruiker die
erbij in plaats van dat je ze er ongevraagd op zet.

Draagt de figuur de bewering zelf en staat er dus geen drager en geen sluitregel op, noem dan
ook dát — in één regel, met wat je in de plek waar het oog het eerst komt hebt gelegd. Het is
een ontwerpbesluit en het hoort zichtbaar te zijn, want het is precies het besluit dat iemand
zou willen terugdraaien als het beeld ergens komt te staan waar niemand het toelicht.

Zeg bij oplevering wat er gecontroleerd is: hoeveel renderronden het waren en of de loop schoon
afsloot of op de grens stopte. Een cijfer dat je niet hebt kunnen verifiëren noem je expliciet.
Laat de aannames die je hebt gedaan in één regel staan, zodat de gebruiker ze kan bijsturen.

Geef bestanden een naam zonder apostrofs of andere tekens die een browser bij downloaden
verhaspelt.

## Wat het kost, en waar je op kunt sturen

Gemeten over drie testopdrachten (een tijdlijn in SVG, een monochrome naaf in SVG, en een
native grafiek op een PowerPoint-slide): **130.000 tot 170.000 tokens per infographic**, van
intake tot oplevering, met dertig tot vijfendertig toolaanroepen en drie renderronden.

Waar dat heen gaat, en wat je eraan doet:

| post | ruwe kosten | waar je op stuurt |
|---|---|---|
| SKILL.md plus de maatstaf lezen | ~15k | vast; dit is het minimum |
| `svg.py` volledig lezen | ~8k | lees de **docstring** en de signatures, niet het hele bestand: `python -c "import ast, inspect; ..."` of `sed -n '1,60p'` |
| de voorbeelden bekijken | 0,5k tot 6k | het vormenwoordenboek (2,2k) altijd, en **één** gebouwd voorbeeld — niet alle vier |
| drie schetsen renderen en bekijken | ~2k | `--schaal 1` op schetsen, en `contactblad()` op één kolom van 1100px. Een figuurschets kost hetzelfde als een roosterschets: de helpers in `schets.py` zijn één regel per stuk, dus daar valt niets te besparen door dozen te tekenen |
| de conceptkeuze als canvas voorleggen | ~0,5k | de artboards komen uit hetzelfde bouwscript (`artboard_=`), dus dit is alleen het seeden en publiceren. Ontbreekt node of de helper, dan is het contactblad de terugval en kost deze regel niets |
| het opleverblad als canvas (stap 6, SVG-route) | ~0,3k | één artboard uit dezelfde `vormen`, één manifest, één publicatie. Bouw het eindbeeld nooit als `.dc.html`: dat is een tweede bouwlaag van 15k tot 30k voor een render die niet van de SVG te onderscheiden is |
| elke renderronde | 0,7k tot 1,8k per beeld | `--schaal 1` in de loop, `--schaal 2` pas bij de oplevering; dat scheelt een factor vier |
| het bouwscript schrijven en herschrijven | 15k tot 30k | het grootste blok, en de reden dat stap 2 bestaat: een verkeerd concept kost dit blok twee keer |

**Beeld is duurder dan tekst.** Eén render van 2560 × 854 kost ongeveer evenveel als drie
pagina's tekst, en vier voorbeelden bekijken kost meer dan deze hele SKILL.md. Dat is ook de
reden dat de renderloop op drie ronden staat en niet op "tot het af is".

**De goedkoopste besparing is de brainstorm.** Drie schetsen kosten samen ongeveer 2k plus het
schrijven ervan; één infographic opnieuw bouwen omdat het concept niet klopte kost 20k tot 30k.
Sla stap 2 dus niet over om tijd te winnen.

## Wat blokkeert

1. **Geen bewering.** Dek de omgeving af: zegt het beeld nog wat de lezer moet overhouden? Zo
   niet, dan is het een verzameling vlakken. Terug naar besluit 2.

   Let op wat dit níet zegt. Het is niet "geen drager" — zo stond het hier eerst, en dat maakte
   van een element een eis. Een figuur die zijn eigen elementen labelt kan de bewering prima
   dragen zonder dat er een getal op displaymaat naast staat, en dan is de drager weglaten een
   ontwerpbesluit en geen gebrek. Wat blokkeert is een beeld waar je de bewering niet kunt
   aanwijzen, met of zonder drager.
2. **Gotham Bold in de infographic.** Dat is de titelletter en een infographic heeft geen titel.
   `svg.py` weigert hem.
3. **Een drager buiten 28 tot 40pt.** Groter leest niet luider. `svg.py` en `shapes.py`
   weigeren hem.
4. **Een lichte hue die tekst kleiner dan 18pt draagt.** 18pt zelf mag; 17,5 niet. Het contrast
   haalt het niet. `svg.py` weigert hem en zegt welke maat het wel mag.
5. **Een schemafout uit `pack.py`** in de PowerPoint-route.
6. **Een omlijning om het geheel, of een titelbalk.** Die twee zijn de reden dat deze skill
   bestaat.
7. **Een titel, een ondertitel of een inleidende alinea waar niemand om vroeg.** Een kopregel
   bovenaan bestaat alleen als de gebruiker erom vroeg (vormentaal §1 punt 3). Staat er een op
   de render zonder dat het gevraagd is, dan gaat hij eruit vóór de oplevering en niet in een
   volgende ronde.
8. **Gebouwd zonder ingevulde vormtoets.** Geen tabel met kandidaten, vier toetsen en een
   slotoordeel betekent niet bouwen. Een vorm die niet expliciet is afgevallen blijft
   rondzweven tot hij per ongeluk gebouwd wordt, en dat is de fout die deze stap moet vangen.
9. **Gebouwd zonder dat er een concept is voorgelegd.** Drie schetsen kosten een tiende van één
   gebouwde infographic; die stap overslaan levert de eerste inval op en kost daarna een
   herbouw. In doorbouwmodus stuur je ze mee in plaats van erop te wachten.
10. **Drie roosterschetsen voorgelegd terwijl er figuren de vormtoets haalden.** Dan is er geen
    keuze voorgelegd maar één concept in drie uitvoeringen. Ten hoogste één van de drie is een
    rooster (stap 2D).
11. **Een compositie waarin geen enkele meting iets bepaalt, zonder dat dat gekozen is.** Loop
    het beeld af en zoek de maat die uit een getal volgt: een lengte, een x, een dikte, een
    hoek, een aantal. Vind je er geen en heeft het rooster de conceptkeuze niet gewonnen, dan
    is de vorm onderweg weggezakt en bouw je hem terug. Bij een gekozen rooster is dit geen
    blokkade, maar noem je bij de oplevering wat het beeld daardoor niet zegt.
12. **Een exhibit geplaatst zonder de maten na te rekenen.** Gaat het beeld in een document of
    een rapport, dan is `insluiten.py` de poort en niet een controle achteraf. Weigert hij, dan
    bouw je opnieuw op het canvas van de bestemming; `--toch` bestaat om een grensgeval bewust
    door te laten en niet om een meting te overrulen. Dit is het defect dat pas op papier
    zichtbaar is, en dat is precies waarom het hier staat.
13. **Het eindbeeld gebouwd als `.dc.html` in plaats van als SVG.** Het canvas is een
    opleverblad en geen tekenprogramma. Bouw je erin, dan valt de contrasttoets weg, de echte
    fontmetriek, en de SVG die in Affinity opengaat — en je krijgt er een render voor terug die
    van de SVG niet te onderscheiden is. Dit is nagemeten (stap 6). Het canvas draagt de SVG en
    de redenering, meer niet.

## Als iets ontbreekt

**Geen echte fontmetriek.** Dan is de regelafbreking geschat en dus ruim. Compositie, kleur,
wit, overlap en uitlijning beoordeel je gewoon op de render; regelval en dus blokhoogte niet.
Bouw conservatiever: kort de tekst in tot ruim binnen zijn vak in plaats van precies, en rek
nooit een vak op om een afbreking te repareren.

**Maar dit hoort niet meer voor te komen**, en dat is het verschil met de losse skill. De
plugin draagt Montserrat en Lato zelf mee, in `assets/documenten/fonts/`, als woff2 voor de
drukroutes — en `svg.py` leest diezelfde bestanden. Meldt `preflight.py` tóch een schatting,
dan is er één waarschijnlijke oorzaak: **`brotli` ontbreekt.** Een woff2 is brotli-gecomprimeerd
en zonder die module krijgt fontTools hem niet open, dus dan staat er een pad in `fonts` en
`meting_echt: false` eronder. `python ${CLAUDE_PLUGIN_ROOT}/scripts/infographic/preflight.py
--herstel` zet hem erbij.

Twee dingen om te weten over die ingesloten letters. Het is de **latin-subset**, dus alles wat
een SFNL-infographic zet zit erin op één teken na: het promillageteken. Dat meet als een cijfer
— ruim genoeg om niet te laat af te breken, maar niet exact. En Montserrat komt als één
variabel bestand met standaardgewicht 100, dus `svg.py` instantieert het op 300 en 600; wie de
metriek rauw zou lezen, meet Thin, en dat is vier procent op de regel. Staat er een volledige
statische snede in `assets/fonts/`, dan gaat die vóór — meer tekens, en niets te instantiëren.

**Geen renderer.** Dan bouw je blind. Minder elementen, ruimere marges, ruimere vakken, en zeg
het bij de oplevering met zoveel woorden: deze infographic is niet visueel geverifieerd. Dat is
het verschil tussen iets dat gecontroleerd is en iets waarvan alleen de code klopt.

**Geen Pillow.** Dan werkt `contactblad()` niet en stuur je de schetsen als losse PNG's. Dat is
een slechtere brainstorm, want de keuze gaat over het verschil; `pip install pillow
--break-system-packages` lost het op.

**Geen deckscripts naast deze skill.** Dan werkt alleen de SVG-route. Binnen de plugin hoort
dat niet te kunnen — `${CLAUDE_PLUGIN_ROOT}/scripts/shapes.py` en
`${CLAUDE_PLUGIN_ROOT}/assets/sfnl-sjabloon.potx` staan er altijd — dus als `preflight.py` hier
`null` meldt, is de checkout niet compleet en zeg je dat, in plaats van het als een gewone
terugval te behandelen. Werk dan door in SVG en bied aan de PNG op 2× te leveren die de
gebruiker zelf in een slide plakt.

## Samenstellen met de andere drie skills

De vier skills in deze plugin zijn geen aparte gereedschappen die dezelfde kleuren gebruiken.
Ze delen hun assets, hun letters en hun canvasroute, en ze zijn bedoeld om aan elkaar geschakeld
te worden. `reference/samenstellen.md` beschrijft de vier ketens die er echt zijn; hier de twee
die bij déze skill beginnen.

**Een infographic in een document of rapport** is stap 4D hierboven. Wat je onthoudt: het canvas
en de maatladder komen van de container, niet van dit beeld, en `insluiten.py` rekent na of het
past. Bouw je op `CANVAS["breed"]` en plaats je het achteraf, dan gaat er een letter door de
vloer en ziet niemand het tot het gedrukt is.

**Een deck of document dat een figuur nodig heeft**, komt de andere kant op. `sfnl-slides`
escaleert naar deze skill boven twaalf onderdelen op een slide, `sfnl-design-documents` bij een
beeld dat rekent (§11 van zijn vormentaal), en `sfnl-rapport-opmaak` bij een figuur die
uitgerekend moet worden. In alle drie de gevallen begin je hier bij stap 1, met één verschil:
**de bewering ligt al vast.** Die staat in de titel van de slide of in de kop van de pagina, dus
de vraag uit de intake is al beantwoord en er komt geen tweede bewering op het beeld — geen
drager en geen sluitregel, tenzij de figuur zonder echt niets zegt.

## Wat deze skill niet is

Voor een hele presentatie gebruik je **sfnl-slides**: dat is de skill met het sjabloon, de
layouts, de titelmodus en de deck-brede besluiten. Voor kort drukwerk in HTML —
een uitnodiging, een executive summary, een spread — **sfnl-design-documents**, en voor een
afgerond Word-rapport dat drukklaar moet **sfnl-rapport-opmaak**; dat zijn de twee zusterskills
in deze plugin. Voor een rapportspread in Affinity gebruik je **sfnl-rapport**, en voor een
HTML-dashboard, een one-pager of een Word-document **sfnl-design**. Deze skill is voor het losse
beeld dat in een van die vijf komt te staan.

Gaat het om een echte reeks over tijd, een verdeling van meer dan zes categorieën of een
vergelijking die je zou willen kunnen bijwerken, overweeg dan een native grafiek in PowerPoint
(`add_chart.py`) of Excel (**sfnl-excel**) in plaats van een getekende infographic. Een getekend
staafje is geen grafiek en veroudert zonder dat iemand het merkt.
