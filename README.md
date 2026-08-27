# sfnl-design

Acht skills die dezelfde regel volgen: de vorm is een ontwerpbeslissing en geen invuloefening, en
de render is de enige vormbeoordeling.

| skill | wat je ermee maakt |
|---|---|
| **`slides`** | een SFNL-deck uit het officiële `.potx`-sjabloon |
| **`ontwerp-documenten`** | kort drukwerk in HTML: een uitnodiging, een executive summary, een proposal, een spread |
| **`rapport-deliverable`** | een afgerond Word-rapport van twintig tot honderdvijftig pagina's, opgemaakt zonder één woord aan de tekst te veranderen |
| **`infographic`** | het losse beeld dat in alle andere routes kan komen te staan: geen titel, geen omlijning, als SVG, als PowerPoint-slide, of als exhibit op het kader van de route die hem plaatst |
| **`sfnl-word`** | de snelle route: een notitie, een memo, een korte analyse — een tussenproduct in Word waar iemand in doortypt |
| **`online-design`** | HTML dat een scherm is en geen blad: een dashboard of interactief overzicht dat meegroeit, gemeten in beide themastanden |
| **`ontwerp-met-affinity`** | drukwerk opmaken in Affinity, met de maten uit de stramienen en niet uit de skill |
| **`deck-check`** | een bestaand deck opschonen en nakijken, op het beleid van `slides` |

**De plugin heette tot 1.6.0 `sfnl-slides`.** Met vier skills was die naam nog te verdedigen; met
acht is hij misleidend, want dan zoekt iemand een designplugin en slaat de slidesplugin over. Bij
2.0.0 is hij daarom `sfnl-design` geworden, en de skills hebben hun `sfnl-`-voorvoegsel afgelegd:
de plugin is de namespace, dus een skill spreek je aan als `sfnl-design:slides`. Dat kost iedereen
één keer opnieuw installeren. De repo blijft `xavier-friesen/sfnl-slides` heten — dat is de
git-URL waarmee de marketplace is toegevoegd, en die hernoemen kost meer dan hij oplevert.

`sfnl-word` houdt zijn voorvoegsel wel, en met opzet: het is de enige naam die tegen een bestaande
skill aan schuurt.

**Ze staan in één plugin omdat ze samengesteld worden, niet omdat ze op elkaar lijken.** Dat is
het verschil met acht losse skills die dezelfde kleuren gebruiken: ze delen de merklaag, de
huisstijlletters,
het voorblad, de canvasroute en de OOXML-primitieven, dus een infographic die in een document
komt te staan hoeft niet opnieuw uitgevonden te worden — hij wordt gebouwd op het canvas en de
maatladder van dat document. `reference/samenstellen.md` beschrijft wat gedeeld is en welke
ketens er zijn.

## rapport-deliverable — een aangeleverd rapport opmaken

De andere twee skills componeren elke pagina zelf. Deze doet iets anders: hij neemt een tekst die
al af is en laat hem door een systeem lopen. Bij tachtig pagina's kun je niet meer per pagina
beslissen.

- **De tekst verandert niet, en dat is te controleren.** `tekstcheck.py` plakt alle stukken met
  hetzelfde `data-bron` weer aan elkaar en vergelijkt karakter voor karakter met de brontekst uit
  het Word-document. Elke afwijking die niet in `wijzigingen.json` staat, blokkeert de oplevering.
  Op het proefrapport: 201 van 201 blokken woordelijk gelijk, in alle vier de modellen en in elke
  stand van het verwijzingsapparaat, en nul ongemarkeerde toevoegingen. Nagemeten met drie
  sabotages — een gewijzigd woord, een verwijderde alinea, een toegevoegde conclusie — en alle
  drie blokkeren.
- **De metingen liegen niet, en dat is apart gerepareerd.** `klip` mat marge en noemde dat
  verdwenen tekst; de meting kijkt nu naar de diepste tekstdragende node. Twee runs op hetzelfde
  bestand gaven verschillende uitkomsten omdat er niet op de beelden werd gewacht; drie runs geven
  nu een byte-identieke meting. En wat aan de zetting niet te zien was, heeft een eigen meting
  gekregen: een figuur van 3120 px in een kolom van 537 px komt op 2,7 pt kapitaalhoogte uit en is
  op papier onleesbaar, terwijl het beeld keurig binnen de kolom paste.
- **Wat de opmaak wél toevoegt, staat gemarkeerd**: de folio, de kopregel, de inhoudsopgave, de
  nummering, het nootcijfer, de herhaalde tabelkop, de omslagregels die de gebruiker zelf heeft
  opgegeven, de kop boven een eindnotenblok, het nummer voor een bronregel, het woord "Bijlagen"
  op het scheidingsblad en het bijschrift bij een apart aangeleverd beeld. Elf soorten, elk met
  `data-toevoeging`, en `tekstcheck.py` telt ze en schrijft ze uit. Alles daarbuiten zonder
  `data-bron` is tekst die niemand heeft goedgekeurd.
- **Voor elke inhoudelijke wijziging die de vorm zou willen, wordt expliciet toestemming
  gevraagd** — een kop inkorten, een alinea splitsen, van vier handgetypte streepjes een echte
  lijst maken. Zes soorten wijzigingen en meer bestaan er niet. `lees_docx.py` schrijft
  `signalen.json` met de waarnemingen; de skill maakt daar voorstellen van met de bron- en de
  doeltekst er letterlijk in; geen antwoord is nee.
