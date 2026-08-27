# Samenstellen — de skills aan elkaar schakelen

Acht skills, één plugin, en dat is geen administratieve keuze. Vier ervan componeren: `slides`
bouwt een deck, `ontwerp-documenten` kort drukwerk in HTML, `rapport-deliverable` een gezet
rapport, en `infographic` het losse beeld dat in alle drie kan komen te staan. Twee leveren een
ander formaat: `sfnl-word` een werkdocument, `online-design` een scherm. En twee doen iets met
wat er al ligt: `ontwerp-met-affinity` voert in Affinity uit wat de stramienen bepalen, en
`deck-check` schoont een bestaand deck op.

Ze delen hun merklaag, hun letters, hun canvasroute, hun PDF-stap en een deel van hun scripts, en
de meeste echte opdrachten raken er meer dan één. **De merkfeiten staan één keer**, in
`reference/merk.md` en `scripts/gedeeld/merk.py`: de kleurwaarde staat één keer, de kleurregel per
medium. Wat per medium verschilt — de maatladder, het raster, de kleurregisters, de vulgraad —
staat in de vormentaal van dát medium en hoort daar te verschillen.

Dit document beschrijft **wat er gedeeld is** en **welke ketens er zijn**. Het is bedoeld om
gelezen te worden op het moment dat een opdracht over de grens van één skill heen gaat — niet
vooraf, en niet als vervanging van de SKILL van de route waar je in zit.

---

## 1. Wat er gedeeld is, en waar het staat

| wat | waar | wie gebruikt het |
|---|---|---|
| de huisstijlletters als woff2 | `assets/documenten/fonts/` | `ontwerp-documenten` en `rapport-deliverable` sluiten ze in met `fonts.css`; `infographic` leest dezelfde bestanden als metriekbron en zet ze in zijn render |
| de fontbestanden voor de deckmeting | `assets/fonts/` | `slides` (`_deck.py`, `find_font_file`) en `infographic` (`svg.py`, `vind_font`) — een volledige statische snede hier gaat vóór het ingesloten subset |
| het voorblad | `.omslag` in `assets/documenten/stijl.css` §8.16 | `ontwerp-documenten` en `rapport-deliverable`, met één maatladder |
| de canvasroute | `scripts/gedeeld/canvas.py` | de vier compositieroutes. `leg_neer()` legt pagina's in spreads neer, `zoek_helper()` vindt `seed-canvas.mjs` van de design-skill |
| de drukwerkrekensom | `scripts/gedeeld/drukwerk.py` | de twee drukroutes: een veelvoud van vier pagina's |
| HTML naar PDF | `scripts/gedeeld/naar_pdf.py` | de twee drukroutes |
| het SFNL-sjabloon | `assets/sfnl-sjabloon.potx` | `slides`, en `infographic` in zijn PowerPoint-route |
| de OOXML-primitieven | `scripts/shapes.py`, `scripts/office/` | `slides`, en `infographic` in zijn PowerPoint-route |

**Eén zoekactie hoort maar één keer te bestaan.** `zoek_helper()` is daar het voorbeeld van, en
het is er een met een geschiedenis: er stonden twee versies van, in de documentenskill en in de
infographicskill, en ze waren niet gelijk. De ene sorteerde alfabetisch en koos daarmee soms een
oudere skillversie, dus dan seedde het canvas op een verouderde editor — zichtbaar pas als
iemand erin klikte. Wat gedeeld hoort, staat in `scripts/gedeeld/`.

---

## 2. Een infographic in een document of rapport

Dit is de keten die het vaakst nodig is en die het makkelijkst stil misgaat.

**Het defect.** Een SVG schaalt álles mee, ook zijn letters. Een beeld dat op `CANVAS["breed"]`
is getekend — 960 × 320 pt — en dat in het beeldkader van een document van 680 px komt te staan,
krimpt met factor 0,53: zijn voetnoot van 10 pt komt op 5,31 pt uit, onder de leesvloer van 8,
en er staat niets fout in de markup. Dat is nagemeten op `m1-geldstroom.svg`, en dezelfde
meting staat als regel in `documenten-vormentaal.md` §11 punt 1.

**De reparatie is het canvas en niet het kader.** Zes canvassen staan er klaar in
`scripts/infographic/svg.py`, met de breedte van het doelkader:

| `CANVAS`-sleutel | px | het kader |
|---|---|---|
| `doc-breed` | 680 × 372 | de volle zetspiegel van een SFNL-document |
| `doc-kolom2` | 325 × 244 | één van twee kolommen |
| `doc-kolom3` | 207 × 207 | één van drie kolommen |
| `rap-breed` | 650 × 366 | de volle zetspiegel van een gezet rapport |
| `rap-kolom` | 537 × 302 | de tekstkolom in het layoutmodel `breed` |
| `rap-dubbel` | 310 × 233 | een kolom in het model `dubbel` |

De hoogte mag groeien, de breedte niet. Meer inhoud nodig: rek de `viewBox` in de hoogte en
houd de breedte gelijk — de infographic van `documenten-vormentaal.md` §11 ging zo van 268 naar
372 px en hield zijn letters.

**Deze zes staan in px en niet in punten, en dat is de kern van deze keten.** De rest van
`svg.py` rekent in punten — één SVG-eenheid is één pt, zoals in PowerPoint — maar het
meetapparaat van de containers leest de **opgegeven** maat en niet de gerenderde. De
`te-klein`-regel van `qa_document.py` neemt `getComputedStyle(el).fontSize`, en dat getal staat
in het lokale coördinatenstelsel van de SVG; een `viewBox` die de inhoud opschaalt, ziet die
regel niet. Nagemeten op een gebouwde documentpagina: een exhibit van 510 pt breed in een kader
van 680 px rendert zijn 10-punts brood keurig op 13,33 px, en `qa_document.py` meldde er elf
`critical` over — acht keer `te-klein`, en geen ervan was een echt defect. Hetzelfde beeld op
`doc-breed` gebouwd komt schoon door: geen bevindingen. Dat is ook wat
`documenten-stramien.md` §5b altijd al voorschreef ("`viewBox` even breed als het kader in px").

`Maten.voor("document")` en `Maten.voor("rapport")` zetten daarom de eenheid mee, en `schrijf()`
weigert een canvas en maten die niet in dezelfde eenheid staan. De drie drempels van `svg.py`
die in punten staan — het dragerwindow van 28 tot 40, de kopvloer van 18 en de displayvloer van
40 — rekenen mee met de eenheid, want anders zou een lichte hue op een px-canvas ineens tekst
van 13,5 pt mogen dragen waar de regel 18 pt eist.

**En de maatladder komt ook van de container.** `Maten.voor("document")` zet brood 13,33, kop 16
en noot 10,67 px; dat is 10, 12 en 8 pt. Een beeld dat zijn eigen 16 pt meeneemt, zet een
zevende maat op een pagina die er zes heeft, en `qa_document.py` meldt dat — ook dat is
nagemeten (§11 punt 2). De drager blijft standaard weg: zijn window begint op 28 pt en dat is
luider dan de titelmaat van de pagina zelf (20 pt), dus in een exhibit is hij het luidste
element na de dektitel. Dat kan, als het gekozen is.

**De poort is `insluiten.py`.** Die leest de `viewBox` en alle `font-size`-waarden, rekent de
factor uit en weigert als de kleinste tekst door de vloer zakt — 7,8 pt in een document, 6 pt in
een rapport, 12 pt op een slide. Die 7,8 is exact de 10,4 px die `qa_document.py` zelf
handhaaft, want twee bijna-gelijke vloeren zijn erger dan één: dan keurt het ene script goed wat
het andere afkeurt.

Hij normaliseert ook de lettersnedes, en dat is de tweede meting van deze keten. `svg.py`
schrijft `font-family="Lato Light, Lato, sans-serif"` — snede vooraan, familie als terugval —
en `qa_document.py` telt de **eerste** naam als familie. Zo staan er drie families op de pagina
waar de regel er twee toestaat. `insluiten.py` haalt de snede uit de naam; het gewicht draagt
hem al en `fonts.css` declareert `'Lato'` op 300, dus de letter blijft exact dezelfde.

### Twee dingen die je op de render van het beeld zelf niet ziet

Deze twee zijn de reden dat `insluiten.py` een poort is en geen rapportje. Ze zijn allebei
onzichtbaar zolang je naar de infographic kijkt, en allebei zichtbaar zodra hij op de pagina
staat — en dan is het te laat om er nog een ontwerpbesluit van te maken.

**1. De omlijsting die de container al draagt.** Een los beeld heeft een aanhef nodig, een
bronregel, soms een drager: er is niets anders dat ze draagt. Een exhibit staat onder een kop,
boven een bijschrift, naast een chapeau. Alles wat het beeld daarvan herhaalt is een tweede stem.

