# sfnl-slides

Een SFNL-deck bouwen uit het officiële sjabloon, waarbij de compositie per slide een
ontwerpbeslissing is en geen invuloefening.

## Waarom deze plugin naast `sfnl-powerpoint` bestaat

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