- **Een eigen zetmotor**, want dit is niet met CSS alleen te doen. `paginator.js` splitst een
  alinea op de regelgrens met een `Range` en een binaire zoektocht, houdt twee regels aan tegen
  weduwen en wezen, laat een kop nooit zonder zijn tekst achter, herhaalt de kop van een tabel die
  over een paginagrens breekt, en zet de voetnoten op de pagina waar hun verwijzing staat — wat de
  tekstkolom inkort, waardoor het blok dat er net in paste alsnog moet verhuizen.
- **De inhoudsopgave klopt.** Zetten, de folio's aflezen, de opgave vullen, opnieuw zetten, tot de
  kaart twee rondes hetzelfde is. Loopt in twee tot drie rondes. `qa_rapport.py` controleert het
  daarna per blok-id en niet op koptekst, want twee secties kunnen dezelfde naam hebben.
- **Vier layoutmodellen, vier kleurregisters, drie hoofdstukopeners**, elk met een gerenderde
  keuzekaart die uit dezelfde pijplijn komt als het echte rapport en dus niets kan beloven wat de
  zetmotor niet doet.
- **Het verwijzingsapparaat is twee besluiten en geen één.** Waar de noten staan — voet, per
  hoofdstuk, achterin, of niet — staat los van de vraag of de bronnenlijst wordt opgemaakt
  (alfabetisch hangend of genummerd op citatievolgorde). Voetnoten *én* een bronnenlijst achterin
  is de gewoonste combinatie die er is. `lees_docx.py` detecteert wat de bron werkelijk heeft, en
  de skill biedt alleen dát aan: een bronnenlijst maken die er niet is, betekent bronregels
  schrijven.
- **Verwijzingen gelijktrekken telt als opmaak.** `(Boogers e.a. 2016)` wordt overal
  `(Boogers et al., 2016)`, of `[3]` als het rapport genummerd citeert. Dat is de enige tekst die
  zonder aparte toestemming wordt aangeraakt, en het is een uitdrukkelijk besluit: `citaten.py`
  schrijft elke omzetting vooraf op, `tekstcheck.py` speelt het plan terug tegen de bron en laat
  een blok dat méér is veranderd alsnog blokkeren, en bij de oplevering staan ze allemaal
  genoemd. Een verwijzing zonder bronregel blijft staan zoals hij stond.
- **Bijlagen krijgen een eigen scheidingsblad**, tellen in letters, en staan in de inhoudsopgave
  onder een eigen groepskop. De folio loopt gewoon door.
- **De dichtheid is een knop en geen grens.** Ruim, gemiddeld of dicht: 284, 295 of 318 woorden
  per tekstpagina, gemeten. De letter verandert niet mee — alleen het aantal regels in de
  zetspiegel en de lucht tussen de blokken.
- **Een kop blijft bij zijn tekst, ook als het in Word geen kop was.** Een alinea die volledig
  vetgezet is, kort, en met gewone tekst eronder, doet op de pagina het werk van een tussenkop.
  Alle drie de kop-blijft-bij-zijn-tekst-regels keken naar een kopstijl en zagen hem dus niet: op
  een rapport van 81 pagina's stonden er drie van de 28 als laatste regel van hun pagina, met hun
  tekst op de volgende, en geen enkele meting zag het. Ze worden nu gemarkeerd bij het inlezen,
  gebonden bij het zetten, en gemeten bij de controle — waar `losse-kop` van aanwijzing naar
  blokkade is gegaan, want dit is een belofte van de zetmotor en geen kwestie van smaak.
- **De kopregel is een besluit geworden**, met vier standen, en hij staat nooit op de pagina waar
  een hoofdstuk begint: daar zei hij in cursief grijs precies wat de titel eronder in 20 pt zegt.
  De bovenmarge is van 20 naar 25 mm gegaan omdat er tussen die kopregel en de eerste tekstregel
  21 px stond — minder dan één regel, en op een pagina die met een sectiekop begint stonden er
  twee koppen tegen elkaar aan met een streep ertussen. Dat kostte één regel per pagina, en die is
  terugverdiend met het volgende punt: hetzelfde rapport blijft op 81 pagina's.
- **Een blok dat past, blijft staan.** `past` mat `scrollHeight` en rekende de ondermarge mee; de
  splitser meet de tekstrechthoeken. Een alinea van vijftien regels in vijftien regels ruimte stak
  er 2 px uit — regelbox, geen letter — waarop `past` "vol" zei, de splitser "past heel", en het
  hele blok verhuisde. Vijftien regels wit achter, midden in een hoofdstuk, zonder klacht en
  zonder klip. Er is nu een derde meting die hetzelfde meet als de splitser, en waar het ondanks
  alles niet lukt is er een klacht `gat-in-de-pagina` met het aantal regels erin.
- **De vraag of er beeld in mag, wordt expliciet gesteld**, ook als er beeld in het Word-document
  zit. Bij apart aangeleverde figuren koppelt een `beeld.json` elk bestand aan een blok; een
  figuur zonder plek wordt niet geplaatst maar gemeld.
