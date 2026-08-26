# Het rapportstramien — de feiten

Alles wat je moet opzoeken en niets wat je moet overwegen. De maatstaf
staat in `rapport-vormentaal.md`.

Dit document beschrijft de laag die `assets/rapport/rapport.css` bovenop
`assets/documenten/stijl.css` legt. Alles uit dat eerste bestand geldt
hier onverkort: de kleuren, de letters, `.pagina`, `.zetspiegel`, de
merktekens. Wat hieronder staat komt er bij.

Alle maten in px bij 96 dpi. **Waar "gemeten" staat, komt het getal uit
een gezet rapport** — de meting staat in de git-historie van deze skill
en is met `scripts/rapport/qa_rapport.py --alles` te herhalen.

---

## 1. Het kader

Anders dan bij `sfnl-design-documents`, en dat is een besluit: een
document van vier pagina's ligt plat, een rapport van tachtig zit in een
rug.

| | px | mm | waarom |
|---|---|---|---|
| marge boven | 76 | 20 | de kopregel staat erin, op 42 px van de snijrand |
| marge binnen (rug) | 82 | 22 | ruimer dan buiten, want de rug eet marge |
| marge buiten | 62 | 16 | de folio staat erin |
| marge onder | **uitgerekend** | | `hoogte − marge-boven − zethoogte` |
| zetspiegelbreedte | 650 | 172 | `794 − 82 − 62` |

De marges **spiegelen per zijde**. Op een `data-zijde="recto"` zit de
binnenmarge links, op een `verso` rechts. Zonder `data-zijde` gedraagt de
pagina zich als recto.

**De zetspiegelhoogte is een geheel aantal regels**, en de ondermarge is
wat er overblijft. Dat is de enige manier waarop twee pagina's naast
elkaar op dezelfde hoogte eindigen.

| formaat | model | regels | zethoogte | marge onder |
|---|---|---|---|---|
| `sfnl` (794 × 1039) | `kantlijn`, `dubbel` | 50 × 17,33 | 867 (gemeten) | 96,5 |
| `sfnl` | `breed` | 39 × 22 | 858 (gemeten) | 105 |
| `a4` (794 × 1123) | `kantlijn`, `dubbel` | 55 × 17,33 | 953 | 94 |
| `a4` | `breed` | 43 × 22 | 946 | 101 |
| `a4-liggend` (1123 × 794) | alleen `dubbel` | 36 × 17,33 | 624 | 94 |

Drie formaten, en er is geen vierde. `a5` en `dl` uit de documentenskill
bestaan hier niet: onder A4 is een rapport geen rapport.

---

## 2. Het raster

Twaalf kolommen, en de goot is de gemeten 30 px (8 mm) uit het
SFNL-drukwerk.

```
--r-kolom = (650 − 11 × 30) / 12 = 26,67 px
```

Dat getal is niet gekozen maar het gevolg van de goot, en de goot is
gekozen zodat alle vier de modellen op het raster vallen. Op elke andere
gootmaat valt er één naast.

| kolommen | breedte | waarvoor |
|---|---|---|
| 3 | 140 | de kantlijn |
| 6 | 310 | één kolom in `dubbel` — precies `(650 − 30) / 2` |
| 8 | 483 | de maximale maat van een omslagondertitel |
| 9 | 480 | de tekstkolom in `kantlijn` |
| 10 | 537 | de tekstkolom in `breed` |
| 12 | 650 | de volle zetspiegel |

Als CSS-variabele: `--k3`, `--k6`, `--k8`, `--k9`, `--k10`, `--k12`.

**De pagina bestaat uit vier lagen**, en dat onderscheid is de
belangrijkste regel van dit document:

- **`.pagina`** — het blad. Vast van maat, `overflow: hidden` als
  snijrand, draagt géén marge.
- **`.zetspiegel--rapport`** — het tekstgebied, met de asymmetrische
  marge als padding. Flexkolom.
- **`.paginakop`** — volle breedte boven het raster. Hier staat de
  hoofdstukopener, zodat een hoofdstuktitel in `dubbel` over de hele
  pagina loopt en niet in de linkerkolom.
- **`.raster`** — het grid met de kaders. Geen eigen hoogte: `flex: 1`,
  en dus neemt hij wat de paginakop en de voetnoten overlaten. Zonder
  allebei komt dat exact op de zethoogte uit.
- **`.kader`** — de doos waar de stroom in valt. `overflow: hidden`, en
  dat is hier geen snijrand maar een alarm: valt er tekst uit, dan meet
  `qa_rapport.py` dat als `klip` en is de zetting stuk.
- **`.voetnoten`** — onder het raster, over de volle breedte.

---

## 3. De vier modellen

Op `data-model` van de `.pagina`. Alle getallen gemeten op een gezet
rapport van dertig tot veertig pagina's.

| model | kader | brood | regel | tekens per regel (mediaan, min–max) | uitvullen |
|---|---|---|---|---|---|
| `breed` | 537 | 14,67 px (11 pt) | 22 px | **77** (65–85) | nee |
| `kantlijn` | 480 + 140 kantlijn | 13,33 px (10 pt) | 17,33 px | **76** (63–83) | nee |
| `dubbel` | 2 × 310 | 13,33 px (10 pt) | 17,33 px | **48** (43–53) | ja |
| `flexibel` | `kantlijn` als basis | 13,33 px | 17,33 px | 76 | nee |

**De kolom in `breed` staat in het midden van de zetspiegel.** Hij is
tien van de twaalf rasterkolommen, 537 van 650 px, en dat overschot van
113 px lag tot voor kort helemaal aan één kant: 0 px wit links tegen
113,3 rechts. De kopregel en de folio hangen aan de zetspiegel en niet
aan de kolom, dus de haarlijn liep 113 px verder door dan de tekst en het
paginanummer stond er 113 px naast — op elke pagina van elk breed
rapport. Gecentreerd is het 56,7 px per kant, en de spiegeling blijft
staan: de kolom staat op een recto 138,7 px van de rug en 118,7 px van de
snijkant, en op een verso andersom. Die 20 px verschil is
`--r-marge-binnen` min `--r-marge-buiten`.

**En `.paginakop` en `.voetnoten` schuiven mee, met een eigen regel.** Ze
zijn bróérs van `.raster` in de flexkolom van de zetspiegel en geen
kinderen ervan, dus `justify-content` op het raster raakt ze niet. Zonder
die tweede regel stond het kader op 56,7 px en de hoofdstukopener en de
notenbalk op 0 — dezelfde misuitlijning, één laag hoger terug, zichtbaar
op elke opener en op elke pagina met noten.

**`flexibel` staat nooit op een pagina.** Het is een eigenschap van het
rapport; de pagina draagt `breed`, `kantlijn` of `dubbel`, en daarnaast
`data-flex="ja"` zodat de broodmaat gelijk blijft aan de basis. Zonder
dat attribuut zou een brede pagina in een flexibel rapport op 11 pt
komen te staan naast een kantlijnpagina op 10, en dat leest als twee
rapporten.

**Uitvullen hangt aan de maat.** Alleen `dubbel` vult uit, want alleen
daar is de maat kort genoeg. En uitvullen kan alleen mét afbreking:
`bouw.py` doet een proef in de browser en zet `data-afbreking="nee"` op
het lichaam als het Nederlandse woordenboek ontbreekt. Dan vervalt het
uitvullen ook in `dubbel`.

**De noodrem selecteert op `[data-afbreking="nee"] .pagina .lopend > p`**,
en die `.pagina` staat er expres in. Zonder dat woord woog de regel lichter
dan `.pagina[data-model="dubbel"] .lopend > p` erboven, en dan haalde de
noodrem het niet in precies het model dat uitvult. Op de gezette proef
was dat te zien als rivieren van wit door de kolom terwijl het
zetverslag netjes `afbreking: false` meldde — de meting klopte en de
zetting niet.

