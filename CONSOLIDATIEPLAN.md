# Consolidatieplan — alle SFNL-designskills in één plugin

Status: **besloten, in uitvoering.** Herijkt op `origin/main` 6a6f10a (plugin 1.6.0, vier skills)
en op de negen opmerkingen bij de eerste versie van dit plan.

De plugin draagt vier skills. Daarbuiten staan in de org-sync nog vijf skills die over vorm gaan,
en twee gaten die geen enkele skill dekt. Dit plan brengt ze samen tot acht skills onder één
merklaag, en noemt wat er weggaat.

De regel eronder: **een kleurwaarde staat één keer, een kleurregel staat per medium.** Dat is de
scheiding tussen wat gedeeld hoort en wat mag verschillen. Een rapport en een PowerPoint horen
verschillende maatladders te hebben — die zijn aan verschillend drukwerk gemeten. Hun oranje niet.

## Het paletbesluit: het sjabloon is de merkbron

Het aangeleverde `SFNL_Word_sjabloon.dotx` is nagemeten en zijn themakleuren waren geen van de vijf
gelijk aan wat de plugin rendeerde. **Besloten: de waarden van het sjabloon zijn correct, dus de
plugin past zich aan.**

| rol | plugin was | sjabloon, en nu canoniek |
|---|---|---|
| oranje | `#F87F4F` | `#FF7F40` |
| grapefruit | `#F95D63` | `#FF595A` |
| navy | `#201B5C` | `#21145F` |
| emerald | `#6AC6BA` | `#66C9BA` |
| royal | `#3B62C1` | `#425CC7` |

`#21145F` staat 26 keer in `styles.xml`, dus het sjabloon is intern consistent — dit was geen
uitschieter in één stijl. Vier waarden staan niet in het Word-thema (sky, violet, grijs en de vijf
tinten) en blijven zoals ze uit het drukwerk gemeten zijn.

**Geen enkele vormregel verandert hierdoor, en dat is nagemeten.** De contrastverhoudingen schuiven
marginaal en elke conclusie die erop staat houdt:

| meting | oud | nieuw | de regel die erop staat |
|---|---|---|---|
| oranje op wit | 2,58 | **2,51** | oranje draagt geen zin — haalt 4,5 niet en 3,0 niet |
| navy op oranje | 5,93 | **6,29** | daarom navy *op* een oranje vlak |
| navy op wit | 15,30 | **15,79** | navy is de inkt |
| grapefruit op wit | 3,10 | **3,08** | alleen grote tekst |
| emerald op wit | 2,02 | **1,98** | emerald draagt nooit tekst |
| royal op wit | 5,67 | **5,85** | royal mag een zin dragen |

Eén correctie onderweg: `rapport-vormentaal.md` §4 noemde 6,4 voor navy-op-oranje. Dat getal was
niet reproduceerbaar — de werkelijke oude verhouding was 5,93.

De renders in `assets/maatstaf/`, `assets/proeven/` en `assets/*/maatstaf/` zijn met de oude
waarden gebouwd en blijven staan. Het verschil ligt onder de drempel waarop je een maatstaf
opnieuw zet, en waar de proeven over contrast gaan staat de meting eronder en niet de kleur zelf.

Alles hiervan staat nu in **`reference/merk.md`** — de enige plek waar een kleurwaarde, een
letterfamilie of het logo staat.

## De namen

De plugin is de namespace, dus een skill wordt aangeroepen als `sfnl-design:sfnl-slides`. De prefix
hoefde niet twee keer.

| nu | wordt |
|---|---|
| plugin `sfnl-slides` | `sfnl-design` |
| `sfnl-slides` | `sfnl-slides` (ongewijzigd) |
| `sfnl-design-documents` | `sfnl-documenten` |
| `sfnl-rapport-opmaak` | `sfnl-rapport-deliverable` |
| `sfnl-infographic` | `sfnl-infographic` (ongewijzigd) |
| `sfnl-rapport` (org-sync) | `sfnl-affinity` |
| — nieuw | `sfnl-word` |
| — nieuw | `sfnl-online-design` |
| `sfnl-presentation-fixer` (org-sync) | `sfnl-deck-check` |