- **De intake begint bij wat er aan het document zelf is gezien.** `lees_docx.py` meldt zeven
  vormbesluiten bij het inlezen — de bron is niet Nederlands, de koppen beginnen bij niveau 2, ze
  nummeren zichzelf, een figuur is EMF en toont dus niet in een browser, er zit media buiten de
  tekststroom, een kop heeft geen inhoud, er staan vetgezette regels die als tussenkop werken.
  Vijf van de zes problemen van het eerste echte Engelse rapport waren hiermee vóór het bouwen te
  zien. `widget.py` zet ze bovenaan, met daaronder de vijfentwintig vormbesluiten; de uitvoer is
  de `ontwerp.json` die de gebruiker terugplakt, en de skill zegt met zoveel woorden dat er geen
  vormbesluit door `AskUserQuestion` gaat zolang dat script draait.
- **Twee van die zeven hebben een tweede poort.** Gebeurt er met `kop-zonder-inhoud` of
  `vetregel-als-kop` niets, dan komt het defect tachtig pagina's later terug op de pagina, en dan
  blokkeert de controle het alsnog. Op het rapport waar dit uit komt was de laatste pagina een
  bijlagetitel met 638 pt wit eronder, en de inhoudsopgave wees ernaar.
- **De taal is een vormbesluit en geen instelling achteraf.** `lang` bepaalt met welk woordenboek
  Chromium afbreekt en dus waar elke regel valt. Eén omzetting ná het zetten maakte drie alinea's
  een regel langer, en die regels vielen weg onder de `overflow: hidden` van het kader — tekst weg
  zonder foutmelding. De taal stuurt ook de labels: `Hoofdstuk 3` wordt `Chapter 3`.
- **Elke oplevering is drie dingen**: het losse HTML-bestand, de PDF op de bladmaat die het
  document zelf zegt, en de artboards voor het designcanvas. Geen vlag, geen keuze.

De maten komen uit twee bronnen: het SFNL-drukwerk, en drie nagemeten rapporten van Bain, BMC en
het McKinsey Global Institute. Die laatste leverden een uitkomst op die tegen de verwachting in
ging — geen van de drie vult zijn lopende tekst uit — en dat is de reden dat hier alleen het
dubbele model uitvult. `reference/rapport-vormentaal.md` §1 heeft de hele meting.

```bash
python scripts/rapport/preflight.py
python scripts/rapport/lees_docx.py rapport.docx --uit werk/
python scripts/rapport/widget.py werk/                      # de intakepagina
python scripts/rapport/citaten.py werk/ --naar uniform      # alleen als het besluit dat vraagt
python scripts/rapport/bouw.py werk/ --model breed --register helder --taal nl
#   levert in één keer het HTML-bestand, de PDF en werk/canvas/ met de artboards
python scripts/rapport/tekstcheck.py werk/rapport.html      # blokkeert
python scripts/rapport/render.py werk/rapport.html
python scripts/rapport/qa_rapport.py werk/rapport.html
```

## ontwerp-documenten — drukwerk in HTML

Een document is een reeks vaste bladen met een snijrand, geen scherm dat meegroeit. Wat er niet op
past, past niet, en dat hoort te blijken.

- **Het formaat is dat van de jaarrapporten**: 210 × 275 mm, niet A4. Dat is de reden dat ze als
  magazine lezen. A4, A5, de liggende spread en een drieluikpaneel zitten er ook in.
- **Eén bron, twee uitvoeren.** De `.dc.html`-artboards zijn de bron. `bouw.py` leidt er het losse
  print-HTML uit af *en* de spreadindeling voor het design-canvas, en houdt ze in de pas. Bewerkt
  de gebruiker een pagina in het canvas en slaat hij op, dan haal je hem er als artboard weer uit.
- **De letters zitten ingesloten**, als `@font-face` met een data-URI onder de OFL. Een document dat
  zijn letters van Google Fonts haalt, valt terug op Helvetica zodra er geen internet is, en de
  export van het canvas neemt ze sowieso niet mee.
- **`qa_document.py` meet wat stil misgaat**: tekst die door `overflow: hidden` is weggevallen, een
  element dat over de snijrand steekt, een gat van 300 px in het midden van een pagina, wit op
  oranje op contrast 2,6. Drie ervan blokkeren; de rest is een aanwijzing en de render beslist.
- **Tien vragen vóór de eerste regel tekst, en ze staan op één scherm.** `widget.py` genereert een
  formulier met de vijf opdrachtvragen als vrije velden en de vijf vormbesluiten als knoppen, met
  een schets die meebeweegt en de katernsom eronder zodra het gedrukt wordt: formaat, omvang (van
  één pagina tot zestien, of laat het uit de inhoud volgen), kleurregister, tekst tegenover beeld,
  en de opening — komt de dektitel op een heel voorblad, in een aflopende titelbalk, of gewoon in
  de zetspiegel. Hoe hóófdstukken openen is een andere vraag en die staat in de outline, want hij
  bestaat pas vanaf acht pagina's. Dit ging eerst in twee rondes `AskUserQuestion` van vier
  knoppen, en dan zie je het geheel op geen enkel moment; de skill zegt nu met zoveel woorden dat
  daar geen vormbesluit meer door gaat.
