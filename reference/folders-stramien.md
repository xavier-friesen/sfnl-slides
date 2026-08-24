# Het stramien — de feiten van een SFNL-folder

Alles wat je moet opzoeken en niets wat je moet overwegen. De maatstaf staat in
`folders-vormentaal.md`.

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
`@page`-regel alle drie bijgewerkt moeten worden, en dat de folder daarna nergens anders meer
past.

**Een drieluik vouwt in een vaste volgorde en daar gaat het meestal mis.** Op de buitenkant is de
voorkant het **rechter** paneel; de volgorde is binnenflap, achterkant, voorkant. De binnenkant
leest als één spread van drie panelen. Schrijf de inhoud in de volgorde waarin de lezer hem
openvouwt: de voorkant doet één belofte, de binnenkant lost hem in drie beten in, de achterkant
draagt de logistiek.

**Bij drukwerk is het aantal pagina's deelbaar door vier.** Zo wordt een katern gevouwen. Dat is
de enige plek in deze skill waar de drukker meebeslist.

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
maatprobleem — `qa_folder.py` telt ze en meldt het boven de zes.

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
naar 11 of 12 pt, want daar is de maat anders. De vloer die `qa_folder.py` handhaaft is 8 pt voor
lopende tekst en 6 pt voor een gespatieerd kapitaallabel — dat laatste omdat de casespread zijn
kleinste labels op 6,8 pt zet en die leesbaar zijn.

**Twee letterfamilies, en niet meer.** Montserrat voor kop, titel, display en label; Lato voor
alles wat gelezen wordt. Gotham Bold is de echte merkletter maar is gelicentieerd en gaat deze
repo nooit in; Montserrat ExtraBold is de substituut, en dat is niet gekozen maar overgenomen —
het SFNL-drukwerk zelf zet zijn display-regels al in Montserrat ExtraBold.

De letters zitten **ingesloten** als `@font-face` met een data-URI, uit
`assets/folders/fonts/fonts.css`. Dat is 197 kB per artboard en die prijs is bewust: een folder
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
precies goed; op een inhoudspagina is het bijna altijd fout. `qa_folder.py` meet het als `gat`.

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

`$S` is `${CLAUDE_PLUGIN_ROOT}/scripts/folders`.

| script | wat |
|---|---|
| `preflight.py` | is er een browser, node, de design-helper en `stijl.css` |
| `bouw.py <werkmap>` | stempelt de stijl in elk artboard, schrijft `canvas.json` als spreads en het losse HTML-bestand |
| `bouw.py <werkmap> --nieuw Naam` | een leeg artboard met het skelet erin |
| `render.py <html>` | losse pagina's plus het contactblad met de spreads |
| `qa_folder.py <html>` | de negen metingen |
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
maar één naamloze `@page`-regel**, dus een folder met twee bladmaten drukt op de maat van pagina
één. `bouw.py` zet er een waarschuwing bij in de CSS; wil je beide maten echt, exporteer dan per
maat een apart bestand.