`rapport` alleen zei niet genoeg — het kon zowel de zetroute als de Affinity-route zijn, dus
`sfnl-rapport-deliverable` tegenover `sfnl-affinity`. `sfnl-online-design` in plaats van `scherm`,
want dat laatste zegt niets tegen wie de skill nog niet kent. En `sfnl-word` houdt zijn prefix:
het is de enige naam die tegen een bestaande skill aan schuurt (`docx` van Anthropic doet iets
anders maar heet bijna hetzelfde).

Twee randvoorwaarden die overal gelden. De woorden "Social Finance NL", "SFNL" en "huisstijl"
staan in élke `description` — daarop wordt getriggerd, niet op de naam. En de namen moeten uniek
zijn over alle geïnstalleerde skills samen, dus bezet en verboden: `design`, `docx`, `pdf`,
`pptx`, `xlsx`, `dataviz`, `run`, `init`, `loop`.

## De voorraad na consolidatie

| skill | status | wat er verandert |
|---|---|---|
| `sfnl-slides` | blijft | beleid komt uit `reference/`, niet uit de skill |
| `sfnl-documenten` | blijft | de twee uitbestedingsregels gaan naar de nieuwe skills wijzen |
| `sfnl-rapport-deliverable` | blijft | de zetroute, ongewijzigd van werking |
| `sfnl-infographic` | al binnen | gedaan in 1.6.0, met `samenstellen.md` en `insluiten.py` |
| `sfnl-affinity` | verhuist | houdt alleen de Affinity-uitvoering over; maten uit de stramienen |
| `sfnl-word` | nieuw | de snelle route: tussenproducten, notities, korte analyses |
| `sfnl-online-design` | nieuw | HTML dat meegroeit: dashboard, interactief overzicht, artifact |
| `sfnl-deck-check` | verhuist | leest het beleid van `sfnl-slides`, houdt zijn eigen tekstregels |
| `sfnl-design` (skill) | vervalt | opgesplitst in `sfnl-word` en `sfnl-online-design` |
| `sfnl-html-to-pdf` | vervalt | al opgeslokt door `scripts/gedeeld/naar_pdf.py` |
| `sfnl-excel`, `sfnl-projectplanner` | blijven buiten | ander vak; wel kleuren uit `merk.md` |
| `sfnl-projectpagina`, `sfnl-referentieslides` | blijven buiten | schrijfskills; vorm uitbesteden aan `sfnl-word` |

## Vier ontwerpbesluiten

### 1. De snelle route is de Word-route

Snel en Word zijn dezelfde as en niet twee assen. Een tussenproduct is per definitie een document
waar iemand in doortypt, en dat is precies wat Word is en wat HTML en PDF niet zijn. De
formaatkeuze doet daarmee het werk dat anders een disciplineoordeel had moeten doen: een lichte
skill naast een strenge wint normaal zodra iemand haast heeft, maar deze wint alleen waar hij het
juiste formaat is.

Erin: notitie, memo, korte analyse, verslag, gespreksnotitie, tussenproduct. Geen intakewidget —
één vraag als er iets echt ontbreekt, anders bouwen.

**De sluitregel is verplicht** en staat onder elke oplevering: *dit is een werkdocument; moet het
naar buiten, dan wordt het mooier met `sfnl-documenten` (kort drukwerk, 210 × 275 met snijrand)
of `sfnl-rapport-deliverable` (een lang stuk door de zetmotor)*. Zonder die regel wordt de snelle route
de gewone route en gaat er een `.docx` naar een fonds.

Eén risico erbij gemeld: een korte analyse die je mailt wil soms PDF zijn. `sfnl-word` krijgt
daarom een optionele PDF-druk, maar de vorm blijft die van een werkdocument. De opwaardeerroute is
niet de PDF-knop.

### 2. `sfnl-affinity` voert uit wat de andere skills bepalen

In de bronskill staan nu eigen maten: 420 × 275 mm, eigen raster, eigen kleurregels, eigen
typografie. Dat is dezelfde 210 × 275 als `sfnl-documenten`, maar als spread — twee bestanden
die hetzelfde blad beschrijven en dus uit elkaar gaan lopen.

Wat hij leest, afhankelijk van de vraag: een spread of casespread → `reference/rapport-stramien.md`;
een uitnodiging, one-pager of executive summary → `reference/documenten-stramien.md`; kleuren en
letters altijd → `reference/merk.md`.