- **Ruimte voor een infographic** is een merkteken, geen losse div: `.beeldkader` houdt de
  verhouding vast, en een kader waar het beeld nog niet in zit staat er zichtbaar leeg bij in
  plaats van als witruimte mee te lezen.
- **Er is geen paginabibliotheek.** `stijl.css` geeft het kader, het raster, de maatladder, de
  kleurregels en twintig merktekens die elk één ding tekenen. De compositie is elke pagina
  opnieuw een beslissing.
- **Op één pagina geldt dat niet, en dat is het voorblad.** `.omslag` is het enige paginatype met
  een eigen klasse: drie zones met een vaste rangorde, vier velden die woordelijk van de
  gebruiker komen, en het is hetzelfde component waarmee `rapport-deliverable` zijn omslag zet.
  Het staat daarom in `stijl.css` en niet in de rapportlaag; `rapport.css` zet er twee
  maatvariabelen op en verder niets. Vóór dat component bestond, leverden twee handgecomponeerde
  voorbladen twee verschillende maatladders op. Het kleurveld is een regel en geen smaak: een
  executive summary staat op navy, elk ander document op het huisverloop tenzij erom gevraagd
  wordt.

Alle maten en kleuren komen uit twee gemeten drukwerken: het jaarrapport 2025 en de casespread
Civitates. Wat er in `reference/documenten-stramien.md` staat met "gemeten" ernaast, komt daaruit.

```bash
python scripts/documenten/preflight.py
python scripts/documenten/widget.py <werkmap> --titel "Uitnodiging"
python scripts/documenten/bouw.py <werkmap> --uit uitnodiging.html --titel "Uitnodiging"
python scripts/documenten/render.py <werkmap>/uitnodiging.html
python scripts/documenten/qa_document.py <werkmap>/uitnodiging.html
```

## slides — een deck uit het sjabloon

### Waarom deze route naast `sfnl-powerpoint` bestaat

`sfnl-powerpoint` heeft de betrouwbaarheid opgelost. Geen kapotte bestanden, geen overlopende
tekst, geen placeholders die blijven staan, een gehandhaafd layoutbeleid. Dat werkt, en het
blijft bestaan.

Wat er onderweg verloren ging, is oordeelsvorming over de vorm. `compose.py` is een
patroonbibliotheek van 2960 regels, `deck_spec.py` valideert 2317 regels aan vormbeslissingen
voordat er iets getekend wordt, en `geometry.json` legt vast hoe hoog een kaartgetal staat en
hoeveel tekens een tegelcaption mag hebben. Wie zo bouwt, kiest niet meer maar vult in. In een
blinde vergelijking van vijf briefs verloor die route van de oudere, veel simpelere skill die
Claude gewoon liet ontwerpen.

Deze plugin neemt de dunne laag mee en laat de vormgevingspolitie liggen.

| | `sfnl-powerpoint` | `slides` |
|---|---|---|
| Vorm per slide | gekozen uit tien patronen, vastgelegd in een spec | zelf gecomponeerd tijdens het bouwen |
| Poorten | outline, spec, QA-drempels | twee, en beide zijn een mens: het vragenvuur en de outline |
| Vormbeoordeling | `qa_fit.py` en `qa_typography.py` meten, daarna de render | de render, met tellingen als hygiëne ernaast |
| Scripts | ± 18.100 regels | ± 13.600 regels |
| Skills | vijf | één |

## infographic — het losse beeld

Een visual die ergens ánders in komt te staan. Geen titel, geen oranje dash, geen kader: die
draagt de container. Wat overblijft is de compositie, en die is elke keer een ontwerpbeslissing.

- **Het vormenwoordenboek is de kern.** Zesenveertig vormen op één blad, structureel getekend en
  geordend naar de vraag die ze beantwoorden, met een vormtoets ernaast die per vorm zegt wat hij
  aan gegevens eist. Zonder dat blad kiest een bouwer wat er het eerst opkomt, en dat is een rij
  kaarten — de enige vorm waarin geen enkele meting iets bepaalt.
- **Een figuur of een rooster, en dat onderscheid loopt door de hele skill.** In een figuur
  bepaalt een meting een lengte, een x, een dikte of een hoek; verandert het getal, dan verandert
  de tekening. In een rooster niet. Vijfenveertig van de zesenveertig vormen zijn een figuur, en
  de stappen zijn erop gebouwd dat dat de gewone uitkomst is.
- **Drie schetsen vóór er gebouwd wordt.** Ze kosten een tiende van één gebouwde infographic en
  ze worden op een canvas voorgelegd, met per concept vier regels: de plattegrond, welke meting
  welke maat bepaalt, wat de boodschap draagt, en wat het kost.
- **Vier routes.** Een SVG, een PowerPoint-slide op layout 19, 17, 21 of 22, een native grafiek
  of tabel als de telling daarop uitkomt, en een exhibit op het kader van een zusterskill.
- **De letters worden gemeten, niet geschat.** De plugin draagt Montserrat en Lato zelf mee, dus
  de regelafbreking klopt op een kale machine zonder netwerk. Hetzelfde bestand rendert de PNG's.

```bash
python scripts/infographic/preflight.py --herstel
python scripts/infographic/render_svg.py uitvoer/*.svg --wit --schaal 1 --knijp
python scripts/infographic/insluiten.py uitvoer/beeld.svg --doel document --kader breed
```