---

## 3a. De dichtheid

Op `data-dichtheid` van de `.pagina`. Drie standen, en geen drempel.

| stand | regels per pagina | lucht tussen blokken | gemeten woorden per tekstpagina |
|---|---|---|---|
| `ruim` | basis − 3 | 3 regels | **284** (79–419) |
| `gemiddeld` — default | basis | 2 regels | **295** (56–502) |
| `dicht` | basis + 3 | 1,5 regel | **318** (46–547) |

De meting komt van hetzelfde proefrapport in het kantlijnmodel; de
spreiding is groot omdat een pagina met een figuur nu eenmaal minder
woorden draagt dan een pagina zonder.

**Wat de knop níét verschuift is de afstand tussen alinea's.** Die blijft
precies één regel. Zou hij meebewegen, dan staat de tekst niet meer op
het regelraster en eindigen twee pagina's naast elkaar niet meer op
dezelfde hoogte — en dat is het enige wat de hele hoogteberekening van
§1 bij elkaar houdt. Wat wél meebeweegt is de sprong boven een sectiekop
en om een exhibit, een paneel en een citaat.

**Er is geen bovengrens en geen ondergrens**, en dat is een besluit.
Hoeveel er op een pagina mág staan hangt af van wat er staat: een
hoofdstuk met drie figuren is ruim bij dezelfde instelling waarbij een
hoofdstuk met alleen proza dicht is. Een drempel zou dat verschil
wegdrukken. In plaats daarvan meet `qa_rapport.py` achteraf hoeveel
woorden er werkelijk per tekstpagina staan, met de laagste en de hoogste
erbij, en rapporteert dat zonder oordeel.

---

## 4. De maatladder

Zeven maten, en zes ervan staan al in `stijl.css`. Wie een achtste nodig
heeft, heeft een compositieprobleem; `qa_rapport.py` telt ze en meldt het
boven de acht.

| px | pt | rol | waar |
|---|---|---|---|
| 9,33 | 7 | noot | `.voetnoot`, `.kantnoot`, `.exhibit__noot`, `.exhibit__bron` |
| 10,67 | 8 | klein | label, folio, kopregel, tabel, exhibitnummer, eenheid, bijschrift |
| 13,33 | 10 | brood | `.lopend`, `.subkop`, `.runinkop`, `.exhibit__titel`, inhoudsopgave |
| 16 | 12 | kop | `.sectiekop`, `.chapeau--rapport` |
| 22 | 16,5 | uitspraak | `.pullcitaat`, de omslagondertitel |
| 26,67 | 20 | titel | `.opener__titel` |
| 56 | 42 | display | de omslagtitel, en de hoofdstuktitel op een heel blad |
| 168 / 104 / 440 | | watermerk | `.opener__watermerk` — geen tekst, een merkteken. 168 bij `nummer`, 104 in het dubbele model, 440 op een heel blad |

In `breed` schuift het brood naar 14,67 px (11 pt) met regel 22, en
schuiven de sprongen mee. De andere maten blijven.

**Drie leesvloeren, en welke geldt hangt af van wat het element is.**
Lopende tekst 8 pt; apparaat — noten, bronregels, kopregel, bijschrift —
7 pt, en dat is de gemeten norm (MGI zet voetnoten op 7 pt, Bain op 6,2);
een gespatieerd kapitaallabel 6 pt.

---

## 5. De klassen

Wat er bovenop `stijl.css` bij komt. Elk tekent één ding.

### Structuur

| klasse | wat |
|---|---|
| `.zetspiegel--rapport` | de asymmetrische, spiegelende zetspiegel |
| `.paginakop` | volle breedte boven het raster; de hoofdstukopener |
| `.raster` | het grid met de kaders |
| `.kader` | de doos waar de stroom in valt. `.lopend` staat erop |
| `.kader--vol` | een kader over alle kolommen |
| `.kantlijn` | de zijkolom van drie rasterkolommen |
| `.voetnoten` | de bak aan de voet. De haarlijn zit op `top: 0` van die bak, dus hij heeft een marge nodig: zonder stond hij pal tegen de laatste tekstregel — gemeten kleinste afstand 10,2 px in `breed` en 0,8 px in `dubbel`, nu 42,7 en 23,7. Een lege bak krijgt de marge niet |

### Tekst

| klasse | wat | let op |
|---|---|---|
| `.lopend` | de typografie van de stroom. Staat op `.kader` | afbreken en uitvullen staan op `p` en `li`, niet op de houder |
| `.hoofdstuktitel` | niveau 1, buiten een opener | |
| `.sectiekop` | niveau 2, met een oranje streep van 56 × 3 erboven als pseudo-element | `break-after: avoid` |
| `.subkop` | niveau 3, vet, geen streep | |
| `.runinkop` | niveau 4, navy met een oranje vierkantje ervoor | was oranje; zie de contrastmeting in de vormentaal |
| `.chapeau--rapport` | de inleidende alinea onder een hoofdstuktitel | alleen als de bron er een heeft |
| `.citaatblok` | een blok dat in de bron als citaat is opgemaakt | geen aanhalingstekens erbij: dat zou tekst toevoegen |
| `.pullcitaat` | een citaat uit de tekst, groot gezet | het enige element dat tekst herhaalt, en dus nooit zonder toestemming |
| `.is-gesplitst-kop` / `--staart` | de twee helften van een gesplitst blok | zet de zetmotor |
| `.is-eerste-in-kader` | het eerste blok van een kader; bovenmarge vervalt | zet de zetmotor |

### Exhibit en beeld

| klasse | wat |
|---|---|
| `.exhibit` | het hele blok, `break-inside: avoid` |
| `.exhibit__nr` | "FIGUUR 7", gespatieerde kapitalen in het accent |
| `.exhibit__titel` | de titel, vet op broodmaat |
| `.exhibit__eenheid` | waar het beeld in meet — "mln euro, prijspeil 2025" |
| `.exhibit__beeld` | de houder; `img` en `svg` vullen de breedte |
| `.exhibit__noot` / `.exhibit__bron` | met "Noot" en "Bron" als pseudo-element ervoor |
| `.beeldblok` | een beeld zonder exhibitomlijsting, met een bijschrift |
| `.beeldblok--leeg` | er hoort beeld en het is er nog niet; zichtbaar leeg |

### Tabel

| klasse | wat |
|---|---|
| `.tabel--rapport` | lijn onder de kop, haarlijn per rij |
| `td.getal` / `th.getal` | rechts uitgelijnd met `tabular-nums`. Per kolom bepaald: een kolom is een getalkolom als tweederde van zijn cellen een getal is |
| `tr.totaal` | vet met een lijn erboven |
| `thead.is-herhaald` | de kop op een vervolgtabel, met "(vervolg)". Draagt `data-toevoeging="tabelkop"` |
| `.tabel--rapport.is-te-breed` | `table-layout: fixed`; de cellen breken af in plaats van over de rand te lopen |

### Navigatie en opener