Wat hij zelf houdt: de SDK-preamble en de leesplicht daarvan, de scriptbibliotheek met
`sfnl-`-prefix, de bekende SDK-valkuilen, de eenheidsomrekening, en `render_spread` als visuele
beoordeling — dat is hier het equivalent van de renderloop.

Wat hij niet doet: een rapport zetten. Loopt het over meer dan een paar pagina's, dan is de
zetmotor van `sfnl-rapport-deliverable` beter dan de hand, en dat zegt de skill dan ook.

**En hij is niet aan één paginatype gebonden.** De bronskill droeg een compleet uitgewerkte
casespread — vijf blokken in vaste volgorde, zeven paspoortvelden, vijf fondsarchetypes. Dat is
een oud artifact en het is eruit: de skill bouwt een generiek stuk SFNL-drukwerk of een
rapportpagina, en welke paginatypes er zijn staat in de stramienen en niet in de skill. Secties 1
tot 6 van het bouwscript zijn het apparaat en staan er voor elke pagina hetzelfde; 7 en 8 zijn de
kopij en de compositie, en die verschillen per paginatype.

Eén ding uit die casespread was wél echt en is gebleven, gegeneraliseerd: de veiligheidsregel dat
navy niet op elk gekleurd vlak kan. Opnieuw gemeten na de paletmigratie en uitgewerkt tot een
paringstabel in `merk.md` §1 — navy op royal haalt 2,70 en navy op violet 2,86, dus daar staat
wit; op oranje, grapefruit, emerald en sky staat navy.

### 3. `sfnl-deck-check` hoort bij `sfnl-slides`, maar niet in hetzelfde bestand

Eigen bestand, zelfde familie. `sfnl-slides` is 836 regels en de fixer 511; samen wordt dat
onleesbaar. En het triggersignaal is een ander: "bouw een deck" tegenover "hier is een deck, check
het", en één description die beide dekt laat de bouwroute vuren op een upload.

Wat gedeeld wordt is het **beleid**, en daar loopt een scherpe grens:

- **Wat écht dubbel is, gaat eruit.** De fixer heeft eigen typografiebeleid (regels 255–310) naast
  `reference/sjabloon.md` en `reference/vormentaal.md`. Twee definities van "wat mag op een
  SFNL-slide" is er één te veel.
- **Wat niet dubbel is, blijft compleet.** De tekstopschoningsregels zijn de kern van de skill en
  staan nergens anders: eindinterpunctie (punt of geen punt), slashspatiëring, dubbele spaties,
  interpunctiespatiëring, kapitalisatie, bullets en nummering, aanhalingstekens en streepjes, plus
  de "Do Not Touch"-lijst ervoor. Ook de bestandsdetectie, de PLAN → GLOBAL → APPLY-werkwijze, de
  roldetectie, de taal- en spellingcontrole en het CSV-wijzigingslogboek blijven.
- **Wat de bron zegt en de referenties niet, is winst** en gaat naar de referentie toe.

Bij twijfel: houden. Een regel kwijtraken is erger dan een regel dubbel hebben.

### 4. `sfnl-online-design` krijgt een harde grens

Eén pagina, geen buildstap, geen backend. Dit is de skill die het meest gevoelig is voor scope
creep richting "bouw een React-app", en dat is softwareontwikkeling en geen huisstijlopdracht.

Wat hier echt nieuw is en niet uit het drukwerk komt: **donkere modus als vormbesluit.** Navy
`#21145F` is de inkt van SFNL, en navy-op-navy is onleesbaar. Welke rol navy dan overneemt, of
oranje op donker nog accent kan zijn, en welke neutralen erbij horen — dat is een besluit met
metingen eronder, geen instelling achteraf. En de render moet in béide thema's gebeuren: een
pagina die je alleen in licht hebt gezien, is half gezien.

## De gedeelde laag

`reference/samenstellen.md` beschrijft sinds 1.6.0 al wat er gedeeld is: de letters, het voorblad,
de canvasroute, de drukwerkrekensom, de PDF-stap, het sjabloon en de OOXML-primitieven. Daar komt
nu de merklaag bij.

