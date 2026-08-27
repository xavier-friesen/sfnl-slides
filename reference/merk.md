# Merk — de feiten die in elk medium hetzelfde zijn

Dit bestand is de enige plek waar een kleurwaarde, een letterfamilie of het logo staat. Alles wat
per medium verschilt — de maatladder, het raster, de kleurregisters, de vulgraad, de weigerlijst
van dát medium — staat niet hier maar in de vormentaal van de skill die het gebruikt.

**De regel: een kleurwaarde staat één keer, een kleurregel staat per medium.** Zo ook voor de
letters: de familie is invariant, de maat is per medium. Een rapport en een PowerPoint horen
verschillende maatladders te hebben, want ze zijn aan verschillend drukwerk gemeten. Hun oranje
niet.

**De toets is mechanisch.** Staat er een hexwaarde in een script of een stylesheet, dan is dat een
fout. Staat er een puntgrootte in dit bestand, dan is dat er ook een. `scripts/preflight.py`
controleert de eerste helft.

---

## 1. De kleuren

De vijf accenten komen uit het themapalet van `SFNL_Word_sjabloon.dotx`. Dat sjabloon is de
merkbron: het is het bestand dat in de organisatie circuleert en waarvan elke kleurkiezer in Word
en PowerPoint bij SFNL zijn waarden neemt.

| naam | hex | themaslot | rol |
|---|---|---|---|
| navy | `#21145F` | accent3 | de inkt. Lopende tekst is nooit puur zwart |
| oranje | `#FF7F40` | accent1 | het accent. Labels, de streep, de badge |
| wit | `#FFFFFF` | accent6 | het papier |
| grapefruit | `#FF595A` | accent2 | het tweede eind van het verloop; alarm, nadruk |
| emerald | `#66C9BA` | accent4 | positief, uitkomst |
| royal | `#425CC7` | accent5, hlink | secundaire data, en de hyperlink |

Vier waarden staan niet in het Word-thema en blijven daarom staan zoals ze gemeten zijn uit het
drukwerk:

| naam | hex | waar gemeten |
|---|---|---|
| sky | `#45B6E2` | tertiaire data |
| violet | `#6B5DAE` | de casespread; een heel paneel of een rail |
| grijs | `#F2F2F2` | een kaartvulling |

En de tinten, gemeten uit de vlakken in het rapport en niet berekend:

| naam | hex | waar |
|---|---|---|
| mint-tint | `#E0F4F1` | een hele pagina of een paneel in emerald |
| periwinkel | `#A0ADE2` | het interviewpaneel |
| oranje-tint | `#FFDFD0` | het watermerkcijfer |
| navy-tint | `#F4F3F7` | een stille container |

### Wat er op 27 augustus 2026 is veranderd, en waarom

De plugin rendeerde tot die datum vijf andere waarden. Ze zijn vervangen door die van het
sjabloon, omdat het sjabloon de merkbron is en de plugin niet.

| rol | was | is | verschuiving |
|---|---|---|---|
| oranje | `#F87F4F` | `#FF7F40` | iets warmer en verzadigder |
| grapefruit | `#F95D63` | `#FF595A` | idem |
| navy | `#201B5C` | `#21145F` | iets donkerder en blauwer |
| emerald | `#6AC6BA` | `#66C9BA` | vrijwel gelijk |
| royal | `#3B62C1` | `#425CC7` | iets lichter en blauwer |

`#21145F` staat 26 keer in `styles.xml` van het sjabloon, dus dat is geen uitschieter in één
stijl maar een consistent ander bestand.

**Geen enkele vormregel is hierdoor veranderd**, en dat is nagemeten. De contrastverhoudingen
schuiven marginaal en alle conclusies die erop staan houden:

| meting | oud | nieuw | de regel die erop staat |
|---|---|---|---|
| oranje op wit | 2,58 | **2,51** | oranje draagt geen zin — haalt 4,5 niet en 3,0 niet |
| navy op oranje | 5,93 | **6,29** | daarom navy *op* een oranje vlak |
| navy op wit | 15,30 | **15,79** | navy is de inkt |
| grapefruit op wit | 3,10 | **3,08** | alleen grote tekst, en dan nog met tegenzin |
| emerald op wit | 2,02 | **1,98** | emerald draagt nooit tekst |
| royal op wit | 5,67 | **5,85** | royal mag een zin dragen |

De oude waarde 6,4 die in `rapport-vormentaal.md` §4 stond voor navy-op-oranje was niet
reproduceerbaar; de gemeten verhouding was 5,93 en is nu 6,29.