Die laatste is de poort naar de andere drie skills, en hij toetst drie dingen die je op de render
van het beeld zelf niet ziet.

- **De maten.** Een SVG schaalt alles mee, ook zijn letters. Een band van 960 × 320 pt krimpt in
  het documentkader van 680 px met factor 0,53 en zet daarmee een voetnoot van 10 pt op 5,31 pt.
  Hetzelfde beeld gebouwd op `CANVAS["doc-breed"]` haalt factor 1,0 — en de gebouwde pagina komt
  schoon door `qa_document.py` waar de eerste versie er elf `critical` opleverde.
- **De omlijsting.** Een los beeld draagt zijn eigen aanhef en bronregel, want er is niets
  anders. Een exhibit staat onder een kop en boven een bijschrift, dus alles wat het beeld
  daarvan herhaalt is een tweede stem. De labels bij de elementen zijn geen dubbeling en blijven
  staan: direct labelen gaat voor.
- **Het dode wit.** De verhouding van het kader komt uit de `viewBox`, dus een canvas dat voor 70
  procent gevuld is, reserveert 30 procent witruimte op de pagina — onzichtbaar in het beeld,
  zichtbaar op papier. `pas_hoogte(c, vormen)` zet de hoogte op de compositie.

Wat de eerste twee scheidt staat in `reference/samenstellen.md`: een exhibit rekent in de px van
zijn container en niet in punten, want het meetapparaat van die container leest de opgegeven maat
en niet de gerenderde.

## De merklaag — de kleurwaarde staat één keer

`reference/merk.md` is de enige plek in de repo waar een kleurwaarde, een letterfamilie of het
logo staat. `scripts/gedeeld/merk.py` is de machineleesbare vorm ervan, en
`assets/gedeeld/merk.css` wordt daaruit gestempeld.

De regel eronder: **een kleurwaarde staat één keer, een kleurregel staat per medium.** Een rapport
en een PowerPoint horen verschillende maatladders te hebben — die zijn aan verschillend drukwerk
gemeten — maar hun oranje niet. De toets is mechanisch en `preflight.py` doet hem: staat er een
merk-hexwaarde in een script of een stylesheet buiten de merklaag, dan blokkeert dat; staat er een
puntgrootte in `merk.md`, dan hoort die daar niet.

- **Het Word-sjabloon is de merkbron, en de plugin is daarop aangepast.** Vijf van de zes accenten
  stonden naast het sjabloon: oranje ging van `#F87F4F` naar `#FF7F40`, navy van `#201B5C` naar
  `#21145F`, en zo ook grapefruit, emerald en royal. Navy stond 26 keer in `styles.xml` van het
  sjabloon, dus dat was geen uitschieter in één stijl. Geen enkele vormregel veranderde erdoor:
  oranje op wit ging van 2,58 naar 2,51 en haalt dus nog steeds geen van beide drempels, navy op
  oranje van 5,93 naar 6,29.
- **Wat de fase rechtvaardigde zat in `qa_document.py`.** Daar stond het hele palet een tweede
  keer, als rgb-drielingen. Na de migratie meldde die poort op élk document "kleur buiten het
  palet: rgb(255, 127, 64)" — het merkoranje zelf. Twee kopieën van dezelfde waarheid, en de ene
  keurde de andere af.
- **Welke tekstkleur op welk vlak staat, is geen smaak.** `merk.md` §1 heeft de paringstabel met
  alle verhoudingen. De val zit in de twee donkere vlakken: navy op royal haalt 2,70 en navy op
  violet 2,86, dus daar staat wit — en dat is precies de fout die je maakt als je "navy is de
  inkt" als regel toepast in plaats van als vertrekpunt.
- **Eén uitzondering, en die is gebonden.** Wit op oranje haalt dezelfde 2,51 als oranje op wit,
  want de verhouding is symmetrisch. Het mag toch, want het gedrukte werk doet het — maar alleen
  in drukwerk, alleen voor korte tekst op display- of leadmaat, en nooit voor een getal of een
  bronregel. Op een scherm geldt de uitzondering niet.

## sfnl-word — de snelle route

Snel en Word zijn dezelfde as en niet twee assen. Een tussenproduct is per definitie een document
waar iemand in doortypt, en dat is precies wat Word is en wat HTML en PDF niet zijn. De
formaatkeuze doet daarmee het werk dat anders een disciplineoordeel had moeten doen: een lichte
route naast een strenge wint normaal zodra iemand haast heeft, maar deze wint alleen waar hij het
juiste formaat is.

Geen intakewidget, geen outline-poort, geen renderloop van drie ronden — wél het document één keer
openen en bekijken voordat je oplevert. En een verplichte sluitregel: *dit is een werkdocument;
moet het naar buiten, dan wordt het mooier met `ontwerp-documenten` of `rapport-deliverable`*.
Zonder die regel wordt de snelle route de gewone route en gaat er een `.docx` naar een fonds.

`reference/word-stramien.md` is het sjabloon nagemeten. Wat daar het meest uitmaakt:

- **Alle stijl-id's zijn Nederlands** — `Standaard`, `Kop1`–`Kop9`, `Titel`, `TableGrid1`. Dit is
  de belangrijkste bouwersval: `w:pStyle w:val="Heading1"` valt stil terug op `Standaard`, en
  `qa_word.py` blokkeert erop.