| laag | waar | wat erin staat |
|---|---|---|
| merkfeiten, invariant | `reference/merk.md`, `scripts/gedeeld/merk.py` | de hexwaarden met hun rol, de letterfamilies met gewicht en licentie, het logo, en de weigerlijst die overal geldt |
| vormentaal, per medium | `vormentaal.md`, `documenten-*`, `rapport-*`, `infographic-*`, `online-*`, `word-stramien.md` | maatladder, raster, kleurregisters, vulgraad, weigerlijst per medium — blijven waar ze staan |

De toets is mechanisch: staat er een hexwaarde in een script of een stylesheet, dan is dat een
fout; staat er een puntgrootte in `merk.md`, dan is dat er ook een. `scripts/preflight.py`
controleert de eerste helft met een grep, en hergenereert `assets/gedeeld/merk.css` uit `merk.py`
om te zien of het niet uit de pas loopt.

**En hier ligt een grens die makkelijk te overschrijden is.** Delen betekent de wáárden delen, niet
de regels. De drie `keuzekaart.py`'s zijn werkelijk verschillend, en dat hoort zo — ze rasteren
verschillende dingen voor verschillende besluiten. Hetzelfde voor de vormentalen. Wat hier gebeurt
is één duplicaat weghalen, niet uniformeren; waar twee scripts iets anders doen met dezelfde
kleur, blijft dat verschil staan.

## Wat er verder samengevoegd wordt

| wat | nu | wordt |
|---|---|---|
| kleuren, letters, logo | vijf scripts, `stijl.css`, `rapport.css`, twee stramienen | `merk.md` + `merk.py` → `merk.css` |
| preflight | vier stuks: root, `documenten/`, `infographic/`, `rapport/` | gedeelde kern plus dunne wrappers die hun eigen eisen toevoegen |
| browserlaag | `scripts/documenten/_browser.py` | `scripts/gedeeld/browser.py`, ook voor `sfnl-online-design` |
| metingfonts (`.ttf`, leeg) | `assets/fonts/`, met twee finders: `find_font_file()` in `_deck.py`, `vind_font()` in `svg.py` | één finder in `scripts/gedeeld/fonts.py` |
| insluitfonts (`.woff2`) | `assets/documenten/fonts/` | blijven staan; `sfnl-online-design` importeert ze |
| visuele tweede lezer | `agents/deck-visual-reviewer.md`, alleen decks | zelfde rol voor `sfnl-documenten`, `sfnl-rapport-deliverable` en `sfnl-online-design` |
| `requirements.txt` | de kop zegt "dependencies for the sfnl-powerpoint scripts" — een andere plugin | rechttrekken, plus wat `sfnl-word` en `sfnl-online-design` nodig hebben |
| keuzekaarten | drie `keuzekaart.py`'s | **blijven apart.** Ze zijn werkelijk verschillend |

## Wat het Word-sjabloon oplevert

Nagemeten op `assets/word/SFNL_Word_sjabloon.dotx` — dit wordt `reference/word-stramien.md`:

- **Het blad is geen echte A4**: `pgSz` is 209,90 × 297,03 mm waar A4 209,97 × 297,04 is. Reken
  daarom uit `pgSz` en niet uit "A4 min marges" — met marges van 25,4 mm rondom komt de
  zetspiegel op 159,10 mm en niet op 159,20. Kopregel en voettekst op 12,5 mm.
- **`titlePg` staat aan, en de kop- en voetteksten staan andersom dan ik eerst meldde.** Uit de
  rIds van `sectPr`: `header2` is de eerste pagina, met het grote PNG-logo; `header1` de default
  en die is leeg; `footer3` de eerste pagina, met een lege contactstrook van 3 × 53,0 mm;
  `footer2` de default, met het kleine logo en het paginanummer. `footer1` is de even-voet en
  wordt **nooit getoond**, want `evenAndOddHeaders` staat niet in `settings.xml`.
- **De stijlen staan er compleet in, de inhoud niet.** Het bestand heeft één lege alinea: het is
  een stijlendrager en geen voorbeeldpagina, dus de skill componeert zelf uit de stijlen.
- **Typografie:** `Standaard` is Lato Light 12 pt. `Titel` Montserrat SemiBold 28 pt met −0,5 pt
  spatiëring, `Ondertitel` Montserrat Light 11 pt met +0,75 pt. `Kop1` is Gotham Bold Regular
  22 pt met **+1,0** pt spatiëring (de −0,5 hoort bij `Titel`, niet hier), `Kop2` Montserrat
  Light 18 pt, `Kop3`–`Kop7` 12 pt en `Kop8`/`Kop9` 10,5 pt. De kopladder is dus 28 – 11 – 22 –
  18 – 12 en houdt daar op. Tabelstijl `TableGrid1` op 11 pt.
