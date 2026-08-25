# Het stramien — de feiten van een SFNL-document

Alles wat je moet opzoeken en niets wat je moet overwegen. De maatstaf staat in
`documenten-vormentaal.md`.

Alle maten in px bij 96 dpi, want dat is de eenheid waarin een design-artboard meet en waarin
`stijl.css` rekent. Eén mm is 3,7795 px. Waar hieronder "gemeten" staat, komt het getal uit het
SFNL-jaarrapport 2025 (210 × 275 mm) of uit de casespread Civitates (420 × 275 mm), en niet uit
een voorkeur.

---

## 1. De bladmaten

| `data-formaat` | mm | px | waarvoor |
|---|---|---|---|
| `sfnl` | 210 × 275 | **794 × 1039** | de default. Het formaat van de jaarrapporten |
| `sfnl-spread` | 420 × 275 | 1587 × 1039 | de dubbelpagina, voor één case of één verhaal |
| `a4` | 210 × 297 | 794 × 1123 | kantoorprinter, bijlage bij een aanbesteding |
| `a4-liggend` | 297 × 210 | 1123 × 794 | een schema dat breed moet |
| `a5` | 148 × 210 | 559 × 794 | uitnodiging, programmaboekje |
| `dl` | 99 × 210 | 374 × 794 | één paneel van een drieluik |

**Er is geen zevende formaat.** Een eigen maat betekent dat `stijl.css`, `bouw.py` en de
`@page`-regel alle drie bijgewerkt moeten worden, en dat het document daarna nergens anders meer
past.

**Een drieluik vouwt in een vaste volgorde en daar gaat het meestal mis.** Op de buitenkant is de
voorkant het **rechter** paneel; de volgorde is binnenflap, achterkant, voorkant. De binnenkant
leest als één spread van drie panelen.

Wat dat je oplevert is een **leesvolgorde**, en die is anders dan de paneelvolgorde: de lezer
ziet eerst de voorkant, vouwt dan open en ziet drie panelen tegelijk, en komt pas daarna bij de
achterkant. Verdeel het materiaal dat je hébt over die volgorde — het eerste paneel draagt wat de
lezer als eerste moet weten, de binnenkant is één samenhangend vlak van drie kolommen, en de
achterkant is de plek die apart staat. Wat er op elk paneel komt, volgt uit de opdracht en niet
uit deze tabel.

**Hoe het gevouwen wordt, bepaalt welke aantallen bestaan.** Dat is de enige plek in deze skill
waar de drukker meebeslist.

| omvang | hoe het op papier komt |
|---|---|
| 1 pagina | één plat vel, enkelzijdig |
| 2 pagina's | één plat vel, dubbelzijdig |
| 3 pagina's | bestaat niet op papier — dat is een vel van vier met een blanco achterkant. Als PDF is drie gewoon drie |
| 4, 8, 12, 16 | een gevouwen katern, en dáárom is het aantal vanaf vier deelbaar door vier |