- **`Kop1` vraagt Gotham Bold Regular**, een licentiefont. Op een SFNL-machine staat het, in een
  sandbox en op de machine van een klant niet, en dan substitueert Word stil. De skill maakt daar
  een expliciet besluit van met Montserrat SemiBold als terugval, en noemt bij de oplevering welke
  van de twee in het bestand staat.
- **Het blad is geen echte A4** — `pgSz` is 209,90 × 297,03 mm — dus reken de zetspiegel uit
  `pgSz` en niet uit "A4 min marges". Dat is 159,10 mm en niet 159,20.
- **Het sjabloon is een stijlendrager en geen voorbeeldpagina**: het bevat één lege alinea, en die
  staat op 11 pt met directe opmaak. Wie erin begint te typen, typt in 11 pt.
- **Twee lijsten achter elkaar smelten samen**, en dat is op de pagina te zien en in de XML niet.
  `Lijstalinea` draagt `contextualSpacing`, en dat is geen waarde die je overschrijft maar een
  schakelaar die de afstand negeert — `w:spacing w:before` erbij zetten verandert niets.

## online-design — het scherm

Een blad is vast en een scherm groeit mee, en dat is niet één instelling verschil. `ontwerp-documenten`
weigert een dashboard met zoveel woorden; deze route is de andere helft van die zin.

- **Donkere modus is een vormbesluit en geen instelling.** Navy wordt de grond, wit de inkt, en die
  verhouding blijft exact 15,79 beide kanten op. Maar daarachter **klapt de rangorde om**: royal en
  violet dragen op wit een alinea (5,85 en 5,52) en zakken op navy naar 2,70 en 2,86; emerald, sky
  en oranje mogen op wit geen letter dragen (1,98, 2,32, 2,51) en halen op navy 7,99, 6,80 en 6,29.
  Daaruit volgt de regel: behalve navy en wit is er **geen merkkleur die in beide thema's een regel
  kan dragen**, dus oranje draagt op een scherm nooit een gelezen regel.
- **De volle merkvlakken wisselen niet mee met het thema** — oranje is licht in beide standen, dus
  de inkt erop is navy in beide — en dat is het anker tussen de twee.
- **De breedte groeit, de maatladder niet.** Zes maten vast in px, de leesmaat op ongeveer 70
  tekens, en geen `clamp()` op de viewport voor tekst: een maat die van de vensterbreedte afhangt
  geeft twee hiërarchieën en valt niet na te meten.
- **Toegankelijkheid is hier een blokkade en geen aanwijzing.** Op papier kun je 2,51 verdedigen als
  merkteken; in een browser met een screenreader vangt niemand het voor je op.
- **`dataviz` is ingebed en niet overschreven.** Met de validator van die skill gemeten draagt het
  palet **drie categorieën en geen vier**: royal, oranje en emerald halen alle checks, en elke
  vierde merkkleur brengt een paar onder de zichtvloer mee.
- **De grens is hard**: één pagina, geen buildstap, geen backend. Dit is de route die het meest
  gevoelig is voor scope creep richting "bouw een React-app", en dat is softwareontwikkeling en
  geen huisstijlopdracht.

## ontwerp-met-affinity — uitvoeren wat de stramienen bepalen

Deze skill draagt geen eigen maten, en dat is een besluit. Er stond een eigen bladmaat, een eigen
raster, een eigen kleurtabel en een eigen typografieladder, en die beschreven hetzelfde blad als de
stramienen — twee bestanden over één blad lopen na de eerste correctie uit elkaar, en dan is
onduidelijk welk van de twee het drukwerk is.

Wat overblijft is de laag die nergens anders staat: de SDK lezen voordat je hem gebruikt, de
scriptbibliotheek vóór en ná, van de eenheid van het stramien naar die van het document komen, de
plekken waar de SDK stil iets anders doet dan je denkt, en `render_spread` als enige vormoordeel.
Het bouwscript heeft alle maten op `null` staan met een keuringslus die faalt met het pad van de
eerste ontbrekende sleutel: een geraden maat is in Affinity niet van een opgezochte te
onderscheiden, en op de render al helemaal niet.

Wat hij niet doet is een rapport zetten. Loopt het over meer dan een paar pagina's, dan is de
zetmotor van `rapport-deliverable` beter dan de hand.

## deck-check — een bestaand deck opschonen

De tegenhanger van `slides`, en een eigen bestand omdat het triggersignaal een ander is: "bouw een
deck" tegenover "hier is een deck, check het". Eén description die beide dekt laat de bouwroute
vuren op een upload.

Wat gedeeld wordt is het beleid. Het eigen typografiebeleid van de bronskill is eruit en wordt nu
gelezen uit `reference/sjabloon.md` en `reference/vormentaal.md` — twee definities van "wat mag op
een SFNL-slide" is er één te veel. Drie regels in dat blok bleken bovendien niet dubbel maar fout,
en zouden als tweede definitie van de huisstijl zijn meegereisd: de bron zette de subtitel in
kapitalen waar `voice.md` zinsvorm eist, schreef een eigen navy en puur zwart voor de body, en
handhaafde posities op vaste centimeters. Deck-check schrijft nu geen kleur, font, maat of
geometrie meer — alleen tekst — en vergelijkt een placeholder met dezelfde placeholder in zijn
eigen layout, wat ook werkt op decks van buiten het sjabloon.

