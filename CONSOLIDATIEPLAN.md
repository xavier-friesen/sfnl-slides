# Consolidatieplan — alle SFNL-designskills in één plugin

Status: **voorstel, wacht op go.** Herijkt op `origin/main` 6a6f10a (plugin 1.6.0, vier skills).

De plugin heet nu `sfnl-slides` en draagt vier skills. Daarbuiten staan in de org-sync nog vijf
skills die over vorm gaan, en twee gaten die geen enkele skill dekt. Dit plan brengt ze samen tot
acht skills onder één merklaag, en noemt wat er weggaat.

De regel die eronder ligt: **een kleurwaarde staat één keer, een kleurregel staat per medium.**
Dat is de scheiding tussen wat gedeeld hoort en wat mag verschillen, en het antwoord op de vraag
of een rapport en een PowerPoint dezelfde vorm moeten hebben. Nee — hun maatladders zijn aan
verschillend drukwerk gemeten en horen te verschillen. Hun oranje niet.

## De meting die dit plan urgent maakt

Het aangeleverde `SFNL_Word_sjabloon.dotx` is nagemeten. Zijn themakleuren zijn geen van de vijf
gelijk aan het palet van de plugin:

| rol | Word-sjabloon | plugin | gelijk |
|---|---|---|---|
| oranje | `FF7F40` | `F87F4F` | nee |
| grapefruit | `FF595A` | `F95D63` | nee |
| navy | `21145F` | `201B5C` | nee |
| emerald | `66C9BA` | `6AC6BA` | nee |
| royal | `425CC7` | `3B62C1` | nee |

`21145F` staat 26 keer in `styles.xml`, dus het sjabloon is intern consistent — dit is geen
uitschieter in één stijl. Elke kleurkiezer in Word en PowerPoint bij SFNL biedt de linkerkolom
aan; alles wat deze plugin rendert staat in de rechterkolom.

**Dit is een besluit dat een mens moet nemen, niet een script.** Het palet van de plugin is
nagemeten aan gedrukt werk (jaarrapport 2025, casespread Civitates) en de hele
`assets/proeven/`-reeks, met zijn contrastmetingen, staat erop. Het sjabloon is het bestand dat
in de organisatie circuleert. Welke van de twee de merkwaarde is, valt uit geen van beide
bestanden af te leiden — dat staat in het merkhandboek.

Voorstel: het palet van de plugin blijft canoniek voor alles wat de plugin rendert, `merk.md`
noteert de sjabloonwaarden als bekende afwijking met de datum van de meting erbij, en de
`word`-skill schrijft het thema dat hij in het sjabloon vindt ongemoeid. Bij de volgende
sjabloonrevisie trek je de vijf waarden gelijk. Zolang dat niet gebeurd is, is stil corrigeren
erger dan de afwijking: dan wijkt een gegenereerd document af van elk document dat een collega
zelf maakt.

## De voorraad na consolidatie

| skill | status | wat er verandert |
|---|---|---|
| `slides` | blijft | beleid komt uit `reference/`, niet uit de skill |
| `documenten` | blijft | de twee uitbestedingsregels gaan naar de nieuwe skills wijzen |
| `rapport` | blijft | nu `sfnl-rapport-opmaak` |
| `infographic` | **al binnen** | gedaan in 1.6.0, inclusief `samenstellen.md` en `insluiten.py` |
| `affinity` | verhuist | nu `sfnl-rapport`. Houdt alleen de Affinity-uitvoering over |
| `word` | nieuw | de snelle route: tussenproducten, notities, korte analyses |
| `scherm` | nieuw | HTML dat meegroeit: dashboard, interactief overzicht, artifact |
| `deck-check` | verhuist | nu `sfnl-presentation-fixer`, leest het beleid van `slides` |
| `sfnl-design` | vervalt | opgesplitst in `word` en `scherm` |
| `sfnl-html-to-pdf` | vervalt | al opgeslokt door `scripts/gedeeld/naar_pdf.py` |
| `sfnl-excel`, `sfnl-projectplanner` | blijven buiten | ander vak; wel kleuren uit `merk.md` |
| `sfnl-projectpagina`, `sfnl-referentieslides` | blijven buiten | schrijfskills; vorm uitbesteden aan `word` |