De renders in `assets/maatstaf/`, `assets/proeven/` en `assets/*/maatstaf/` zijn met de oude
waarden gebouwd. Ze blijven staan: het verschil is onder de drempel waarop je een maatstaf
opnieuw zou zetten, en waar de proeven over contrast gaan staat de meting eronder en niet de
kleur zelf.

---

## 2. De letters

| familie | gewichten | licentie | mag mee in de plugin |
|---|---|---|---|
| Gotham | Bold | commercieel, Hoefler&Co | **nooit** |
| Montserrat | 300 Light, 600 SemiBold, 700 Bold, 800 ExtraBold | SIL OFL 1.1 | ja, met `OFL-Montserrat.txt` erbij |
| Lato | 300 Light, 400, 700, plus 300 en 400 cursief | SIL OFL 1.1 | ja, met `OFL-Lato.txt` erbij |

**Gotham is de merkletter en reist nooit mee.** Op een SFNL-machine staat hij; in een sandbox, in
een browser en op de machine van een klant niet. Elke route die hem zou willen gebruiken, neemt
in plaats daarvan een expliciet besluit met **Montserrat SemiBold** als terugval — expliciet, want
Word en LibreOffice substitueren anders stil en dan verandert de regelval zonder melding.

Waar de bestanden staan:

| soort | map | waarvoor |
|---|---|---|
| insluitfonts, `.woff2` | `assets/documenten/fonts/` | HTML en drukwerk sluiten ze in als data-URI via `fonts.css` |
| metingfonts, `.ttf`/`.otf` | `assets/fonts/` | de deck- en SVG-meting; leeg in de repo, want de statische snedes zijn niet meegeleverd |

Een document dat zijn letters bij Google Fonts haalt, valt terug op Helvetica zodra er geen
internet is, en de PNG- en PDF-export van het canvas neemt een Google Font sowieso niet mee. In
alles wat de plugin oplevert zijn de letters dus ingesloten of geïnstalleerd, nooit gelinkt.

---

## 3. Het logo

Het logo is een oranje cirkel, een oranje vierkant, "SOCIAL FINANCE" in navy Montserrat 800 en
"NL" in oranje. Als markup staat het in `assets/documenten/stijl.css` §8 en in
`reference/documenten-stramien.md`; als bitmap in het Word-sjabloon.

Uit het sjabloon nagemeten: de kopregel van de eerste pagina draagt hem als PNG op
59,9 × 16,0 mm, de voettekst van de volgende pagina's als JPG op 37,6 × 10,1 mm. Meet met
`wp:extent` en niet met `a:ext` — dat is het getal dat Word voor de opmaak gebruikt, en de twee
lopen 1,87 % uiteen, dus het beeld wordt in zijn kader geperst.

Het is dezelfde tekening twee keer, en de JPG hoort er niet te zijn: beide zijn 934 × 251 px, de
PNG is 10.268 bytes met alfakanaal en de JPG 52.399 progressief zonder. Vijf keer zo groot, geen
transparantie, en compressieartefacten op wit.

---

## 4. Wat overal geldt

Dit is de weigerlijst die niet per medium verschilt. De vormentaal van elk medium heeft er zijn
eigen bovenop.

- **Gotham reist niet mee.** Zie §2.
- **Geen schaduw.** Niet onder een kaart, niet onder een vlak, niet onder een letter.
- **Geen verloop buiten het huisverloop.** Er is er één, van oranje naar grapefruit onder 150
  graden, en die is gemeten. Een ander verloop is een andere huisstijl.
- **Geen kleur die niets codeert.** Vier hues op één vlak omdat het vrolijker staat, is vier keer
  hetzelfde zeggen.
- **Geen benaderde waarde.** `#F87F4F` is niet oranje meer, `#FF8040` is het nooit geweest, en
  "ongeveer oranje" bestaat niet. Wat hier niet staat, is geen merkkleur.
- **Oranje draagt geen lopende tekst.** 2,51 op wit. Navy op een oranje vlak wel, 6,29.

---

## 5. Voor de scripts

`scripts/gedeeld/merk.py` is de machineleesbare vorm van §1 en §2, en de enige. Hij levert:

- `KLEUREN` — naam → hex, met de rol erbij
- `LETTERS` — familie → gewichten, licentie, bestandspad
- `css_variabelen()` — het `:root`-blok
- `contrast(a, b)` — de verhouding, zodat een meting in een vormentaal navertelbaar is

`merk.py --css` schrijft `assets/gedeeld/merk.css`. Dat bestand gaat mee in de repo omdat een
stylesheet geen Python kan importeren; `scripts/preflight.py` hergenereert het, vergelijkt, en
blokkeert als het uit de pas loopt.