Wat compleet is gebleven, is de kern die nergens anders staat: de bestandsdetectie vóór alles, de
PLAN → GLOBAL → APPLY-werkwijze met haar read-only en write-only fasen, de roldetectie, de Do Not
Touch-lijst, en alle acht tekstregelgroepen — eindinterpunctie, slashspatiëring, dubbele spaties,
interpunctiespatiëring, kapitalisatie, bullets, aanhalingstekens en streepjes. Wat de bron zei en
de referenties niet, is winst en staat nu in `vormentaal.md` §9.

## Installeren

Deze plugin woont in zijn eigen repo en staat daar op de root, dus rechtstreeks vanaf git:

```
/plugin marketplace add xavier-friesen/sfnl-slides
/plugin install sfnl-design@sfnl
```

De marketplace heet `sfnl` — de organisatie, niet de plugin — dus de plugin heet overal
`sfnl-design@sfnl`. Werk je in de monorepo waar deze plugin naast `sfnl-powerpoint` staat, dan
wijst de marketplace in die repo-root met een relatief pad naar beide plugins:

```
/plugin marketplace add .
/plugin install sfnl-design
```

**Bijwerken naar een nieuwe versie gaat niet vanzelf.** Auto-update staat voor een eigen
marketplace standaard uit, dus een geïnstalleerde kopie blijft op zijn versie staan:

```
/plugin marketplace update sfnl
/plugin install sfnl-design@sfnl
/reload-plugins
```

Zet auto-update aan via `/plugin` → Marketplaces → Enable auto-update, of org-breed met
`"autoUpdate": true` op de `extraKnownMarketplaces`-regel in managed settings.

Daarna spreek je een skill aan als `/sfnl-design:slides` — de plugin is de namespace. Beide
plugins kunnen naast elkaar geïnstalleerd staan; ze delen geen bestanden en importeren niet over
de grens.

Stond `sfnl-slides` er al, dan verdwijnt die niet van zichzelf: `/plugin` → Marketplaces →
`sfnl` → verwijder de oude plugin, dan de nieuwe installeren. Twee kopieën naast elkaar geeft
twee skills die op hetzelfde triggeren.

## Wat er in zit

```
reference/merk.md               de merklaag: kleuren, letters, logo, de paringstabel, de weigerlijst
scripts/gedeeld/merk.py         de machineleesbare vorm; --css stempelt assets/gedeeld/merk.css
reference/samenstellen.md       wat de skills delen en welke ketens er zijn
scripts/gedeeld/                canvas, drukwerk, naar_pdf, merk — wat meer dan één skill gebruikt

skills/slides/                  de deckroute: vragenvuur, outline, zes bouwstappen, de loop
reference/vormentaal.md         de maatstaf in proza — waar de lat ligt
reference/adviesvorm.md         de laag erboven — antwoord voorop, exhibitcraft, weigerlijst
reference/sjabloon.md           geometrie, layouts, placeholderdozen, negen valkuilen
reference/merktekens.md         dertig merktekens uit elf decks, met wat elk codeert
reference/voice.md              de taal op de slide
reference/layouts.json          de sjabloonfeiten per layout, waar de scripts op keyen
agents/deck-visual-reviewer.md  de visuele beoordeling, als subagent
assets/sfnl-sjabloon.potx       het geprunde sjabloon, 5,5 MB
assets/maatstaf/                veertien slides: tien uit winnende decks, vier reconstructies
assets/proeven/                 de kleur- en gevuldheidsproef, met de metingen eronder
assets/keuzekaarten/            de keuzekaart die bij het vragenvuur meegaat

skills/deck-check/              de opschoonroute: vind, PLAN, GLOBAL, APPLY, logboek
scripts/deckcheck/              vind.py, tekstregels.py, plan.py, toepassen.py

skills/ontwerp-documenten/      de drukwerkroute in HTML: widget, compositie, render, QA
reference/documenten-vormentaal.md  de maatstaf, plus achttien dingen die het door een model
reference/documenten-stramien.md    de feiten: bladmaten, raster, maatladder, merktekens
assets/documenten/stijl.css     het kader, het raster, twintig merktekens, het voorblad
assets/documenten/fonts/        de huisstijlletters als woff2, ingesloten via fonts.css
assets/documenten/maatstaf/     vijf gebouwde pagina's als contactblad
scripts/documenten/             bouw, render, qa_document, widget, _browser

skills/rapport-deliverable/     de zetroute: inlezen, vormbesluiten, wijzigingsvoorstellen, zetten
reference/rapport-vormentaal.md de maatstaf: de metingen aan Bain, BMC en MGI, de weigerlijst
reference/rapport-stramien.md   de feiten: raster, vier modellen, vier registers, klassenlijst
assets/rapport/rapport.css      de rapportlaag boven stijl.css
assets/rapport/keuzekaarten/    drie gerenderde keuzekaarten: modellen, registers, openers
assets/rapport/maatstaf/        vier gezette pagina's als maatstaf
scripts/rapport/                de zetmotor en de checks, met paginator.js

skills/infographic/             de beeldroute: intake, vormtoets, schetsen, vier bouwroutes
reference/infographic-vormentaal.md  de maatstaf voor een titelloos, kaderloos beeld
reference/infographic-vormkeuze.md   de vormtoets: wat elke vorm eist en hoeveel erin past
assets/infographic/vormen/      het vormenwoordenboek: zesenveertig vormen op één blad
assets/infographic/maatstaf/    vijf afgemaakte infographics plus de drie schetsen
assets/infographic/voorbeeld/   hun bouwscripts, met in elke docstring wat er misging
scripts/infographic/            svg.py, schets.py, render_svg.py, insluiten.py, blanco.py

skills/sfnl-word/               de snelle route naar een werkdocument in Word
reference/word-stramien.md      het sjabloon nagemeten: blad, stijlen, letters, valkuilen
assets/word/                    het SFNL-Word-sjabloon zelf
scripts/word/                   bouw.py, qa_word.py, preflight.py

skills/online-design/           de schermroute: één pagina, beide thema's, harde grens
reference/online-vormentaal.md  de maatstaf voor een scherm, met de donkeremodus-meting
assets/online/stijl.css         de schermlaag boven merk.css, met zestien merktekens
assets/online/maatstaf/         het dashboard dat de lat is, met zijn LEESMIJ
scripts/online/                 bouw.py, render.py, qa_online.py, preflight.py

skills/ontwerp-met-affinity/    de Affinity-laag: SDK, eenheden, valkuilen, render_spread

scripts/                        de dunne laag voor de deckroute
```