## Vier ontwerpbesluiten

### 1. De snelle route is de Word-route

Snel en Word zijn dezelfde as en niet twee assen. Een tussenproduct is per definitie een document
waar iemand in doortypt, en dat is precies wat Word is en wat HTML en PDF niet zijn. De
formaatkeuze doet daarmee het werk dat anders een disciplineoordeel had moeten doen: een lichte
skill naast een strenge wint normaal zodra iemand haast heeft, maar deze wint alleen waar hij het
juiste formaat is.

Eén snelle skill dus, automatisch getriggerd, en die levert Word. Erin: notitie, memo, korte
analyse, verslag, gespreksnotitie, tussenproduct. Geen intakewidget — één vraag als er iets echt
ontbreekt, anders bouwen.

**De sluitregel is verplicht** en staat onder elke oplevering: *dit is een werkdocument; moet het
naar buiten, dan wordt het mooier met `documenten` (kort drukwerk, 210 × 275 met snijrand) of
`rapport` (een lang stuk door de zetmotor)*. Zonder die regel wordt de snelle route de gewone
route en gaat er een `.docx` naar een fonds.

Wat ik erbij meld: een korte analyse die je mailt wil soms PDF zijn. `word` krijgt daarom een
optionele PDF-druk, maar de vorm blijft die van een werkdocument. De opwaardeerroute is niet de
PDF-knop.

### 2. Namen zonder `sfnl-`, want de plugin is de namespace

Een plugin-skill wordt aangeroepen als `plugin:skill`, dus `sfnl-design:slides`. De prefix zit al
in de plugin en staat er nu twee keer.

Twee randvoorwaarden. De woorden "Social Finance NL", "SFNL" en "huisstijl" blijven in élke
`description` staan — daarop wordt getriggerd, niet op de naam. En de namen moeten uniek zijn over
alle geïnstalleerde skills samen, dus bezet en verboden: `design`, `docx`, `pdf`, `pptx`, `xlsx`,
`dataviz`, `run`, `init`, `loop`.

    slides · documenten · rapport · infographic · affinity · word · scherm · deck-check

`scherm` in plaats van `web` of `webapps`, omdat `documenten` zijn eigen grens al zo formuleert:
"een vast blad met een snijrand, geen scherm dat meegroeit". Dan is `scherm` letterlijk de andere
helft van die zin, en `-apps` nodigt uit tot de scope creep waar juist die skill gevoelig voor is.
`word` houdt `word`: dat is wat mensen zeggen als ze het vragen.

De rename gaat in één commit samen met de plugin-rename naar `sfnl-design` 2.0.0. De vier skills
verwijzen tientallen keren naar elkaar en half hernoemd is de slechtste toestand die er is. Kosten:
iedereen installeert één keer opnieuw.

### 3. `affinity` voert uit wat de andere skills bepalen

In `sfnl-rapport` staan nu eigen maten: 420 × 275 mm, eigen raster, eigen kleurregels, eigen
typografie. Dat is dezelfde 210 × 275 als `documenten`, maar als spread — twee bestanden die
hetzelfde blad beschrijven en dus uit elkaar gaan lopen.

Wat hij leest, afhankelijk van de vraag: een spread of casespread → `reference/rapport-stramien.md`;
een uitnodiging, one-pager of executive summary → `reference/documenten-stramien.md`.

Wat hij zelf houdt: de SDK-preamble en de leesplicht daarvan, de scriptbibliotheek met
`sfnl-`-prefix, de bekende SDK-valkuilen, de mm→pt-omrekening, en `render_spread` als visuele
beoordeling — dat is hier het equivalent van de renderloop.

Wat hij niet doet: een rapport zetten. Loopt het over meer dan een paar pagina's, dan is de
zetmotor van `rapport` beter dan de hand, en dat zegt de skill dan ook.

### 4. `deck-check` hoort bij `slides`, maar niet in hetzelfde bestand