- **Alle stijl-id's zijn Nederlands** — `Standaard`, `Kop1`–`Kop9`, `Titel`, `Ondertitel`,
  `Citaat`, `Lijstalinea`, `TableGrid1`. Dit is de belangrijkste bouwersval: `w:pStyle
  w:val="Heading1"` valt stil terug op `Standaard`, en `qa_word.py` blokkeert erop.
- **De letternaam is `Gotham Bold Regular`**, vier keer in `Kop1`/`Kop1Char` plus één in
  `fontTable.xml`. Wie op `Gotham Bold` grept, vindt niets.
- **`Heading 1` vraagt een licentiefont.** Op een SFNL-machine staat Gotham; in een sandbox en op
  de machine van een klant niet, en dan substitueert Word stil — waardoor de regelval verandert
  zonder melding. `sfnl-word` maakt daar een expliciet besluit van met Montserrat SemiBold als
  terugval, en zegt bij oplevering welke van de twee in het bestand staat.
- **De themafonts zijn beide Lato Light**, dus Montserrat en Gotham hangen aan de stijlen en niet
  aan het thema. Wie een stijl overschrijft, verliest ze.
- **Het logo staat twee keer in het bestand:** als PNG van 59,9 × 16,0 mm op de eerste pagina,
  als JPG van 37,6 × 10,1 mm in de voettekst daarna. Meet met `wp:extent` en niet met `a:ext`;
  die lopen 1,87 % uiteen, dus het beeld wordt in zijn kader geperst. Beide zijn 934 × 251 px —
  de PNG 10.268 bytes met alfakanaal, de JPG 52.399 zonder. Dat hoort de PNG te zijn.

## Fasering

| | wat | staat |
|---|---|---|
| **F1** | Merkfeiten op één plek: `merk.md` (gedaan), `merk.py`, gegenereerde `merk.css`, de vijf nieuwe hexwaarden door de vijf scripts en twee stylesheets, de contrastgetallen in de vormentalen, de synccheck in preflight | in uitvoering |
| **F2** | `sfnl-word`: `word-stramien.md` uit het sjabloon, `scripts/word/`, de snelroute, de brede trigger, het Gotham-besluit, de verplichte sluitregel | in uitvoering |
| **F3** | `sfnl-affinity`: bron naar binnen, eigen maten eruit, de twee stramienen erin, alleen de SDK-laag over | in uitvoering |
| **F4** | `sfnl-online-design`: `online-vormentaal.md` met de donkeremodus-meting, `scripts/online/`, de renderloop in beide thema's, de harde grens | in uitvoering |
| **F6** | `sfnl-deck-check`: bron naar binnen, dubbel beleid eruit, de tekstregels compleet erin | in uitvoering |
| **F7** | Hernoemen en 2.0.0: de vier bestaande skills, de plugin, alle kruisverwijzingen, README, `plugin.json`, `marketplace.json` | na F1–F6 |
| **F5** | Intrekken uit de org-sync: `sfnl-design` en `sfnl-html-to-pdf` | **niet vanuit deze repo** |

F5 staat onderaan en met opzet los: die twee skills staan in de org-skillbibliotheek en niet in
deze repo, dus intrekken gebeurt in de beheeromgeving van de organisatie. Doe het pas nadat
`sfnl-word` en `sfnl-online-design` geïnstalleerd zijn, want tot dat moment is `sfnl-design` de enige
route naar Word en naar een dashboard.

## Openstaand

- **De naamgeving is nog niet één conventie.** `sfnl-documenten` en `sfnl-affinity`
  beschrijven de handeling, `sfnl-rapport-deliverable` het product, `sfnl-online-design` het medium, en
  `sfnl-slides`, `sfnl-infographic` en `sfnl-deck-check` staan er zonder voorvoegsel. Dat is te verdedigen — elke
  naam zegt wat hij doet — maar het is geen stelsel. Als er één van moet komen, is dat één commit
  extra en het moment is F7.
- **`agents/deck-visual-reviewer.md` voor de andere media** is benoemd maar niet ingepland.