Komt de gebruiker met vijf of zes pagina's en gaat het naar de drukker, zeg dan wat dat betekent
(acht bladen met lege pagina's erin) en leg de keuze voor: inkorten naar vier, uitbreiden naar
acht, of het bij een PDF houden. Stilzwijgend afronden is het defect.

**De som staat in een script en niet in je hoofd.** `bouw.py <werkmap> --gedrukt` rekent hem uit
met `scripts/gedeeld/drukwerk.py` — daar staat hij omdat de rapportroute dezelfde vraag stelt —
en zet het antwoord onder `katern` in het verslag: klopt het aantal, hoeveel er bij moeten, hoeveel
eraf, en één zin die je kunt doorgeven. Het script rekent en meldt. Het maakt geen pagina bij en
het gooit er geen weg, want welke van de drie uitwegen de goede is, hangt af van wat het document
is en dat weet alleen de gebruiker. De vlag staat default uit: blijft het een PDF, dan is het
aantal vrij. Deze route kent geen `ontwerp.json`, dus het besluit `gedrukt` staat bij de
vormbesluiten bovenaan `outline.md` en de vlag draagt het naar het script.

---

## 1a. Wat er nog niet in zit als het naar de drukker gaat

Twee dingen ontbreken in de PDF die deze route oplevert, en een drukker vraagt naar allebei. Dit
is de plek waar die uitleg staat; de skills vatten hem samen en wijzen hierheen, want twee
volledige kopieën lopen na de eerste correctie uit elkaar.

**Er zit geen afloop van 3 mm in en er staan geen snijtekens.** De snijrand is `overflow: hidden`
op `.pagina` en er is geen gebied buiten het blad: wat over de rand steekt is weg, en dat is
precies wat `qa_document.py` als `overloop` meldt. Een echte afloop maakt het blad 6 mm breder en
hoger en raakt daarmee de formatentabel hierboven, dezelfde tabel in `stijl.css` en de
`@page`-regel die `bouw.py` schrijft. Dat is een aparte ingreep en geen vlag die je even omzet.
Wat aflopend werk hier wél doet, is de rand ráken — `.aflopend` en zijn varianten lopen tot aan de
snijlijn en niet erover.

**Montserrat komt in de PDF als Type3 terecht.** Google serveert alleen nog een variabel bestand
dat alle gewichten draagt, `haal_fonts.py` sluit datzelfde bestand in, en Chromium neemt het zo
mee. De PDF drukt en de tekst is te selecteren, maar een drukkerij die om een lettertype vraagt,
krijgt geen normale naam te zien. Lato komt wél gewoon als Lato-Light mee.

De bladmaat zelf klopt en is nagemeten op een gebouwd document van vier pagina's: 595 × 780 pt,
wat exact 210 × 275 mm is en dus gelijk aan het echte jaarrapport. Wat ontbreekt is de rand
eromheen, niet de maat.

Zeg deze twee bij de oplevering zodra de gebruiker het woord drukker laat vallen, samen met de
katernsom hierboven. Alle drie horen bij dezelfde vraag: bestaat dit stuk op een pers.

---

## 2. Het kader

| | px | mm | herkomst |
|---|---|---|---|
| marge rondom | 57 | 15 | gemeten: de tekstkolom begint op 42,5 pt van de snijrand |
| marge onder | 64 | 17 | ruimer, want de folio staat eronder |
| zetspiegel op `sfnl` | 680 × 918 | 180 × 243 | wat er overblijft |
| goot tussen kolommen | 30 | 8 | gemeten: 23,5 pt |
| twee kolommen | 325 elk | 86 | ± 52 tekens per regel |
| drie kolommen | 207 elk | 55 | ± 32 tekens, uitgevuld met afbreking |

`a5` en `dl` hebben een eigen, kleinere marge; die staat in `stijl.css` op het formaat zelf.

**Vier kolommen bestaat niet op het rapportformaat.** De maat wordt dan 24 tekens en dat leest
niet meer, ook niet uitgevuld.

De pagina bestaat uit twee lagen en dat onderscheid is de belangrijkste regel van dit document:

- **`.pagina`** is het blad. Vast van maat, `overflow: hidden` als snijrand, en het draagt
  **geen marge**.
- **`.zetspiegel`** is het tekstgebied en draagt de marge als padding. Alles wat gelezen wordt
  staat hierin.
- **Aflopend werk staat ernaast**, als broer van de zetspiegel.

Waarom het blad geen marge draagt: een absoluut geplaatst element rekent tegen de padding box van
zijn containing block. Stond de marge op `.pagina`, dan zou `.aflopend { inset: 0 }` keurig
binnen de marge blijven staan, en dat is precies wat aflopend werk niet is.

---

## 3. De maatladder

Vier rollen plus twee. Wie een vijfde maat nodig heeft, heeft een compositieprobleem en geen
maatprobleem — `qa_document.py` telt ze en meldt het boven de zes.

| rol | klasse | px | pt | letter |
|---|---|---|---|---|
| brood | `.tekst`, `.chapeau` | 13,33 / 17,33 | 10 / 13 | Lato Light 300 |
| klein | `.klein`, `.label`, `.bron` | 10,67 / 14 | 8 | Lato Light / Montserrat 400 |
| kop | `.kop` | 16 | 12 | Montserrat Bold 700, kapitalen |
| titel | `.titel` | 26,67 | 20 | Montserrat ExtraBold 800 |
| uitspraak | `.uitspraak` | 22 | 16,5 | Montserrat ExtraBold 800 |
| display | `.display` | 56 en hoger | 42+ | Montserrat ExtraBold 800 |

**De body staat op 10 pt en dat is lager dan de generieke drukvloer van 12 pt.** Dat is een
gemeten afwijking en geen slordigheid: het rapport zet zijn brood op 10/13 in kolommen van 55 tot
86 mm, en dat geeft 32 tot 52 tekens per regel. Op een A5-uitnodiging met één brede kolom ga je
naar 11 of 12 pt, want daar is de maat anders. De vloer die `qa_document.py` handhaaft is 8 pt voor
lopende tekst en 6 pt voor een gespatieerd kapitaallabel — dat laatste omdat de casespread zijn
kleinste labels op 6,8 pt zet en die leesbaar zijn.

**Twee letterfamilies, en niet meer.** Montserrat voor kop, titel, display en label; Lato voor
alles wat gelezen wordt. Gotham Bold is de echte merkletter maar is gelicentieerd en gaat deze
repo nooit in; Montserrat ExtraBold is de substituut, en dat is niet gekozen maar overgenomen —
het SFNL-drukwerk zelf zet zijn display-regels al in Montserrat ExtraBold.

De letters zitten **ingesloten** als `@font-face` met een data-URI, uit
`assets/documenten/fonts/fonts.css`. Dat is 197 kB per artboard en die prijs is bewust: een document
die zijn letters van Google Fonts haalt, valt terug op Helvetica zodra er geen internet is, en de
PNG- en PDF-export van het canvas neemt een Google Font sowieso niet mee. `haal_fonts.py` maakt
het bestand opnieuw; Montserrat en Lato staan onder de SIL Open Font License 1.1 en de
licentietekst reist mee.

---

## 4. De kleuren

| naam | hex | rol |
|---|---|---|
| navy | `#201B5C` | de inkt. Lopende tekst is nooit puur zwart |
| oranje | `#F87F4F` | het accent. Labels, de streep, de badge |
| wit | `#FFFFFF` | het papier |
| grapefruit | `#F95D63` | het tweede eind van het verloop; alarm, nadruk |
| emerald | `#6AC6BA` | positief, uitkomst |
| royal | `#3B62C1` | secundaire data |
| sky | `#45B6E2` | tertiaire data |
| violet | `#6B5DAE` | gemeten uit de casespread; een heel paneel of een rail |

Tinten, gemeten uit de vlakken in het rapport en niet berekend:

| naam | hex | waar |
|---|---|---|
| mint-tint | `#E0F4F1` | een hele pagina of een paneel in emerald |
| periwinkel | `#A0ADE2` | het interviewpaneel |
| oranje-tint | `#FFDFD0` | het watermerkcijfer |
| navy-tint | `#F4F3F7` | een stille container |
| grijs | `#F2F2F2` | een kaartvulling |

**Eén verloop, en het is gemeten.** `--verloop` loopt van oranje naar grapefruit onder 150 graden;
op de omslag van het rapport 2025 meet dat `#FF7F40` naar `#FF5F55`. Wie een tweede verloop
verzint, verzint een tweede huisstijl.

**Contrast, en dit is de val die het vaakst toeslaat.** Wit haalt 2,6 op oranje en 2,8 op het
verloop. Dat draagt een kop van 40 px prima — elke SFNL-omslag doet dat — en het draagt geen
alinea van 10 pt. Navy haalt 6,4 op oranje. Daarom is op `data-veld="oranje"` en
`data-veld="verloop"` de inkt **navy**, en is wit de uitzondering die je per element zet. Wil je
een heel veld in wit, dan zet je `data-inkt="wit"` op de pagina en dan is het een keuze.

Op navy en violet is het andersom: daar is wit de inkt.

---

## 5. De merktekens

Elk tekent één ding en codeert één ding. Ze zijn geoogst uit het rapport 2025 en de casespread.
Dit is de complete lijst; er zit geen `.kaartenrij` en geen `.tijdlijn` tussen, en die komen er
niet.

| klasse | codeert | let op |
|---|---|---|
| `.kopregel` | welk hoofdstuk je leest en waar je bent | rechtsboven, cursieve naam, oranje pijp, vet nummer, met een haarlijn die naar links doorloopt. Vanaf acht pagina's |
| `.folio` | het paginanummer | buitenonder, dus `--links` op een linkerpagina en `--rechts` op een rechter |
| `.kicker` | dit is de zoveelste van een reeks | klein, oranje, boven de kop |
| `.uitspraak` | wat er van deze pagina blijft hangen | één per pagina, hooguit |
| `.watermerk` | de hoofdstukgrens, zonder een regel te kosten | half áchter de kop, niet ernaast |
| `.streep` | hier begint iets | 56 × 3 px in oranje. Het goedkoopste merkteken dat er is |
| `.haarlijn` | hier houdt iets op | 1 px op 22 procent dekking |
| `.paspoort` | een rij feiten in een zijkolom | label in kapitalen op 9 px, waarde eronder in vet |
| `.badge` | volgorde | altijd rond, nooit een afgeronde rechthoek |
| `.lesmarkering` | een los punt in een reeks aanbevelingen | cirkel plus staafje, in plaats van een opsommingsteken |
| `.paneel` | een gekleurd vlak met inhoud | `data-veld` kiest de kleur én de inkt in één keer |
| `.kaart` | een paneel dat los op wit staat | haarlijn in de eigen kleur, nooit een slagschaduw |
| `.rondfoto` | een portret | hoort half over de rand van zijn paneel heen te hangen |
| `.bol` | diepte in een vol kleurvlak | dezelfde kleur, lichter, half buiten het blad |
| `.icoon` | een soort die de lezer moet vergelijken | zelf getekend in SVG op een raster van 24. Geen bibliotheek, geen emoji |
| `.doorloop` | dit loopt door op de volgende pagina | een klein oranje driehoekje aan het eind van de laatste alinea |
| `.logo` | het merk | inline SVG, erft `currentColor` |
| `.titelbalk` | een titel op een aflopende band bovenaan — de dektitel op pagina 1, of een hoofdstuknaam | zet `--balk` op de `.pagina`, niet op de balk. `data-veld` kiest de kleur én de inkt |
| `.beeldkader` | de gereserveerde plek voor een infographic of foto | verhouding inline met `aspect-ratio`; zonder opgaaf 3:2 |
| `.beeldkader--leeg` | er hoort hier beeld en het is er nog niet | met `data-wat="…"`; `qa_document.py` telt wat je hebt laten staan |

Structuur en zetting:

| klasse | wat |
|---|---|
| `.kolommen` + `data-kolommen="2\|3"` | het kolommenraster met de goot |
| `.kolommen--gelijk` | panelen naast elkaar even hoog. Zet dit op élke rij met `.paneel` of `.kaart` |
| `.overspan` | een element over alle kolommen |
| `.stapel`, `.stapel--ruim`, `.stapel--dicht` | verticale afstand uit het raster in plaats van per element |
| `.rij` | horizontaal naast elkaar met de goot |
| `.tekst` | uitgevuld met automatische afbreking. Dit is de lopende tekst |
| `.tekst--links` | vlaggend links. Voor een kolom onder 50 mm en voor alles op een donker veld |
| `.chapeau` | de vetgezette inleidende alinea onder een kop. Eén per hoofdstuk |
| `.tabel` | lijn onder de kop, haarlijn per rij, verder niets |
| `.zetspiegel--onder\|--spreid\|--midden` | waar de inhoud verankert |
| `.beeld`, `.beeld--grijs` | een foto vult zijn doos en wordt bijgesneden, nooit vervormd |

**`--spreid` is de klasse waarmee je een gat maakt.** `justify-content: space-between` drukt twee
blokken uit elkaar en laat de lucht op één plek vallen. Op een omslag met drie blokken is dat
precies goed; op een inhoudspagina is het bijna altijd fout. `qa_document.py` meet het als `gat`.

---

## 5a. De opening, en de hoofdstukopening

Twee verschillende dingen, en ze worden op verschillende momenten besloten.

**De opening** is hoe de dektitel op het document komt. Eenmalig, pagina 1, besluit 5 in het
vragenvuur.

| opening | hoe je hem bouwt |
|---|---|
| **titelblad** | een hele pagina, gecomponeerd met `.display`, een kleurveld en het logo. Geen eigen klasse, want dat zou een paginasjabloon zijn |
| **titelbalk** | `<header class="titelbalk" data-veld="oranje">` als broer van de zetspiegel, en `--balk` op de `.pagina` |
| **gewoon titel** | `.titel` in de zetspiegel, met `.streep` eronder |

**De hoofdstukopening** is hoe een hoofdstuk begint, en die vraag bestaat pas vanaf acht
pagina's. Je beantwoordt hem in de outline (stap 2 van de SKILL). Drie manieren: een `.kicker`
plus `.titel` met een `.watermerk` half erachter, een `.titelbalk` op die pagina, of een heel
blad met alleen de hoofdstuknaam. Eén manier voor álle hoofdstukken, en één bandhoogte.

Een document kan dus met een titelblad beginnen en daarna per hoofdstuk een band dragen. Dat is
geen mengeling maar twee besluiten over twee verschillende dingen.

### De titelbalk

De band heeft **drie gebruiken** en de consistentieregel geldt binnen elk ervan apart:

1. **De dektitel op pagina 1**, als je bij besluit 5 voor de titelbalk hebt gekozen. Eén keer.
2. **Een hoofdstukopening**, vanaf acht pagina's. Dan krijgen álle hoofdstukken er een, in
   dezelfde kleur en dezelfde hoogte.
3. **Eén pagina die apart staat** — een interview, een uitspraak, het beeld waar het hele document
   om draait. Dat is geen inconsistentie maar nadruk, en het staat zo in het drukwerk: het
   rapport 2025 zet zijn interviewpaneel op precies één pagina, en de oranje band en het
   mintveld ook. `maatstaf/03` doet hetzelfde met een violette band op de pagina met de
   infographic.

Wat je niet doet is twee van de drie door elkaar op één document. Draagt hoofdstuk 2 een band en
staat er ook een band op de pagina die apart hoort te staan, dan valt de nadruk weg.

De band bleedt links, rechts en boven, en lijnt binnenin uit op de marge. De titel hangt aan de
**onderkant** van de band, want dan is de afstand tot de tekst eronder de maat die het oog leest.
Gemeten voorbeeld: de casespread Civitates zet de casenaam op 42 pt in wit op een violet paneel
over de volle bovenbreedte.

`--balk` staat op de `.pagina` en niet op de balk zelf. De balk leest hem als zijn hoogte, de
zetspiegel telt hem bij zijn bovenmarge op, en zo noem je de bandhoogte maar één keer. Vergeet je
hem, dan zakt de band terug op zijn padding — niet naar nul, want `box-sizing: border-box` — en
wordt de titel erin afgesneden. `qa_document.py` leest daarom de variabele zelf en niet de hoogte,
en meldt het als `critical`.

Bruikbare bandhoogtes op `sfnl`: 190 px voor een titel van één regel, 232 voor twee regels met
een kicker erboven, 300 als er ook een intro in de band staat.

---

## 5b. Het beeldkader

Een infographic of foto staat in een `.beeldkader`. De verhouding zet je inline, want dat is een
keuze per beeld en het is precies wat het eigenschappenpaneel van het canvas kan bewerken.

Bruikbare maten op `sfnl`, waarbij de breedte de zetspiegel of een kolom volgt:

| plek | breedte | verhoudingen die passen |
|---|---|---|
| over de volle zetspiegel | 680 px | `680 / 372` (het gemeten voorbeeld), `16 / 9`, `3 / 2` |
| één van twee kolommen | 325 px | `4 / 3`, `1 / 1` |
| één van drie kolommen | 207 px | `1 / 1`, `4 / 5` |

**Teken de SVG op schaal 1:1** — `viewBox` even breed als het kader in px. Een `<svg>` schaalt
álles mee, ook zijn `font-size`, dus een beeld dat op 680 is getekend en in een kader van 340
staat, zet zijn 13,33 px-tekst op 6,7 px. Meer hoogte nodig: laat de `viewBox` in de hoogte
groeien en houd de breedte gelijk.

Een leeg kader krijgt `beeldkader--leeg` en een `data-wat` met wat er hoort te komen. Dan staat er
een gemarkeerd vlak in plaats van wit, zie je op de render dat er iets ontbreekt, en telt
`qa_document.py` wat er nog open staat.

---

## 6. Het logo

Cirkel plus vierkant plus het woordmerk op drie regels, alles in één kleur. Het staat als inline
SVG in de pagina en erft daardoor `currentColor`: wit op een kleurveld, navy op wit. Er is geen
bestandsversie, want een los bestand zou in het canvas als base64 mee moeten en is dan niet meer
herkleurbaar.

```html
<svg class="logo" viewBox="0 0 412 104" aria-label="Social Finance NL">
  <circle cx="52" cy="52" r="52" fill="currentColor"/>
  <rect x="118" y="0" width="104" height="104" fill="currentColor"/>
  <text x="248" y="31" font-family="Montserrat, sans-serif" font-weight="700"
        font-size="30" letter-spacing="0.4" fill="currentColor">SOCIAL</text>
  <text x="248" y="67" font-family="Montserrat, sans-serif" font-weight="700"
        font-size="30" letter-spacing="0.4" fill="currentColor">FINANCE</text>
  <text x="248" y="103" font-family="Montserrat, sans-serif" font-weight="700"
        font-size="30" letter-spacing="0.4" fill="currentColor">NL</text>
</svg>
```

`.logo` staat op 40 px hoog, `.logo--groot` op 62 en `.logo--klein` op 27. De `viewBox` is 412
breed en niet 384: op 384 valt de laatste letter van FINANCE eraf, en dat gebeurde op de eerste
gebouwde omslag zonder dat de markup er verkeerd uitzag.

---

## 7. De scripts

`$S` is `${CLAUDE_PLUGIN_ROOT}/scripts/documenten`.

| script | wat |
|---|---|
| `preflight.py` | is er een browser, node, de design-helper en `stijl.css` |
| `bouw.py <werkmap>` | stempelt de stijl in elk artboard, schrijft `canvas.json` als spreads en het losse HTML-bestand |
| `bouw.py <werkmap> --gedrukt` | hetzelfde, plus de katernsom uit `scripts/gedeeld/drukwerk.py` onder `katern` in het verslag. Zie §1 |
| `bouw.py <werkmap> --nieuw Naam` | een leeg artboard met het skelet erin |
| `render.py <html>` | losse pagina's plus het contactblad met de spreads |
| `qa_document.py <html>` | de negen metingen |
| `haal_fonts.py` | de letters opnieuw insluiten. Onderhoud |
| `keuzekaart.py` | de keuzekaart voor het vragenvuur opnieuw renderen. Onderhoud |

Wat `bouw.py` uit een pagina leest, van het `.pagina`-element:

| attribuut | betekenis |
|---|---|
| `data-volgnr` | de volgorde. Ontbreekt hij, dan telt de bestandsnaam en het script zegt het |
| `data-formaat` | de bladmaat, uit de tabel in §1 |
| `data-veld` | het kleurveld: `wit`, `oranje`, `verloop`, `navy`, `mint`, `violet`, `navy-tint` |
| `data-inkt` | `wit` of `navy`, als je de default van het veld wilt omdraaien |
| `data-kopregel` | de hoofdstuknaam; komt in de titel van het artboard op het canvas |
| `data-folio` | het paginanummer, of `nee` |

Het losse HTML-bestand krijgt één `@page`-regel, op de maat van de eerste pagina. **Chromium leest
maar één naamloze `@page`-regel**, dus een document met twee bladmaten drukt op de maat van pagina
één. `bouw.py` zet er een waarschuwing bij in de CSS; wil je beide maten echt, exporteer dan per
maat een apart bestand.