Hier wijk ik af van de opdracht, en waarvan: "binnen `slides` laten vallen" lees ik als *moet de
policies van `slides` gebruiken en niet zijn eigen*. Dat is de hele winst — de fixer herhaalt nu
een eigen typografiebeleid (regels 255–310) naast `reference/sjabloon.md` en
`reference/vormentaal.md`, en twee definities van "wat mag op een SFNL-slide" is er één te veel.

In hetzelfde `SKILL.md` zetten kost twee dingen. `slides` is 836 regels en de fixer 511; samen
1300+, en een skill wordt in zijn geheel gelezen. Belangrijker: het triggersignaal is een ander.
"Bouw een deck" en "hier is een deck, check het" staan tegenover elkaar, en één description die
beide dekt laat de bouwroute vuren op een upload.

Dus: eigen bestand, zelfde familie. Leest `reference/`, gebruikt `scripts/qa_*.py`, herhaalt
niets. Dat is ook het patroon van de plugin zelf — één skill per taak, alles daaronder gedeeld.
Moet het toch één skill met twee routes worden, dan is dat een regel of tien extra.

## De gedeelde laag

`reference/samenstellen.md` beschrijft sinds 1.6.0 al wat er gedeeld is: de letters, het voorblad,
de canvasroute, de drukwerkrekensom, de PDF-stap, het sjabloon en de OOXML-primitieven. Wat daar
nog niet in zit is de merklaag zelf.

| laag | waar | wat erin staat |
|---|---|---|
| merkfeiten, invariant | `reference/merk.md`, `scripts/gedeeld/merk.py` | de hexwaarden met hun rol, de letterfamilies met gewicht en licentie, het logo, de bekende afwijking van het Word-sjabloon, en de weigerlijst die overal geldt |
| vormentaal, per medium | `vormentaal.md`, `documenten-*`, `rapport-*`, `infographic-*` | maatladder, raster, kleurregisters, vulgraad, weigerlijst per medium — blijven waar ze staan |

De toets is mechanisch: staat er een hexwaarde in een script of een CSS-bestand, dan is dat een
fout; staat er een puntgrootte in `merk.md`, dan is dat er ook een. `preflight.py` controleert de
eerste helft met een grep.

Vijf scripts en één stylesheet hebben de waarden nu hardgecodeerd: `scripts/documenten/widget.py`,
`scripts/infographic/schets.py`, `scripts/infographic/svg.py`, `scripts/rapport/keuzekaart.py`,
`scripts/rapport/widget.py`, `assets/documenten/stijl.css`. De hexwaarden in `assets/**/*.dc.html`
en `assets/infographic/maatstaf/*.svg` zijn gebouwde uitvoer en blijven staan.

Een stylesheet kan geen Python importeren, dus `merk.py --css` genereert `assets/gedeeld/merk.css`
met het `:root`-blok. Dat bestand gaat mee in de repo; `preflight.py` hergenereert het en
vergelijkt, en blokkeert als het uit de pas loopt. `stijl.css` en `rapport.css` importeren het en
zetten er alleen hun eigen maatvariabelen bovenop.

## Wat er verder samengevoegd moet worden

| wat | nu | wordt |
|---|---|---|
| kleuren, letters, logo | vijf scripts, `stijl.css`, twee stramienen, plus het Word-thema | `merk.py` → `merk.css` |
| preflight | vier stuks: `preflight.py`, `documenten/`, `infographic/`, `rapport/` | gedeelde kern plus dunne wrappers |
| keuzekaart / contactblad | drie `keuzekaart.py`'s plus `thumbnail.py` plus de schetsroute | gedeelde kern voor rasteren en labelen |
| browserlaag | `scripts/documenten/_browser.py` | `scripts/gedeeld/browser.py`, ook voor `scherm` |
| metingfonts (`.ttf`, leeg) | `assets/fonts/` met twee finders: `find_font_file()` in `_deck.py`, `vind_font()` in `svg.py` | één finder in `scripts/gedeeld/fonts.py` |
| insluitfonts (`.woff2`) | `assets/documenten/fonts/` | `assets/gedeeld/fonts-web/`, want `scherm` heeft ze ook nodig |
| visuele tweede lezer | `agents/deck-visual-reviewer.md`, alleen decks | zelfde rol voor `documenten`, `rapport` en `scherm` |
| `requirements.txt` | de kop zegt "dependencies for the sfnl-powerpoint scripts" | rechttrekken, plus wat `word` en `scherm` nodig hebben |
| Word-stramien | bestaat niet | `reference/word-stramien.md` plus `assets/word/` |