| wat | in een los beeld | in een exhibit |
|---|---|---|
| de aanhef boven de figuur | vaak, als kapitaallabel | de pagina, in zijn kop |
| de bronregel | ja, zodra er cijfers op staan | het bijschrift onder het kader |
| de drager op displaymaat | als de figuur de bewering niet zelf draagt | bijna nooit |
| de sluitregel | als de figuur het half zegt | de alinea onder het kader |
| **de labels bij de elementen** | **ja** | **ja — hier verandert niets** |

Die laatste rij is de belangrijkste. Direct labelen is vormentaal §9 en het staat boven deze
afweging: een figuur die zijn eigen staven niet meer benoemt, is geen figuur meer. Dat de
chapeau "begeleiding op de werkvloer" noemt en het staaflabel ook, is de pagina die beschrijft
wat de figuur laat zien.

`insluiten.py` leidt de rol af uit de attributen en niet uit de naam — kapitalen met
letterspatiëring zijn een aanhef, dekking 0,70 is een bronregel, een maat in het dragerwindow is
een drager — en blokkeert alleen op die drie. Geef hem `--pagina` en `--bijschrift`; zonder die
twee kan hij niets vergelijken en zegt hij dat. Nagemeten op de proefpagina: de eerste versie had
een aanhef die de kop herhaalde en een bronregel die het bijschrift herhaalde, en het staaflabel
werd terecht niet gevlagd.

**2. Het dode wit onder de compositie.** Op een los beeld zie je een leeg onderstuk op de render
en verklein je het canvas. In een `.beeldkader` zie je het niet: de verhouding van het kader komt
uit de `viewBox`, dus een canvas dat voor 70 procent gevuld is reserveert 30 procent wit op de
pagina — wit dat er staat omdat `doc-breed` nu eenmaal 372 px hoog is, en dat de tekst eronder
wegduwt.

`pas_hoogte(c, vormen)` zet de hoogte op de compositie plus één marge, ná het componeren. De
breedte blijft staan, want die is van de container; alleen de hoogte beweegt, precies zoals
`documenten-vormentaal.md` §11 punt 1 voorschrijft. `schrijf()` waarschuwt tijdens het bouwen en
`insluiten.py` blokkeert bij de poort, en ze gebruiken dezelfde functie — `wit_onder()` in
`svg.py` — zodat een waarschuwing die je in de bouw negeert bij de poort terugkomt.

