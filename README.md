# sfnl-slides

Drie skills die dezelfde regel volgen: de vorm is een ontwerpbeslissing en geen invuloefening, en
de render is de enige vormbeoordeling.

| skill | wat je ermee maakt |
|---|---|
| **`sfnl-slides`** | een SFNL-deck uit het officiële `.potx`-sjabloon |
| **`sfnl-design-documents`** | kort drukwerk in HTML: een uitnodiging, een executive summary, een proposal, een spread |
| **`sfnl-rapport-opmaak`** | een afgerond Word-rapport van twintig tot honderdvijftig pagina's, opgemaakt zonder één woord aan de tekst te veranderen |

De plugin blijft `sfnl-slides` heten, ook nu er drie skills in zitten: dat is de naam waarmee hij
geïnstalleerd staat, en hernoemen zou iedereen tot opnieuw installeren dwingen.

## sfnl-rapport-opmaak — een aangeleverd rapport opmaken

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
- **De vraag of er beeld in mag, wordt expliciet gesteld**, ook als er beeld in het Word-document
  zit. Bij apart aangeleverde figuren koppelt een `beeld.json` elk bestand aan een blok; een
  figuur zonder plek wordt niet geplaatst maar gemeld.
- **Vijftien besluiten passen niet in een gesprek**, dus `widget.py` genereert er een pagina van:
  alles op één scherm met een schets die meebeweegt, per rapport samengesteld uit wat de bron
  werkelijk bevat. De uitvoer is de `ontwerp.json` die de gebruiker terugplakt.

De maten komen uit twee bronnen: het SFNL-drukwerk, en drie nagemeten rapporten van Bain, BMC en
het McKinsey Global Institute. Die laatste leverden een uitkomst op die tegen de verwachting in
ging — geen van de drie vult zijn lopende tekst uit — en dat is de reden dat hier alleen het
dubbele model uitvult. `reference/rapport-vormentaal.md` §1 heeft de hele meting.

```bash
python scripts/rapport/preflight.py
python scripts/rapport/lees_docx.py rapport.docx --uit werk/
python scripts/rapport/widget.py werk/                      # de intakepagina
python scripts/rapport/citaten.py werk/ --naar uniform      # alleen als het besluit dat vraagt
python scripts/rapport/bouw.py werk/ --model breed --register helder
python scripts/rapport/tekstcheck.py werk/rapport.html      # blokkeert
python scripts/rapport/render.py werk/rapport.html
python scripts/rapport/qa_rapport.py werk/rapport.html
```

## sfnl-design-documents — drukwerk in HTML

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
- **Vijf besluiten vóór de eerste regel tekst**, met een gerenderde keuzekaart erbij: formaat,
  omvang (van één pagina tot zestien, of laat het uit de inhoud volgen), kleurregister, tekst
  tegenover beeld, en de opening — komt de dektitel op een heel titelblad, in een aflopende
  titelbalk, of gewoon in de zetspiegel. Hoe hóófdstukken openen is
  een andere vraag en die staat in de outline, want hij bestaat pas vanaf acht pagina's.
- **Ruimte voor een infographic** is een merkteken, geen losse div: `.beeldkader` houdt de
  verhouding vast, en een kader waar het beeld nog niet in zit staat er zichtbaar leeg bij in
  plaats van als witruimte mee te lezen.
- **Er is geen paginabibliotheek.** `stijl.css` geeft het kader, het raster, de maatladder, de
  kleurregels en twintig merktekens die elk één ding tekenen. De compositie is elke pagina
  opnieuw een beslissing.

Alle maten en kleuren komen uit twee gemeten drukwerken: het jaarrapport 2025 en de casespread
Civitates. Wat er in `reference/documenten-stramien.md` staat met "gemeten" ernaast, komt daaruit.

```bash
python scripts/documenten/preflight.py
python scripts/documenten/bouw.py <werkmap> --uit uitnodiging.html --titel "Uitnodiging"
python scripts/documenten/render.py <werkmap>/uitnodiging.html
python scripts/documenten/qa_document.py <werkmap>/uitnodiging.html
```

## sfnl-slides — een deck uit het sjabloon

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

| | `sfnl-powerpoint` | `sfnl-slides` |
|---|---|---|
| Vorm per slide | gekozen uit tien patronen, vastgelegd in een spec | zelf gecomponeerd tijdens het bouwen |
| Poorten | outline, spec, QA-drempels | twee, en beide zijn een mens: het vragenvuur en de outline |
| Vormbeoordeling | `qa_fit.py` en `qa_typography.py` meten, daarna de render | de render, met tellingen als hygiëne ernaast |
| Scripts | ± 18.100 regels | ± 13.600 regels |
| Skills | vijf | één |

## Installeren

Deze plugin woont in zijn eigen repo en staat daar op de root, dus rechtstreeks vanaf git:

```
/plugin marketplace add xavier-friesen/sfnl-slides
/plugin install sfnl-slides@sfnl
```

De marketplace heet `sfnl` — de organisatie, niet de plugin — dus de plugin heet overal
`sfnl-slides@sfnl`. Werk je in de monorepo waar `sfnl-slides` naast `sfnl-powerpoint` staat, dan
wijst de marketplace in die repo-root met een relatief pad naar beide plugins:

```
/plugin marketplace add .
/plugin install sfnl-slides
```

**Bijwerken naar een nieuwe versie gaat niet vanzelf.** Auto-update staat voor een eigen
marketplace standaard uit, dus een geïnstalleerde kopie blijft op zijn versie staan:

```
/plugin marketplace update sfnl
/plugin install sfnl-slides@sfnl
/reload-plugins
```

Zet auto-update aan via `/plugin` → Marketplaces → Enable auto-update, of org-breed met
`"autoUpdate": true` op de `extraKnownMarketplaces`-regel in managed settings.

Daarna is `/sfnl-slides` het commando. Beide plugins kunnen naast elkaar geïnstalleerd staan;
ze delen geen bestanden en importeren niet over de grens.

## Wat er in zit

```
skills/sfnl-slides/SKILL.md     de route: vragenvuur, outline, zes bouwstappen, de loop
skills/sfnl-rapport-opmaak/     de zetroute: inlezen, vormbesluiten, wijzigingsvoorstellen, zetten
reference/rapport-vormentaal.md de maatstaf: de metingen aan Bain, BMC en MGI, de weigerlijst
reference/rapport-stramien.md   de feiten: raster, vier modellen, vier registers, klassenlijst
assets/rapport/rapport.css      de rapportlaag boven stijl.css
assets/rapport/keuzekaarten/    drie gerenderde keuzekaarten: modellen, registers, openers
assets/rapport/maatstaf/        vier gezette pagina's als maatstaf
scripts/rapport/                de zetmotor en de checks
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
scripts/                        de dunne laag
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
`docs/superpowers/specs/2026-07-31-sfnl-slides-design.md`. Dat document hoort bij de
vergelijking tussen beide routes en blijft daarom in de monorepo staan; het reist niet mee met
deze plugin-repo.
