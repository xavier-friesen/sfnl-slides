# sfnl-slides

Twee skills die dezelfde regel volgen: de vorm is per stuk een ontwerpbeslissing en geen
invuloefening, en de render is de enige vormbeoordeling.

| skill | wat je ermee maakt |
|---|---|
| **`sfnl-slides`** | een SFNL-deck uit het officiële `.potx`-sjabloon |
| **`sfnl-design-folders`** | drukwerk in HTML: een uitnodiging, een executive summary, een proposal, een spread |

De plugin blijft `sfnl-slides` heten, ook nu er twee skills in zitten: dat is de naam waarmee hij
geïnstalleerd staat, en hernoemen zou iedereen tot opnieuw installeren dwingen.

## sfnl-design-folders — drukwerk in HTML

Een folder is een reeks vaste bladen met een snijrand, geen scherm dat meegroeit. Wat er niet op
past, past niet, en dat hoort te blijken.

- **Het formaat is dat van de jaarrapporten**: 210 × 275 mm, niet A4. Dat is de reden dat ze als
  magazine lezen. A4, A5, de liggende spread en een drieluikpaneel zitten er ook in.
- **Eén bron, twee uitvoeren.** De `.dc.html`-artboards zijn de bron. `bouw.py` leidt er het losse
  print-HTML uit af *en* de spreadindeling voor het design-canvas, en houdt ze in de pas. Bewerkt
  de gebruiker een pagina in het canvas en slaat hij op, dan haal je hem er als artboard weer uit.
- **De letters zitten ingesloten**, als `@font-face` met een data-URI onder de OFL. Een folder die
  zijn letters van Google Fonts haalt, valt terug op Helvetica zodra er geen internet is, en de
  export van het canvas neemt ze sowieso niet mee.
- **`qa_folder.py` meet wat stil misgaat**: tekst die door `overflow: hidden` is weggevallen, een
  element dat over de snijrand steekt, een gat van 300 px in het midden van een pagina, wit op
  oranje op contrast 2,6. Drie ervan blokkeren; de rest is een aanwijzing en de render beslist.
- **Vijf besluiten vóór de eerste regel tekst**, met een gerenderde keuzekaart erbij: formaat,
  omvang, kleurregister, tekst tegenover beeld, en de opening — komt de dektitel op een heel
  titelblad, in een aflopende titelbalk, of gewoon in de zetspiegel. Hoe hóófdstukken openen is
  een andere vraag en die staat in de outline, want hij bestaat pas vanaf acht pagina's.
- **Ruimte voor een infographic** is een merkteken, geen losse div: `.beeldkader` houdt de
  verhouding vast, en een kader waar het beeld nog niet in zit staat er zichtbaar leeg bij in
  plaats van als witruimte mee te lezen.
- **Er is geen paginabibliotheek.** `stijl.css` geeft het kader, het raster, de maatladder, de
  kleurregels en twintig merktekens die elk één ding tekenen. De compositie is elke pagina
  opnieuw een beslissing.

Alle maten en kleuren komen uit twee gemeten drukwerken: het jaarrapport 2025 en de casespread
Civitates. Wat er in `reference/folders-stramien.md` staat met "gemeten" ernaast, komt daaruit.

```bash
python scripts/folders/preflight.py
python scripts/folders/bouw.py <werkmap> --uit uitnodiging.html --titel "Uitnodiging"
python scripts/folders/render.py <werkmap>/uitnodiging.html
python scripts/folders/qa_folder.py <werkmap>/uitnodiging.html
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