## De dunne laag

Twintig scripts plus `office/`, samen ongeveer 13.600 regels — 10.400 in `scripts/` en 3.200
in `office/`. Ze dragen de kennis uit vijf
QA-rondes: dat een `.potx` zijn content-type naar `presentation.main` moet, dat LibreOffice op
Windows over `MAX_PATH` valt, dat `python-pptx` grafieken sloopt als je na `add_chart` nog een
keer in- en uitpakt, waar de huisstijlfonts staan.

| Script | Waarvoor |
|---|---|
| `preflight.py` | is er een interpreter, een renderer, de fonts |
| `prepare_template.py` | sjabloon uitpakken en het content-type omzetten |
| `add_slide.py` | een layout instantiëren; hiermee erft de slide zijn header |
| `set_text.py` | geërfde placeholders vullen |
| `shapes.py` | de primitieven: vlak, lijn, tekstrun, raster, hoogtemeting, merktekens, `contour()` voor een eigen vorm en `icoon()` voor een zelfgetekend lijnicoon |
| `place_shapes.py` | vormen op naam verschuiven of herschalen, in inch |
| `clean.py` | lege placeholders eruit, XML normaliseren, ongebruikte layouts weg |
| `office/pack.py`, `unpack.py`, `validate.py` | in- en uitpakken met schemavalidatie |
| `add_chart.py`, `add_table.py` | native grafiek en tabel, ná het inpakken |
| `render.py`, `thumbnail.py` | slides naar PNG en een contactblad |
| `qa_text.py` | hygiëne: restplaceholders, Calibri, harde hex, rechte apostrof |
| `keuzekaart.py` | onderhoud: bouwt de keuzekaart voor het vragenvuur uit de renders in `assets/` |
| `qa_tellingen.py` | tellingen: maten per rol, bandfrequentie, exhibits bij cijfers, maatsprong, letterfamilies, hoge punt — plus woorden, registers en plattegrond als cijfer zonder oordeel |
| `fit_title.py` | past een titel op één regel, gemeten met het echte font |
| `inspect_deck.py` | wat staat er werkelijk op de slide |
| `duplicate_slide.py`, `retext_slide.py` | een bestaand deck uitbreiden |
| `prune_template.py` | het sjabloonasset herbouwen uit het merkorigineel |

Wat er bewust niet in zit: `compose.py`, `deck_spec.py`, `build_deck.py`, `layout_catalog.py`,
`qa_fit.py`, `qa_typography.py`, `fit_box.py` en `geometry.json`. Samen ongeveer 10.800 regels
patroonbibliotheek, spec-contract en meting-op-maat.

## Wat blokkeert

Zes dingen. Drie van de soort "het bestand is stuk" — het content-type staat niet op
`presentation.main`, `pack.py` meldt een schemafout, de grafieken zijn verdwenen na de laatste
`pack` — en drie `critical`s uit een script: `qa_text.py`, `fit_title.py` en `qa_tellingen.py`.
Wat daarin over vorm gaat is te tellen zonder interpretatie: de titelletter, één maat per rol,
één letterfamilie per alinea, de hoge punt, en een titel die over zijn subtitel heen groeit.
`SKILL.md` somt ze op onder "Wat blokkeert".

De vorm wordt beoordeeld op de render. Is er geen renderer, dan bouwt de skill conservatiever
en zegt bij oplevering letterlijk dat het deck niet visueel geverifieerd is.

## Ontwerp

Waarom deze route bestaat, wat er meegaat en wat er blijft liggen, staat vast in
`docs/superpowers/specs/2026-07-31-slides-design.md`. Dat document hoort bij de
vergelijking tussen beide routes en blijft daarom in de monorepo staan; het reist niet mee met
deze plugin-repo.