| klasse | wat |
|---|---|
| `.rapport-kopregel` | verso: de rapporttitel; recto: de hoofdstuknaam. Eén naam per zijde, aan de buitenkant |
| `.rapport-folio` | buitenonder, met een oranje streepje van 14 × 2 ervoor |
| `.opener` | de hoofdstukopener |
| `.opener__kicker` | "HOOFDSTUK 3", gespatieerde kapitalen in het accent |
| `.opener__titel` | de hoofdstuktitel |
| `.opener__watermerk` | het hoofdstukcijfer, open getekend: vulling in de papierkleur, contour in `--r-watermerk-lijn`. Staat rechts buiten het kader, op de hoogte van de titel |
| `.scheiding__streep` | de streep op het scheidingsblad van de bijlagen, vier rasterkolommen breed |
| `.opener-band` | de aflopende band; `--balk` op de `.pagina` |
| `.inhoud`, `.inhoud__regel`, `.inhoud__nr`, `.inhoud__naam`, `.inhoud__leader`, `.inhoud__folio` | de inhoudsopgave. De puntenlijn is een lijnelement en geen reeks punten, want punten zouden als toegevoegde tekst opduiken |
| `.omslag`, `.omslag__boven/__midden/__onder`, `.omslag__titel`, `.omslag__onderschrift`, `.omslag__regel` | de omslag. Het component staat in `stijl.css` §8.16, want `sfnl-design-documents` bouwt zijn voorblad met hetzelfde merkteken; `rapport.css` §14 zet er alleen de rapportmaat op — `--m-omslag-onderschrift` op 22 px en `--omslag-maat` op acht kolommen |
| `.kantnoot` | een kanttekening in de kantlijn, met een streepje erboven |
| `.voetnoot` | een noot aan de voet, of in de kantlijn in het kantlijnmodel |
| `.paneel--rapport` | een gekleurd vlak met een blok tekst |

### Het achterwerk

De vier pagina's die niet uit het brondocument komen. Ze delen één
compositie met de hoofdstukopener — kicker, titel, tekst eronder — omdat
ze anders als een ander document lezen. Wat ze niet delen is de
nummering: het zijn geen hoofdstukken, dus geen cijfer en geen regel in
de inhoudsopgave. Zie §7d.

| klasse | wat |
|---|---|
| `.extra` | de houder, op de hele kaderhoogte zodat een colofon onderaan kan hangen |
| `.extra__kicker`, `.extra__titel`, `.extra__intro`, `.extra__lopend` | de opbouw van zo'n pagina |
| `.team`, `.lid`, `.lid__naam`, `.lid__rol`, `.lid__mail` | het team als raster van drie. Twee leest als een tegenstelling, vier maakt de naam te smal voor een dubbele achternaam |
| `.colofon` | de regels van het colofon, klein en onderaan |
| `.omslag--achter` | het achterblad: hetzelfde vlak als de omslag, met het merk onderaan |
| `.pagina[data-blanco]` | een blanco pagina die een katern afmaakt. Geen folio, geen kopregel |

---

## 6. De vier registers

Op `data-register` van de `.pagina`. Een register zet vijf variabelen;
al het andere leest die vijf.

| register | `--r-accent` | `--r-accent-2` | `--r-tint` | `--r-watermerk` | de opener |
|---|---|---|---|---|---|
| `helder` | oranje `#F87F4F` | navy | navy-tint `#F4F3F7` | oranje-tint `#FFDFD0` | wit |
| `diep` | oranje | navy | navy-tint | oranje-tint | navy blad, witte inkt |
| `zacht` | emerald `#6AC6BA` | navy | mint-tint `#E0F4F1` | `#CDEBE5` | mint blad |
| `contrast` | violet `#6B5DAE` | oranje | `#EEEBF6` | `#DCD5EE` | violet blad, witte inkt |

De vijfde is `--r-watermerk-lijn`: de contourkleur van het open
hoofdstukcijfer. `--r-watermerk` is de dichte vlek van de eerste
zetting en staat er nog voor wie hem leest; wat je op het blad ziet is
de lijn. Op een navy of violet blad zijn allebei wit met een lage
dekking, want daar is de inkt wit.

In `zacht` blijft de folio oranje, zodat het merk niet verdwijnt.

Het **omslagveld** staat hier los van: dat is `omslagveld` in
`ontwerp.json` en het gaat vóór het register. Zie
`rapport-vormentaal.md` §7.

---

## 7. De drie hoofdstukopeners

Op `data-opener`. Eén manier voor álle hoofdstukken in een rapport.

| opener | wat je krijgt | wat het kost |
|---|---|---|
| `nummer` | kicker, titel en het hoofdstukcijfer ernaast, buiten het kader, boven aan de eerste pagina van het hoofdstuk | niets |
| `band` | een aflopende band bovenaan die pagina; `--balk` bepaalt de hoogte (232 px is de default) | ongeveer een kwart pagina |
| `blad` | een heel blad met de hoofdstuknaam onderin en het cijfer op 440 px erachter | een pagina per hoofdstuk; pas vanaf veertig pagina's |

**Alle drie dragen hetzelfde merkteken**, het hoofdstukcijfer, en dat is
wat ze tot drie varianten van één ding maakt in plaats van drie losse
ontwerpen: naast de titel en buiten het kader bij `nummer`, aan de
buitenrand van de band bij `band`, groot linksonder bij `blad`.

### Het cijfer, van dichtbij

Het cijfer is opnieuw ontworpen, want de eerste versie deed precies wat
punt 12 van de weigerlijst verbiedt.

**Wat er misging.** Het cijfer stond als dichte lichte vlek half achter
de titel. De letters dekken het middenstuk af, dus wat er op de pagina
overbleef was een smalle gekleurde strook boven en onder de titel: een
rechthoek, geen cijfer. Drie varianten zijn daarna gerenderd en tegen
elkaar gezet. Groter en lager liep door de eerste alinea; hoger werd
door het kader afgesneden; naar buiten werkte.

**Wat het nu is.** Een **open cijfer** aan de buitenkant van het kader,
op dezelfde hoogte als de titel:

| | |
|---|---|
| vulling | `var(--papier)` — de papierkleur, dus het cijfer is hol |
| contour | `-webkit-text-stroke` in `--r-watermerk-lijn`, 2,5 px bij `nummer`, 2 px in `dubbel`, 5 px op een heel blad |
| plaats | `right: 0`, `top: -18px`; in `dubbel` `top: -8px`; op een heel blad `left: 0`, `bottom: 4px` |
| maat | 168 px; **104 px in het dubbele model**, want een hoofdstuk 10 op 168 px neemt de hele kolombreedte van 310 px in; **440 px op een heel blad** |

**Op een heel blad staat het cijfer wél achter de titel**, en dat is het
enige geval waarin dat werkt: de titel hangt daar onderaan en de
driekwart pagina erboven is leeg, dus er is ruimte voor een cijfer dat
groot genoeg is om cijfer te blijven. In de eerste versie stak het 58 px
onder het blad uit op 260 px, en wat er dan overbleef was de bovenkant
van een cijfer achter de titel — dezelfde rechthoek als op de
tekstpagina, alleen op een ander blad. Het staat nu helemaal op de
pagina.

De titel loopt dwars door het cijfer heen zonder er iets van af te
snijden, en het cijfer blijft leesbaar als cijfer. De contour is dun en
licht genoeg om achtergrond te blijven: het is geen tweede kop, het is
de plaats van het hoofdstuk in het geheel.

**Het spiegelt niet mee met de pagina.** Het hoort bij de titel en niet
bij de bladrand, en een cijfer dat op elke tweede pagina naar de andere
kant springt leest als een fout in de zetting. Op het scheidingsblad
van de bijlagen staat het er niet: daar is geen nummer om te tonen.

### De band, van dichtbij

Een band die alleen een kleurvlak met twee regels tekst is, leest als een
onafgemaakt ontwerp — dat was de eerste zetting. Wat er nu op staat komt
uit het gemeten drukwerk en niet uit een idee:

| onderdeel | waar | herkomst |
|---|---|---|
| het tekstblok — kicker plus titel | linksonder, hangend aan de onderkant van de band | de gemeten opbouw van de titelbalk: een groot veld met een klein blok in de onderhoek, en de leegte erboven ís de compositie. De afstand van de titel tot de tekst eronder is de maat die het oog leest |
| de tonale bol | linksboven, half buiten het blad, `currentColor` op 10 procent, 2,1 × de bandhoogte | `stijl.css` §8.12: "gemeten op de omslag en op de bronvermelding van het rapport 2025: een cirkel in dezelfde kleur, iets lichter, half buiten de pagina. Dit is wat een vol oranje vlak diepte geeft zonder een tweede kleur" |
| het hoofdstukcijfer | rechtsonder, op 0,46 × de bandhoogte, `currentColor` op 26 procent | het watermerk uit het jaarrapport, hier aan de buitenrand in plaats van achter de titel |

Twee dingen die eraan vastzitten:

- **De band spiegelt niet mee met de pagina.** De marges, de folio en de
  kopregel doen dat wel, want een gebonden rapport wordt aan de
  buitenrand doorgebladerd. De band niet: de bol staat boven het
  tekstblok en het cijfer staat aan de andere kant, en dat is een
  verhouding tussen de drie onderling. Spiegel je de bol wél, dan komen
  op een verso de bol en het cijfer allebei rechts uit en vechten ze om
  dezelfde hoek. Gemeten op de proef: precies dat gebeurde.
- **`currentColor` doet in beide richtingen het goede.** Op een oranje of
  mint band is de inkt navy, dus worden bol en cijfer een tint dónkerder;
  op een navy of violette band is de inkt wit en worden ze lichter.
  Allebei geeft het diepte, en het scheelt een uitzondering per register.

Wat er níét bij komt: een logo, een haarlijn of een tweede kleur. De band
is één vlak en het merk staat op de omslag.

De **omslag** is geen hoofdstukblad: die krijgt `data-opener="omslag"`,
en daar staat de titel in het midden in plaats van onderaan.

---

## 7a. Het verwijzingsapparaat

Twee onafhankelijke besluiten, en dat onderscheid is de kern.

**Waar de noten staan** — `noten` in `ontwerp.json`:

| stand | wat er gebeurt |
|---|---|
| `geen` | er wordt geen notenapparaat gezet. Alleen als de bron geen noten heeft; anders verdwijnt die tekst en blokkeert `tekstcheck.py` |
| `voetnoot` — default | aan de voet van de pagina waar de verwijzing staat. In het kantlijnmodel: in de kantlijn, naast de regel |
| `eindnoot-hoofdstuk` | als `.eindnoten`-blok vóór de opener van het volgende hoofdstuk |
| `eindnoot-rapport` | als één `.eindnoten`-blok aan het eind |

**Of er een bronnenlijst is** — `bronnenlijst`:

| stand | wat er gebeurt |
|---|---|
| `geen` — default | de regels onder de bronnenkop worden gewone alinea's |
| `apa` | `.bronnenlijst` met hangende inspringing van 1,7 em |
| `genummerd` | idem, op citatievolgorde, met `[n]` ervoor als `data-toevoeging="bronnummer"` |

**Ze gaan samen.** Voetnoten mét een volledige bronnenlijst achterin is
niet de uitzondering maar het gewone geval in een Nederlands
beleidsrapport, en het is wat Chicago notes-bibliography doet. Vandaar
twee besluiten en niet één lijst.

`lees_docx.py` schrijft in `document.json` een `apparaat`-blok met wat er
werkelijk in de bron zit: het aantal voet- en eindnoten, de gevonden
bronnenlijst met zijn kop en bereik, de bijlagekoppen, en hoeveel
auteur-jaar- en genummerde verwijzingen er in de lopende tekst staan. De
skill biedt alleen aan wat daar in staat.

### De citatiestijl

`citaatstijl` raakt als enige besluit de tékst, en dat is een
vaststelling van de opdrachtgever: een verwijzing gelijktrekken of
hernummeren is opmaak en geen herschrijving. Het gaat dus niet per geval
langs de gebruiker. Wat er tegenover staat is dat alles wordt vastgelegd.

| stand | wat er gebeurt |
|---|---|
| `zoals-aangeleverd` — default | niets |
| `uniform` | `e.a.` en `et. al.` worden `et al.`, en er komt een komma voor het jaartal |
| `genummerd` | `(Boogers et al., 2016)` wordt `[3]`, en de bronnenlijst gaat op citatievolgorde |

`citaten.py` rekent de omzetting uit en schrijft `citaten.json` met elke
vervanging: welk blok, wat er stond, wat er komt te staan, en naar welke
bronregel hij wijst. `bouw.py` voert ze uit met behoud van de inline
opmaak — de vervanging wordt op de samengevoegde tekst gezocht en
teruggerekend naar de runs, want een verwijzing van twintig tekens kan
over drie runs verdeeld staan. `tekstcheck.py` controleert daarna dat er
**precies** dát is veranderd: de brontekst mét de vervangingen uit het
plan moet karakter voor karakter gelijk zijn aan wat er staat. Zo kan
een omzetting geen dekmantel zijn voor een andere verandering in
dezelfde alinea.

**Wat niet meedoet:** `en` vervangen door `&`. In "Ministerie van Sociale
Zaken en Werkgelegenheid" hoort dat `en` bij de naam, en er is aan de
tekst niet te zien of een `en` twee auteurs scheidt of in een naam
staat. Op de eerste proef maakte die regel er "Sociale Zaken &
Werkgelegenheid" van.

**En wat er ook niet in zit:** omzetten naar voetnootverwijzingen. Dat
vraagt een noottekst per verwijzing, gemaakt uit de bronregel, en dan
staat dezelfde regel twee keer in het rapport. Dat is een besluit over
hoe het rapport zijn bronnen presenteert en niet langer een kwestie van
vorm. Wie dat wil, kiest `noten: voetnoot` met een bronnenlijst erbij.

**Een verwijzing die niet aan een bronregel te koppelen is, blijft staan
zoals hij stond**, en `citaten.py` meldt hem. Liever één verwijzing die
uit de toon valt dan een nummer dat nergens naar wijst.

---

## 7b. De bijlagen

`bijlagen` in `ontwerp.json` is `null` of `{"vanaf": "b0197"}`. Vanaf dat
blok verandert er vier dingen:

1. Er komt een **scheidingsblad** voor: een heel blad met een streep van
   vier rasterkolommen, één woord op displaymaat, en de tonale bol van
   de hoofdstukband — 430 px, half buiten het blad linksboven. Die bol
   staat er omdat het blad zonder cijfer in het heldere register bijna
   leeg was: een streep en een woord onderaan, en verder wit, wat leest
   als een vergeten pagina in plaats van als een besluit. Is het blok
   zelf een kop die alleen "Bijlagen" of "Appendix" zegt, dan ís dat de
   tekst van het blad en is er niets toegevoegd. Staat er meer —
   "Bijlage A: methodeverantwoording" — dan draagt het blad het woord uit
   `bijlagen.titel` als `data-toevoeging="scheiding"`.
2. De openers **tellen in letters**: de kicker zegt "Bijlage A" in plaats
   van "Hoofdstuk 6".
3. Elke pagina daarna draagt `data-deel="bijlagen"`.
4. De inhoudsopgave krijgt er een **tussenkop** boven, als
   `.inhoud__groep`. Zonder die kop staat bijlage A tussen hoofdstuk 5 en
   6 en leest de opgave als een fout in de nummering.

Wat er níét verandert: het register, het model en het raster. Een bijlage
is een ander soort inhoud en geen ander rapport.

---

## 7c. Beeld

`beeld` in `ontwerp.json`: `geen`, `uit-bron` (default) of `aangeleverd`.
De skill vraagt dit expliciet, want stilzwijgend aannemen dat er geen
beeld is, is de reden dat een rapport kaal uitkomt terwijl de figuren in
een aparte map stonden.

Bij `aangeleverd` leest `bouw.py` een `beeld.json` uit de werkmap:

```json
[
  {"bestand": "beeld/extra/geldstroom.png", "na": "b0042",
   "bijschrift": "Verdeling van de vijftien bonds naar opdrachtgever."}
]
```

Elk beeld komt ná het genoemde blok. Het bijschrift komt van de gebruiker
en niet uit het rapport, dus het draagt `data-toevoeging="beeldbijschrift"`
— net als de regels op de omslag. Zonder bijschrift staat het beeld er
zonder, en dat is beter dan er een verzinnen.

**Een beeld dat te hard krimpt, krijgt de volle zetspiegel.** De grens is
een krimpfactor van **2,5**: intrinsieke breedte gedeeld door de breedte
waarop het beeld gerenderd wordt. Gemeten op een tabel van 3000 px gaat
hij in `dubbel` van 310 naar 650 px en in `breed` van 537 naar 650. Het
getal komt van twee kanten. Een figuur van 3120 px in een kolom van 537
px komt op 2,7 pt kapitaalhoogte uit; op ware grootte is diezelfde letter
15,7 pt, en die zakt door de leesvloer van 6 bij factor 2,6. En een
bitmap wordt op het dubbele geëxporteerd om op 192 dpi te drukken, dus
factor 2 is bedoeld en kost niets — 2,5 laat daar een halve factor
speling boven.

De regel keek vroeger naar `scrollWidth` en vuurde daarom nooit voor
beeld: een `img` met `max-width: 100%` wordt nooit te breed, hij krimpt.
Nu wordt de intrinsieke breedte gemeten, in elk model. Die breedte staat
als `data-eigenbreedte` op elke `<img>`, gestempeld op het origineel
vóórdat de stroom gekloond wordt — een verse kloon kent zijn
`naturalWidth` niet altijd al, en dan meet je nul en gebeurt er niets.
Gemeten wordt tegen de gerenderde breedte van hetzelfde beeld en niet
tegen de kaderbreedte: een beeld in een exhibit staat binnen de rand van
dat exhibit en is daar smaller dan de kolom.

**Wat het kost staat erbij.** De pagina die de promotie verlaat, blijft
half gevuld achter. Dat is inherent aan een zetting die één keer vooruit
loopt: de brede pagina moet ná de huidige komen en de blokken erna kunnen
niet terug zonder de leesvolgorde te breken. Het gebeurde al voor brede
tabellen en het gebeurt nu vaker. `qa_rapport.py` meet zo'n pagina als
`vulgraad`; dat is een aanwijzing en geen fout.

---

## 7d. Het achterwerk

Vier pagina's die niet uit het brondocument komen: over ons, het team,
het colofon en het achterblad. `elementen` in `ontwerp.json` zet ze aan,
en alle vier staan standaard **uit** — een rapport krijgt geen
teampagina omdat rapporten vaak een teampagina hebben.

```json
"elementen": {"overOns": false, "team": false,
              "colofon": false, "achterblad": false}
```

**De tekst komt uit `paginas.json`** in de werkmap, en nergens anders
vandaan:

```json
{"overOns":   {"kop": "…", "alineas": ["…"]},
 "team":      {"kop": "…", "intro": "…",
               "leden": [{"naam": "…", "rol": "…", "mail": "…"}]},
 "colofon":   {"kop": "Colofon", "regels": ["…"]},
 "achterblad": {"regels": ["…"], "veld": "oranje"}}
```

Dit is de enige plek in het hele rapport waar hele alinea's staan die
niet in het Word-document stonden. Ze dragen daarom allemaal
`data-toevoeging="pagina"`, `tekstcheck.py` telt ze apart — op de proef
34 — en bij de oplevering hoort te staan hoeveel er zo bij is gekomen en
van wie die tekst is. Schrijft de skill ze zelf, dan gaan ze woordelijk
langs de gebruiker voordat ze in het rapport komen.

**Staat een pagina aan zonder tekst, dan komt hij er niet.** Hij wordt
gemeld als `paginas_zonder_tekst` in het bouwverslag en dan vraag je
erom. Het achterblad is de uitzondering: dat bestaat ook zonder tekst,
want een achterkant met alleen het merk erop is af.

**De drie tekstpagina's dwingen geen rechterpagina af**, en dat is een
gemeten besluit. Ze dragen wél een `data-hoofdstuk` — ze hebben een
eigen kopregel nodig — maar daarnaast `data-recto="nee"`, en
`paginator.js` kijkt daarnaar voordat hij naar een recto springt. Zonder
dat attribuut dwong elk van de drie een rechterpagina af en kostte het
achterwerk vier blanco bladen: 49 pagina's werden er 53.

**Het achterblad dwingt er ook geen af**, en om een andere reden. Het is
de láátste pagina, en op de pers is dat de achterkant van het laatste vel
— een verso. Een achterblad dat naar een recto springt, zet er een blanco
pagina vóór en gaat zelf op de verkeerde kant van het vel staan. De
omslag en de hoofdstukbladen doen dat wél, want die beginnen iets.

Ze staan achteraan, ná het laatste notenblok, in de volgorde van
`EXTRA_PAGINAS`: over ons, team, colofon, achterblad. Een lezer die het
stuk leest komt ze pas tegen als hij klaar is. Het achterblad draagt
geen folio en geen kopregel en erft het veld van de omslag, tenzij
`paginas.json` er een eigen `veld` bij zet.

---

## 7e. Drukklaar

Twee sleutels: `drukklaar` (standaard `false`) en `katern` (standaard
`4`). Op de opdrachtregel is `drukklaar` de vlag `--drukklaar`.

De rekensom zelf staat niet hier maar in `scripts/gedeeld/drukwerk.py`,
en die module is **van beide drukskills tegelijk**: `sfnl-design-documents`
stelt bij kort drukwerk dezelfde vraag en krijgt hetzelfde antwoord. Een
gebonden of geniet drukwerk wordt per vel gedrukt en een dubbelgevouwen
vel is vier pagina's, dus een rapport van 49 pagina's wordt hoe dan ook
52 pagina's papier.

**Wat `bouw.py` doet als het niet uitkomt**: er komen blanco pagina's
achteraan tot het wél uitkomt, en die gaan vóór het achterblad, want dat
is op de pers de laatste pagina van het laatste vel. Dat is de enige van
de drie uitwegen die een script mag nemen. Inkorten kan niet — daar zit
tekst in — en het bij een PDF houden is een besluit van de gebruiker.