Nagemeten: het canvas van de proef ging van 372 naar 179 px, en die 111 px stonden als niets
midden in een zetspiegel. Verwacht daarna één ding dat op een terugslag lijkt en het niet is:
`qa_document.py` kan over de pagina gaan klagen ("de inhoud houdt op 57 procent van de zetspiegel
op"). Het wit is van onzichtbaar in het beeld naar zichtbaar op de pagina verplaatst, en daar is
het een paginabesluit — meer inhoud of een kortere pagina — in plaats van een gat waar niemand
naar kijkt.

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/infographic/insluiten.py exhibit.svg \
    --doel document --kader breed --uit fragment.html
python ${CLAUDE_PLUGIN_ROOT}/scripts/infographic/insluiten.py exhibit.svg \
    --doel rapport --kader kolom --na b0042 --bijschrift "..."
```

**Wat er uit komt, verschilt per bestemming**, en dat komt doordat de containers beeld anders
plaatsen. Dat is geen inconsistentie om weg te poetsen, het is hoe die routes werken:

* **document** — een `.beeldkader` met de SVG **inline**, met de verhouding inline op het kader.
  De artboards van `ontwerp-documenten` zijn met de hand gecomponeerde HTML, dus dat kan, en
  het is beter: tekst blijft tekst en de PDF houdt hem selecteerbaar.
  `assets/documenten/voorbeeld/Geldstroom.dc.html` doet het zo.
* **rapport** — een **PNG op 2×** plus de regel voor de `figuren`-JSON. `bouw.py` plaatst beeld
  als `<img src>` uit die JSON en niet als inline SVG. Factor 2 is bedoeld — een bitmap gaat op
  het dubbele mee om op 192 dpi te drukken — en blijft onder de krimpgrens van 2,5 waar de
  zetmotor een beeld naar de volle zetspiegel promoveert (`rapport-stramien.md` §7c). Geef
  `--na <blok-id>` mee; `lees_docx.py` geeft die id's.
* **slide** — een PNG op 2× om te plakken. Wil je een slide die in PowerPoint bewerkbaar blijft,
  dan is dat stap 4B van `infographic` en niet dit script.

**Het bijschrift is van de container.** In een document staat de herkomst in de `figcaption`
onder het kader, in een rapport in `.exhibit__titel` en `.exhibit__bron`. Zet er dus geen tweede
bronregel in de SVG bij.

---

## 3. Een deck of document dat een figuur nodig heeft

De andere kant op, en alle drie de containers zeggen zelf wanneer:

| route | de grens | staat in |
|---|---|---|
| `slides` | boven twaalf onderdelen op een slide is het een tekening | `vormentaal.md`, bovengrens onderdelen |
| `ontwerp-documenten` | een beeld dat rekent — een verhouding, een volgorde, een afstand | `documenten-vormentaal.md` §11 |
| `rapport-deliverable` | een figuur die uitgerekend moet worden | `rapport-vormentaal.md`, "Geen infographics ontwerpen" |

Je begint dan bij stap 1 van `infographic`, met één verschil dat de hele intake korter
maakt: **de bewering ligt al vast.** Die staat in de titel van de slide of in de kop van de
pagina. De eerste vraag van de intake is dus al beantwoord, en er komt geen tweede bewering op
het beeld — geen drager en geen sluitregel, tenzij de figuur zonder die regel niets zegt. Dat is
vormentaal §1 van de infographicskill, en in deze richting is het bijna altijd het antwoord.

Wat je wél uitvraagt bij de container: welk kader (kolom of zetspiegel), en of de container het
bijschrift en de bron draagt.

---

## 4. Een rapport dat uit een deck komt, of omgekeerd

Deze keten bestaat, maar hij is **niet geautomatiseerd** en dat is een keuze. Een deck en een
rapport hebben een andere structuur: een slide draagt één bewering en een rapportpagina draagt
een betoog. Een deck omzetten in een rapport is dus opnieuw schrijven en niet opnieuw opmaken,
en dat is werk voor `sfnl-rapporttekst` of `sfnl-writer` en niet voor deze plugin.

Wat wél overgaat zonder herschrijven: de exhibits. Een infographic die als SVG in het deck
stond, gaat via §2 hierboven het rapport in — op het canvas van het rapport, met de maten van
het rapport. Een native PowerPoint-grafiek gaat níet over; die exporteer je als beeld of je
bouwt hem opnieuw.

---

## 5. Wat níet gedeeld is, en waarom

**De primitievenlagen.** `scripts/infographic/svg.py` tekent in SVG-punten,
`scripts/shapes.py` in OOXML-inches, en de HTML-routes componeren met CSS-klassen. Die drie
samenvoegen is geprobeerd op de kleinste plek waar het kon — het eindbeeld van een infographic
als `.dc.html`-artboard bouwen in plaats van als SVG — en het antwoord was nee: de twee renders
waren niet van elkaar te onderscheiden, en wat de canvasversie inleverde was de contrasttoets,
de echte fontmetriek en een bestand dat in Affinity opengaat. Dat staat als blokkade 13 in
`skills/infographic/SKILL.md`.

**De schrijfwijze van de vullingen.** In `svg.py` is het `vulling=container("emerald")` en
`lijn_=`; in `shapes.py` `vulling="container:emerald"` en `lijn=`. Twee lagen, twee conventies.
Gelijktrekken zou één van de twee bestanden moeten herschrijven voor een winst die alleen bij
het wisselen van route merkbaar is.

**En de eenheid van de dekking.** `svg.py` rekent met een breuk (`("navy", 0.07)`), `shapes.py`
met de OOXML-honderdduizendste (`("navy", 7000)`). Dat verschil is niet gelijk te trekken zonder
de OOXML-eenheid te verlaten, en het is de gevaarlijkste van de twee: de verkeerde eenheid gaf
geen fout maar een onzichtbare vorm, want `int(0.16)` is 0 en alpha nul is doorzichtig.
Nagemeten op de keten van layout 19 — drie van de vier staven stonden er niet en de XML
valideerde schoon. `shapes.py` weigert sinds die meting een alpha tussen 0 en 1000 en zegt in de
foutmelding welke van de twee lagen je vermoedelijk voor je had. Zo blijft de eenheid verschillen
en wordt het verschil hoorbaar in plaats van zichtbaar-pas-op-de-render.

**De renderloop.** Elke route kijkt naar zijn eigen render met zijn eigen script, want ze
beoordelen niet hetzelfde: een slide op afstand, een pagina op leesafstand, een infographic
zonder de omgeving eromheen. Wat ze wél delen is de Chromium-zoeker in
`scripts/documenten/_browser.py`, en die staat er omdat Playwright anders faalt op een machine
waar de browser vooraf is neergezet.
