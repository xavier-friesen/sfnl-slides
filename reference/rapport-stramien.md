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
| 132 / 240 | | watermerk | `.opener__watermerk` — geen tekst, een merkteken |

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
| `.voetnoten` | de bak aan de voet |

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
| `.opener__watermerk` | het cijfer half achter de titel. `left: 0`, want het kader snijdt af |
| `.opener-band` | de aflopende band; `--balk` op de `.pagina` |
| `.inhoud`, `.inhoud__regel`, `.inhoud__nr`, `.inhoud__naam`, `.inhoud__leader`, `.inhoud__folio` | de inhoudsopgave. De puntenlijn is een lijnelement en geen reeks punten, want punten zouden als toegevoegde tekst opduiken |
| `.omslag`, `.omslag__boven/__midden/__onder`, `.omslag__titel`, `.omslag__onderschrift`, `.omslag__regel` | de omslag |
| `.kantnoot` | een kanttekening in de kantlijn, met een streepje erboven |
| `.voetnoot` | een noot aan de voet, of in de kantlijn in het kantlijnmodel |
| `.paneel--rapport` | een gekleurd vlak met een blok tekst |

---

## 6. De vier registers

Op `data-register` van de `.pagina`. Een register zet vier variabelen;
al het andere leest die vier.

| register | `--r-accent` | `--r-accent-2` | `--r-tint` | `--r-watermerk` | de opener |
|---|---|---|---|---|---|
| `helder` | oranje `#F87F4F` | navy | navy-tint `#F4F3F7` | oranje-tint `#FFDFD0` | wit |
| `diep` | oranje | navy | navy-tint | oranje-tint | navy blad, witte inkt |
| `zacht` | emerald `#6AC6BA` | navy | mint-tint `#E0F4F1` | `#CDEBE5` | mint blad |
| `contrast` | violet `#6B5DAE` | oranje | `#EEEBF6` | `#DCD5EE` | violet blad, witte inkt |

In `zacht` blijft de folio oranje, zodat het merk niet verdwijnt.

---

## 7. De drie hoofdstukopeners

Op `data-opener`. Eén manier voor álle hoofdstukken in een rapport.

| opener | wat je krijgt | wat het kost |
|---|---|---|
| `nummer` | kicker, titel en een watermerkcijfer half erachter, boven aan de eerste pagina van het hoofdstuk | niets |
| `band` | een aflopende band bovenaan die pagina; `--balk` bepaalt de hoogte (232 px is de default) | ongeveer een kwart pagina |
| `blad` | een heel blad met de hoofdstuknaam onderin en het cijfer op 240 px erachter | een pagina per hoofdstuk; pas vanaf veertig pagina's |

De **omslag** is geen hoofdstukblad: die krijgt `data-opener="omslag"`,
en daar staat de titel in het midden in plaats van onderaan.

---

## 8. Wat de zetmotor toevoegt aan de markup

Elk element dat brontekst draagt heeft `data-bron` met het blok-id uit
`document.json`. Elk element dat tekst draagt die de opmaak erbij heeft
gezet, heeft `data-toevoeging`. `tekstcheck.py` leunt op die twee, en
alles wat geen van beide heeft is tekst die niemand heeft goedgekeurd.

| attribuut | waar | wat het zegt |
|---|---|---|
| `data-bron` | elk tekstelement | het blok-id in `document.json` |
| `data-toevoeging` | folio, kopregel, inhoudsopgave, nummers, nootcijfers, herhaalde tabelkop, omslagregels | dit is geen brontekst |
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

---

## 9. De werkmap

Eén map per rapport. Wat er in staat en wie het schrijft:

| bestand | door | wat |
|---|---|---|
| `document.json` | `lees_docx.py` | de blokken in leesvolgorde, met runs en voetnoten |
| `bron-tekst.txt` | `lees_docx.py` | de vingerafdruk: één genormaliseerde regel per blok |
| `signalen.json` | `lees_docx.py` | wat er aan de brontekst opvalt; grondstof voor wijzigingsvoorstellen |
| `beeld/` | `lees_docx.py` | de uitgepakte beelden |
| `ontwerp.json` | jij, na het vragenvuur | de vormbesluiten |
| `wijzigingen.json` | jij, ná toestemming | de goedgekeurde inhoudelijke wijzigingen |
| `_zetten.html` | `bouw.py` | de werkpagina met de stroom en de zetmotor. Weggooibaar |
| `<naam>.html` | `bouw.py` | het rapport. Dít is de oplevering |
| `zetverslag.json` | `bouw.py` | wat de zetting deed, per ronde |
| `tekstcheck.json` | `tekstcheck.py` | het volledige tekstverslag |
| `qa_rapport.json` | `qa_rapport.py` | de metingen |
| `png/` | `render.py` | de contactbladen en de losse pagina's |

`ontwerp.json` — de sleutels, met hun default:

```json
{
  "model": "breed",            "register": "helder",
  "formaat": "sfnl",           "opener": "nummer",
  "bandhoogte": 232,           "dubbelzijdig": true,
  "omslag": true,              "inhoudsopgave": true,
  "inhoudDiepte": 2,           "hoofdstuknummers": true,
  "exhibitnummers": true,      "eersteFolio": 1,
  "folioVanaf": 2,             "rapporttitel": null,
  "ondertitel": null,          "opdrachtgever": null,
  "datum": null,               "colofon": null
}
```

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

## 10. De scripts

`$S` is `${CLAUDE_PLUGIN_ROOT}/scripts/rapport`.

| script | wat | blokkeert |
|---|---|---|
| `preflight.py` | is er een browser, de letters, de stijl, en werkt de Nederlandse afbreking | ja, bij geen browser |
| `lees_docx.py <bron> --uit <werkmap>` | `.docx`, `.md` of `.txt` uitlezen naar `document.json`, `bron-tekst.txt`, `signalen.json` en `beeld/` | |
| `bouw.py <werkmap>` | de stroom schrijven, in de browser zetten, de inhoudsopgave in meerdere rondes vullen, en het losse HTML-bestand schrijven | |
| `bouw.py <werkmap> --nieuw-ontwerp` | `ontwerp.json` met de defaults | |
| `tekstcheck.py <html>` | staat er nog precies wat er stond | **ja** |
| `qa_rapport.py <html>` | dertien metingen; vier ervan blokkeren | **ja** |
| `render.py <html>` | contactbladen per twaalf spreads, of één spread, of één pagina | |
| `keuzekaart.py` | de drie keuzekaarten opnieuw bouwen. Onderhoud | |

`bouw.py` heeft geen renderloze route. Het splitsen van een alinea op een
regelgrens kan alleen een engine die weet hoe breed een woord is.