Het verslag geeft er twee dingen over terug: `katern` met één zin uitleg
("49 pagina's komt niet uit op een katern van 4: er moeten er 3 bij
(naar 52)") en `blanco_toegevoegd`. Gemeten op de proef: 49 pagina's
werden er 52 met drie blanco's.

Een blanco pagina draagt `data-blanco="ja"`, geen folio en geen
kopregel, en hij erft van de laatste pagina alleen wat het blad zelf is:
model, register, formaat en dichtheid. `qa_rapport.py` rekent hem niet
aan als lege pagina en telt hem niet mee in de gemiddelde vulgraad —
anders meet dat getal de drukkerij in plaats van de zetting.

**Na het invoegen worden `data-volgnr` en `data-zijde` opnieuw op
volgorde gezet.** Dat is niet netjesheid maar een reparatie: de blanco's
komen vóór het achterblad te staan, dus dat blad hield het volgnummer dat
het vóór de opvulling had. Op de eerste drukklare proef stond er twee
keer een pagina 49 in het bestand en stond het achterblad als recto
gemarkeerd terwijl het de laatste pagina van het laatste vel is, dus een
verso. De folio blijft ongemoeid — die komt uit de zetting en de
inhoudsopgave wijst ernaar, en de blanco's staan achter alles wat een
folio draagt.

**Wat er niet in zit**: een afloop van 3 mm en snijtekens. Die uitleg
staat één keer, in `documenten-stramien.md` §1a, en geldt voor beide
drukroutes.

---

## 8. Wat de zetmotor toevoegt aan de markup

Elk element dat brontekst draagt heeft `data-bron` met het blok-id uit
`document.json`. Elk element dat tekst draagt die de opmaak erbij heeft
gezet, heeft `data-toevoeging`. `tekstcheck.py` leunt op die twee, en
alles wat geen van beide heeft is tekst die niemand heeft goedgekeurd.

| attribuut | waar | wat het zegt |
|---|---|---|
| `data-bron` | elk tekstelement | het blok-id in `document.json` |
| `data-toevoeging` | folio, kopregel, inhoudsopgave, nummers, nootcijfers, herhaalde tabelkop, omslagregels, de vier pagina's van het achterwerk | dit is geen brontekst |
| `data-deel` | de helften van een gesplitst blok | 1 of 2 |
| `data-kop` | een kop | het niveau |
| `data-kop-tekst` | een kop | de kale tekst, voor de inhoudsopgave |
| `data-nieuwe-pagina` | een blok dat op een nieuwe pagina begint | |
| `data-heel` | een blok dat niet gesplitst mag worden | |
| `data-opener` | een hoofdstukopener of de omslag | `nummer`, `band`, `blad`, `omslag` |
| `data-hoofdstuk` | de opener | de naam voor de kopregel |
| `data-verwijst` | een regel in de inhoudsopgave | het blok-id van de kop waar hij naar wijst |
| `data-zijde` | de pagina | `recto` of `verso` |
| `data-folio` | de pagina | het paginanummer, ook als het niet gedrukt wordt |
| `data-flex` | de pagina | staat in een flexibel rapport |
| `data-recto` | een blok dat een pagina opeist | `nee` betekent: dit begint niet op een rechterpagina. Staat op over ons, het team, het colofon en het achterblad |
| `data-veld` | de omslag, het achterblad, het scheidingsblad | het kleurveld waarop de pagina staat |
| `data-sjabloon` | de omslag en het achterblad | welk paginasjabloon de zetmotor gebruikt |
| `data-blanco` | de pagina | een blanco blad dat het katern afmaakt |
| `data-eigenbreedte` | elke `<img>` | de intrinsieke breedte in px, gestempeld vóór het klonen. Zie §7c |

---

## 9. De werkmap

Eén map per rapport. Wat er in staat en wie het schrijft:

| bestand | door | wat |
|---|---|---|
| `document.json` | `lees_docx.py` | de blokken in leesvolgorde, met runs en voetnoten |
| `bron-tekst.txt` | `lees_docx.py` | de vingerafdruk: één genormaliseerde regel per blok |
| `signalen.json` | `lees_docx.py` | wat er aan de brontekst opvalt; grondstof voor wijzigingsvoorstellen |
| `beeld/` | `lees_docx.py` | de uitgepakte beelden |
| `ontwerpwidget.html` | `widget.py` | de intakepagina. Gaat naar de gebruiker en komt als `ontwerp.json` terug |
| `ontwerp.json` | jij, na de vormbesluiten | de vormbesluiten. Komt uit de widget en wordt woordelijk weggeschreven |
| `paginas.json` | jij, na de tekst van de gebruiker | de tekst voor de vier pagina's van het achterwerk. Zie §7d |
| `wijzigingen.json` | jij, ná toestemming | de goedgekeurde inhoudelijke wijzigingen |
| `citaten.json` | `citaten.py` | het omzettingsplan voor de verwijzingen, per blok |
| `beeld.json` | jij, bij `beeld: aangeleverd` | welk bestand achter welk blok komt |
| `extra.css` | jij, als dit rapport iets eigens nodig heeft | CSS die alleen voor dít rapport geldt. Optioneel. Zie §9b |
| `_zetten.html` | `bouw.py` | de werkpagina met de stroom en de zetmotor. Weggooibaar |
| `<naam>.html` | `bouw.py` | het rapport, in één bestand met de letters ingesloten |
| `<naam>.pdf` | `bouw.py` | dezelfde pagina's op de bladmaat die het document zelf zegt |
| `canvas/` | `bouw.py` | één `.dc.html` per pagina plus `canvas.json` en `fonts.css`: het rapport als artboards |
| `zetverslag.json` | `bouw.py` | wat de zetting deed, per ronde |
| `tekstcheck.json` | `tekstcheck.py` | het volledige tekstverslag |
| `qa_rapport.json` | `qa_rapport.py` | de metingen |
| `png/` | `render.py` | de contactbladen en de losse pagina's |

`ontwerp.json` — de sleutels, met hun default:

```json
{
  "taal": "nl",
  "model": "breed",            "register": "helder",
  "formaat": "sfnl",           "opener": "nummer",
  "dichtheid": "gemiddeld",    "bandhoogte": 232,
  "dubbelzijdig": true,        "omslag": true,
  "inhoudsopgave": true,       "inhoudDiepte": 2,
  "hoofdstuknummers": true,    "exhibitnummers": true,
  "noten": "voetnoot",         "bronnenlijst": "geen",
  "citaatstijl": "zoals-aangeleverd",
  "beeld": "uit-bron",         "beeldmap": null,
  "bijlagen": null,            "eersteFolio": 1,
  "folioVanaf": 2,             "rapporttitel": null,
  "ondertitel": null,          "opdrachtgever": null,
  "datum": null,               "omslagveld": "oranje",
  "elementen": {"overOns": false, "team": false,
                "colofon": false, "achterblad": false},
  "drukklaar": false,          "katern": 4,
  "herindelen": false,         "beeldtekst": false
}
```

`taal` staat vooraan omdat dat besluit als eerste vaststaat; de andere
jongste sleutels staan onderaan in het blok. Ze staan allemaal op de
veiligste stand:

| sleutel | default | wat het besluit |
|---|---|---|
| `taal` | `"nl"` | de taal waarin het rapport gezet wordt, als ISO-code. Stuurt de afbreking én de woorden die de skill zelf toevoegt. Elke code mag; er is geen lijst om tegen te toetsen. Op de opdrachtregel `--taal`. Zie §9b |
| `hoofdstuknummers` | `true` | `true` (de skill telt zelf), `false` (geen kicker en geen watermerkcijfer) of `"uit-bron"` (geen kicker, wél een cijfer, en dat cijfer uit de kop). De koptekst verandert in geen van de drie |
| `omslagveld` | `"oranje"` | het kleurveld van de omslag: `oranje`, `verloop`, `navy`, `violet`, `mint` of `wit`. Gaat vóór het register; zie `rapport-vormentaal.md` §7 |
| `elementen` | alles `false` | welke van de vier pagina's van het achterwerk erin komen. Zie §7d |
| `drukklaar` + `katern` | `false`, `4` | of het aantal pagina's moet uitkomen op de pers, en op welk katern. Zie §7e |
| `herindelen` | `false` | mag de opmaak voorstellen doen om de tekst anders in te delen. Bij `false` doet de skill er geen enkel |
| `beeldtekst` | `false` | mag tekst binnen een beeld of infographic worden aangepast |

`bijlagen` is `null` of `{"vanaf": "b0180", "titel": "Bijlagen"}`;
`beeld.json` is een lijst van
`{"bestand": "figuur-3.png", "na": "b0042", "bijschrift": "…"}`, waarin
`na` het blok-id is waarachter het beeld komt en `bijschrift` mag
ontbreken. `colofon` bestaat niet meer als losse sleutel: die pagina
zit nu in `elementen`, met zijn tekst in `paginas.json`.

**`herindelen` en `beeldtekst` zijn toestemmingen en geen vormbesluiten.**
Ze staan hier omdat `ontwerp.json` de plek is waar de besluiten van de
gebruiker worden bewaard, maar ze schakelen niets aan de opmaak: ze
bepalen of de skill iets mág vragen. `herindelen: false` betekent dat
stap 3 van de skill overgeslagen wordt; `beeldtekst: false` betekent dat
de tekst in een figuur blijft staan zoals hij staat. In deze route is
beeld een rasterbestand uit de docx en is die tekst praktisch
onbereikbaar, dus het is vooral een afspraak — in `sfnl-design-documents`
bijt dezelfde regel harder, want daar staat de SVG inline in de markup.
Dezelfde twee woorden in beide skills, met opzet.

`bouw.py` waarschuwt wanneer er goedgekeurde wijzigingen liggen terwijl
`herindelen` op nee staat. Ze worden wél toegepast — een per geval
gegeven ja weegt zwaarder dan een schakelaar die vooraf op nee stond —
maar er is dan ergens een besluit overgeslagen en dat hoor je te zien.

`wijzigingen.json` — een lijst besluiten. Zonder `"akkoord": true`
gebeurt er niets. Zes soorten en meer bestaan er niet:

```json
[
  {"soort": "tekst",  "id": "b0042", "naar": "…", "reden": "…", "akkoord": true},
  {"soort": "kop",    "id": "b0018", "naar": "…", "reden": "…", "akkoord": true},
  {"soort": "knip",   "id": "b0031", "op": "De tweede route", "reden": "…", "akkoord": true},
  {"soort": "lijst",  "ids": ["b0055","b0056","b0057"], "geordend": true,
   "teken_vervalt": true, "reden": "…", "akkoord": true},
  {"soort": "chapeau", "id": "b0009", "reden": "…", "akkoord": true},
  {"soort": "tabelkop", "id": "b0077", "reden": "…", "akkoord": true}
]
```

---

## 9a. De documentsignalen

`lees_docx.py` schrijft twee soorten waarneming in `signalen.json`, en ze
staan uit elkaar omdat ze op een ander moment aan de beurt zijn. Elk
signaal draagt een `groep`:

| groep | wat het is | wanneer |
|---|---|---|
| `voorstel` | een waarneming over één blok: een kop van 74 tekens, vier handgetypte streepjes, een alinea van 280 woorden. Draagt `wijziging` | stap 3, en alleen bij `herindelen: true` |
| `vormbesluit` | een waarneming over het document als geheel. Draagt `besluit` | vóór het bouwen, in de widget en in stap 1 |

In `signalen.json` staan ze in één lijst, met de vormbesluiten vooraan;
de uitvoer van het script noemt ze apart onder `vormbesluiten`.

De zes vormbesluiten komen alle zes uit één rapport — Engels, 18.043
woorden, 522 blokken, 72 eindnoten, vijf bijlagen, zes figuren waarvan
vier EMF — en ze waren daar alle zes bij het inlezen al te zien. Zie
`rapport-vormentaal.md` §13.

| soort | wat het ziet | waar de detectie ophoudt |
|---|---|---|
| `bron-niet-nederlands` | de lopende tekst is niet Nederlands, met de tellingen per taal erbij | alleen woorden die in **precies één** taallijst staan; de vaakst voorkomende woorden zijn gedeeld ("de" in nl en fr, "was" in nl en en) en die maken het onderscheid troebel. Tabellen tellen niet mee, onder 80 woorden wordt er niets gemeld, en er moeten twee keer zoveel treffers zijn als voor het Nederlands, én vier procent van alle woorden. Een Nederlands rapport met een Engels citaat per hoofdstuk — ruim een derde van de tekst — meldt niets |
| `koppen-een-niveau-te-diep` | de hoogste kop staat op niveau 2 of dieper | meldt alleen als niveau 1 **helemaal niet** voorkomt, en pas vanaf vier koppen |
| `kop-nummert-zichzelf` | een kopniveau draagt zijn eigen nummering | per niveau geteld, met een drempel van drie koppen en zestig procent. Daarom melden "Bijlage A" en "Bijlage B" niet. Een los getal zonder punt telt niet mee, en een jaartal ook niet — hoogstens drie cijfers |
| `beeld-niet-renderbaar` | een beeldformaat dat Chromium niet toont: EMF, WMF, TIFF, EPS, WDP, HDP, PICT | op de extensie; wat er ín het bestand zit, wordt niet gelezen |
| `beeld-buiten-de-stroom` | media in het `.docx` die door geen enkel blok wordt genoemd — een tekstvak, SmartArt, een figuur in de koptekst | het zegt dat het er is, niet waar het hoort; dat staat nergens in het bestand |
| `kop-zonder-inhoud` | een kop met niets eronder | meldt **niet** als er een diepere kop volgt — dat is de gewone hoofdstukkop met zijn eerste sectiekop. Zonder die toets gaf het Engelse rapport zes treffers waarvan er één echt was. Twee koppen op het bovenste niveau achter elkaar tellen ook niet: dat is de deeltitel |

**Elk van de zes komt hoogstens één keer in de lijst**, met zijn
treffers erin. Over vier EMF-figuren valt één besluit te nemen; vier losse regels
maken van een besluit een lijst, en een lijst wordt overgeslagen. De eis
die het zwaarst weegt is dat er geen valse bij zitten: een signaallijst
die één keer onzin zegt, wordt daarna niet meer gelezen.

Nagemeten op het Nederlandse proefdocument: nul vormbesluiten en dezelfde
achttien voorstellen als daarvoor.

`widget.py` zet ze bovenaan de widget onder "Dit moet je eerst
beslissen", elk met wat er gezien is en wat ermee gebeurt, en met één of
twee voorbeelden uit het document erbij. Zijn er geen bevindingen, dan is
er geen blok.

---

## 9b. `extra.css` en de taal — wat vóór het zetten vaststaat

Twee dingen bepalen waar elke regel valt, en allebei moeten ze vaststaan
vóórdat `bouw.py` draait. Wat er daarna aan verschuift, valt weg onder de
`overflow: hidden` van het kader, en dat is de enige fout in deze skill
die geen foutmelding geeft.

**De taal.** `"taal"` in `ontwerp.json`, `--taal` op de opdrachtregel, en
het komt terecht in `<html lang="…">` van **beide** sjablonen — de
werkpagina waarop gezet wordt en het bestand dat wordt opgeleverd. `lang`
bepaalt met welk woordenboek Chromium afbreekt. Gemeten: één omzetting
van `nl` naar `en` ná het zetten maakte drie alinea's een regel langer,
en die regels vielen onder de kaderrand weg.

De taal doet nog twee dingen:

- **De afbreekproef volgt de taal.** Die proef zet een lang woord in een
  doos van 62 px en kijkt of het afbreekt, en de uitkomst bepaalt of het
  hele rapport uitgevuld of vlaggend wordt gezet. Hij stond vast op
  Nederlands met een Nederlands proefwoord. `PROEFWOORDEN` heeft er nu
  een per taal — nl, en, de, fr, es, it — met het Engelse als terugval.
  Een taal zonder eigen woord krijgt geen goede toets voor die taal, maar
  wel een eerlijke: hij meet of Chromium überhaupt een woordenboek heeft,
  en bij twijfel vervalt het uitvullen. Dat is de veilige kant.
- **De woorden die de skill zelf toevoegt.** `LABELS` in `bouw.py` heeft
  negen sleutels per taal: `hoofdstuk`, `bijlage`, `bijlagen`, `figuur`,
  `noten`, `noten_hoofdstuk`, `noot`, `bron` en `vervolg`. `nl` en `en`
  staan erin. De laatste drie staan niet in de HTML maar in `content:` in
  de CSS en kunnen dus niet uit Python komen; ze gaan als custom property
  mee — `--label-noot`, `--label-bron` en `--label-vervolg` — met het
  Nederlandse woord als terugval in het stijlblad zelf. Zonder variabele
  verandert er dus niets aan een Nederlands rapport.

`en-GB` put uit `en`: een streekvariant heeft dezelfde woorden. Een taal
waar geen tabel voor is, krijgt de goede afbreking en Nederlandse
woorden, met een melding op stderr. Stil Nederlandse woorden boven een
Portugese kop zetten is erger dan de melding.

**`extra.css`.** Ligt er een `extra.css` in de werkmap, dan gaat hij
achter de letters, `stijl.css` en `rapport.css` aan — in **beide**
sjablonen, want zetten met andere CSS dan er opgeleverd wordt is precies
het soort fout dat pas in de PDF te zien is. Dit is de enige plek waar
één rapport iets eigens mag doen. De twee uitwegen die er zonder deze
haak waren, deugen allebei niet: de gedeelde `rapport.css` aanpassen
overkomt elk volgend rapport ook, en ná het zetten stylen verschuift de
regelval onder een zetting die al gemeten is.

Het labelblok komt ná `extra.css` en in hetzelfde document. Wie een van
de drie labels daar wil overschrijven, heeft dus `!important` nodig; dat
is de prijs voor één plek waar de labels vandaan komen.

Het bouwverslag zegt terug waarmee er gezet is: `taal`, `labels` (uit
welke labeltabel er geput is), `extra_css` (het aantal regels, of
`geen`) en `hoofdstuknummers` (`eigen telling`, `geen` of `uit de kop`).

---

## 9c. De nootnummering

Een noot krijgt zijn nummer bij **zijn eerste voorkomen in de lopende
tekst**, uit één telling over het hele rapport. De verwijzing en de noot
lezen uit die telling, en de noten worden er ook op gesorteerd.

Twee dingen gingen daar mis en ze staan als punt 18 op de weigerlijst:

- **De `<sup>` in de lopende tekst werd leeg gelaten.** Het commentaar
  zei dat de zetmotor het cijfer erbij zou zetten, en in `paginator.js`
  staat geen regel die dat doet. Op een rapport van 72 eindnoten stonden
  alle 72 genummerd aan de voet en stond er in de tekst geen enkel cijfer
  dat ernaar wees.
- **Het nummer kwam uit het Word-id.** Word begint zijn eindnoot-id's bij
  2 — −1, 0 en 1 zijn scheidingstekens — dus elke noot stond één te hoog.
  `_ruw_nummer` bestaat nog als terugval voor een noot zonder telling;
  binnen `Stroom` gaat de telling altijd mee.

**De controle die het bewijst**: `nootnummer` in `tekstcheck.json` hoort
**twee keer** het aantal noten te zijn — één cijfer in de tekst en één
bij de noot. Op het proefrapport stond er 6 bij 6 noten; nu staat er 12.
Het bouwverslag zegt in `noten` hoeveel er genummerd zijn.

Bij `noten: geen` verdwijnt ook het verwijzingscijfer. Een noot die er
niet is met een bovengezet cijfer ervoor is erger dan geen noot: de lezer
zoekt naar iets wat nergens staat.

`qa_rapport.py` herkent een noot sindsdien aan zijn markering en niet aan
zijn maat. Dat is nodig geworden: nu er werkelijk een cijfer in de `sup`
staat, is een noot van een superscript uit de brontekst alleen nog aan
het attribuut te onderscheiden.

---

## 10. De scripts

`$S` is `${CLAUDE_PLUGIN_ROOT}/scripts/rapport`.

| script | wat | blokkeert |
|---|---|---|
| `preflight.py` | is er een browser, de letters, de stijl, en werkt de Nederlandse afbreking | ja, bij geen browser |
| `lees_docx.py <bron> --uit <werkmap>` | `.docx`, `.md` of `.txt` uitlezen naar `document.json`, `bron-tekst.txt`, `signalen.json` en `beeld/` | |
| `bouw.py <werkmap>` | de stroom schrijven, in de browser zetten, de inhoudsopgave in meerdere rondes vullen, en het losse HTML-bestand schrijven | |
| `bouw.py <werkmap> --nieuw-ontwerp` | `ontwerp.json` met de defaults | |
| `bouw.py <werkmap> --drukklaar` | hetzelfde, plus blanco pagina's tot het aantal uitkomt op het katern. Zie §7e | |
| `widget.py <werkmap>` | de ontwerpwidget voor dít rapport: alle vormbesluiten op één pagina, en alleen wat de bron werkelijk heeft. **Het verplichte beginpunt** | |
| `citaten.py <werkmap> --naar <stijl>` | het omzettingsplan voor de verwijzingen in `citaten.json`. Draait vóór `bouw.py` | |
| `tekstcheck.py <html>` | staat er nog precies wat er stond | **ja** |
| `qa_rapport.py <html>` | veertien metingen; zes ervan blokkeren | **ja** |
| `render.py <html>` | contactbladen per twaalf spreads, of één spread, of één pagina | |
| `keuzekaart.py` | de drie keuzekaarten opnieuw bouwen. Onderhoud | |
| `artboards.py <html>` | het gezette rapport uit elkaar halen tot `.dc.html`-artboards plus `canvas.json`. `bouw.py` draait hem zelf | |

En één script dat hier niet staat maar wel meedoet:

| script | wat |
|---|---|
| `scripts/gedeeld/drukwerk.py` | de katernsom: komt dit aantal pagina's uit op de pers, en zo niet, hoeveel erbij of eraf. `bouw.py` leest hem via `vul_aan_tot_katern` |

Die staat in `gedeeld/` en niet in `rapport/` omdat hij **van beide
drukskills tegelijk** is: `sfnl-design-documents` stelt dezelfde vraag
over kort drukwerk en hoort hetzelfde antwoord te krijgen. Hij rekent en
hij beslist niet; los te draaien met `python drukwerk.py 45`.

De volgorde is `preflight` → `lees_docx` → `widget` → (`citaten`) →
`bouw` → `tekstcheck` → `render` en `qa_rapport`. `widget.py` staat er
niet tussen haakjes: er wordt niets gebouwd voordat de ingevulde
`ontwerp.json` terug is. `citaten.py` staat er wél tussen haakjes, want
die draait alleen wanneer `citaatstijl` iets anders is dan
`zoals-aangeleverd`; `bouw.py` leest het plan dat hij achterlaat.

`bouw.py` heeft geen renderloze route. Het splitsen van een alinea op een
regelgrens kan alleen een engine die weet hoe breed een woord is.

**En hij levert altijd drie dingen tegelijk**: het HTML-bestand, de PDF
en de artboards. Dat is geen vlag en er is geen stand waarin er één
wegvalt. De reden dat het in het bouwscript zit en niet in de skill: het
stond in de skill, als proza met een verwijzing naar een andere skill
erbij, en proza wordt overgeslagen. Wie een rapport oplevert zonder PDF,
levert iets op wat de opdrachtgever niet kan openen op de manier waarop
hij het gaat lezen; wie het oplevert zonder artboards, levert iets op
waar niemand meer iets aan kan verschuiven.

Twee van de drie modules staan in `scripts/gedeeld` omdat de
documentenroute ze net zo hard nodig heeft:

| module | wat | van wie |
|---|---|---|
| `gedeeld/drukwerk.py` | de katernsom: komt dit aantal pagina's uit op de pers | beide drukroutes |
| `gedeeld/naar_pdf.py` | het document printen op de bladmaat die het zelf zegt | beide drukroutes |
| `gedeeld/canvas.py` | de artboards in spreads neerleggen: 1 alleen, dan 2-3, 4-5 | beide drukroutes |