## Wat het Word-sjabloon oplevert

Nagemeten op `SFNL_Word_sjabloon.dotx`:

- **A4, 210 × 297 mm**, marges 25,4 mm rondom, zetspiegel 159,1 mm, kopregel en voettekst op
  12,5 mm. `titlePg` staat aan, dus de eerste pagina heeft een eigen kop en voet.
- **Het logo staat twee keer in het bestand**: als PNG van 61,0 × 16,3 mm in `header2`, en als JPG
  van 38,2 × 10,2 mm in `footer2`. Zelfde tekening. Een JPG-logo op wit heeft compressieartefacten
  en geen transparantie; dat hoort de PNG te zijn, en dan kan `image1.jpg` weg.
- **De stijlen staan er compleet in, de inhoud niet.** Het bestand heeft één lege alinea. Het is
  een stijlendrager en geen voorbeeldpagina, dus `word` componeert het document zelf uit de
  stijlen — er is niets om na te tekenen.
- **De typografie**: `Normal` is Lato Light 12 pt. `Title` is Montserrat SemiBold 28 pt met −0,5 pt
  spatiëring, `Subtitle` Montserrat Light 11 pt met +0,75 pt. `Heading 1` is **Gotham Bold** 22 pt,
  `Heading 2` Montserrat Light 18 pt, de rest van de koppen Montserrat Light. Tabelstijl
  `Table Grid1` op 11 pt.
- **`Heading 1` vraagt dus een licentiefont.** Op een SFNL-machine staat Gotham; in een sandbox en
  op de machine van een klant niet, en dan substitueert Word stil. `word` maakt daar een expliciet
  besluit van met Montserrat SemiBold als terugval, in plaats van het aan Word te laten.
- **De themafonts zijn beide Lato Light**, dus Montserrat en Gotham hangen aan de stijlen en niet
  aan het thema. Wie een stijl overschrijft, verliest ze.

## Fasering

Zeven commits, elk zelfstandig opleverbaar. De volgorde is niet vrij: `sfnl-design` mag pas weg
als de twee skills die zijn werk overnemen er zijn, want drie skills wijzen ernaar.

| | wat | afhankelijkheid |
|---|---|---|
| **F1** | Merkfeiten op één plek: `merk.md`, `merk.py`, gegenereerde `merk.css`, de hexwaarden uit vijf scripts en `stijl.css`, de synccheck in preflight, en de Word-afwijking genoteerd | kan nu; verandert geen uitkomst |
| **F2** | `word` bouwen: sjabloon nameten naar `word-stramien.md`, bouwscript, snelroute, brede automatische trigger, de verplichte sluitregel | na F1 |
| **F3** | `affinity`: `sfnl-rapport` naar binnen, eigen maten eruit, de twee stramienen erin, alleen de SDK-laag over | na F1 |
| **F4** | `scherm` bouwen: meegroeiende breedte, donkere modus als vormbesluit, de `dataviz`-skill ingebed in plaats van overschreven, browserrender als beoordeling. Grens hard: één pagina, geen buildstap, geen backend | na F1 |
| **F5** | Intrekken uit de org-sync: `sfnl-design` en `sfnl-html-to-pdf`; de drie "Wat deze skill niet is"-regels omzetten | na F2 én F4 |
| **F6** | `deck-check`: fixer naar binnen, het herhaalde beleid eruit | na F1 |
| **F7** | Hernoemen en 2.0.0: plugin en skills, alle kruisverwijzingen, README, `plugin.json`, `marketplace.json` | laatste |

## Openstaand

- **Welk palet canoniek is** — de vijf hexwaarden van het Word-sjabloon tegen die van de plugin.
  Dit blokkeert F1 niet (de afwijking wordt genoteerd), maar het blijft open tot iemand het
  merkhandboek ernaast legt.
- **Besluit 4** — `deck-check` als eigen bestand, of toch één skill met twee routes.
- **De namen `scherm` en `word`** worden pas hard in F7.
