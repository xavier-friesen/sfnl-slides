# De vormentaal van een SFNL-rapport

De maatstaf. Wat een rapport van tachtig pagina's goed maakt, wat er
gemeten is aan het drukwerk van anderen, en de weigerlijst. De feiten —
maten, klassen, variabelen — staan in `rapport-stramien.md`.

Deze skill doet iets anders dan de twee andere in deze plugin. Daar is de
vorm een compositie per pagina; hier is de vorm een **systeem waar tekst
door loopt**. Dat is geen gradueel verschil. Bij tachtig pagina's kun je
niet meer per pagina beslissen, dus alles wat je vooraf besluit geldt
zestig keer, en alles wat je vergeet gaat zestig keer mis.

En er is een tweede verschil, en dat is het belangrijkste: **de tekst is
niet van ons.** Hij is af, hij is goedgekeurd, en misschien is hij al
door een opdrachtgever vastgesteld. De opmaak mag er niets aan
veranderen. Dat is de grens waar deze skill om heen is gebouwd, en het
is de reden dat `tekstcheck.py` bestaat.

---

## 1. Wat er gemeten is, en wat het opleverde

Drie rapporten zijn nagemeten met een PDF-parser: elke lettergrootte,
elke tekstkolom, elke kleur. Niet om na te doen — een SFNL-rapport is
geen Bain-rapport — maar omdat de keuzes van een goed drukwerk
uitgangspunten zijn die je verdedigen kunt, en een voorkeur niet.

| | Bain, *Global Private Equity Report 2026* | BMC, *Zelfbewust zichtbaar* | McKinsey Global Institute, *Global growth* |
|---|---|---|---|
| bladmaat | US Letter, 216 × 279 mm | A4, 210 × 297 mm | A4, 210 × 297 mm |
| kolommen | één, 470 pt (166 mm) | twee, 233 pt (82 mm), goot 18 pt | één, 403 pt (142 mm), met 113 pt kantlijn links |
| brood | Reckless Neue, schreef, 10 pt | Interstate, 10 pt | Helvetica Neue Light, 9,8 pt |
| tekens per regel | ± 104 | ± 42 | ± 91 |
| letterfamilies | twee: schreef voor brood, Graphik voor exhibits | **één**, in twee gewichten | twee: Helvetica voor brood, Arial in exhibits |
| inkt | zwart, met grijs `#666666` voor secundair | navy `#171846` | zwart, grijs `#808183` |
| accent | rood `#CC0000` | warm zand `#B0A891` | oranje `#EF8400` |
| uitvullen | **nee** | **nee** | **nee** |
| exhibits | "Figure N:" in rood vet, dan de titel, dan het beeld, dan noten en bron | volle breedte, bijschrift vet erboven | haarlijn, "Exhibit N" grijs, titel vet, eenheid grijs, beeld, NOOT, BRON |
| voetnoten | 6,2 pt onderaan | 8 pt onderaan | 7 pt onderaan, achter een haarlijn |
| kopregel | logo plus rapporttitel, gecentreerd bovenaan | haarlijn boven en onder elke pagina | driedelige voet: instituut, rapporttitel, folio |
| folio | midden onder | buitenonder, met de hoofdstuknaam ervoor in het accent | buitenonder rechts |

**Vijf dingen die hieruit volgen en die in `rapport.css` staan.**

1. **Geen van de drie vult zijn lopende tekst uit.** Dat ging tegen de
   verwachting in, want het SFNL-drukwerk vult wél uit. Het verschil zit
   in de maat: SFNL zet zijn kolommen op 32 tot 52 tekens en daar gaat
   uitvullen op; op 90 tot 104 tekens valt het als gaten in de regel.
   Daarom vult in deze skill alleen `dubbel` uit — 48 tekens — en de
   andere modellen niet. En omdat uitvullen zonder afbreking altijd
   gaten geeft, doet `bouw.py` eerst een proef of Chromium een
   Nederlands afbreekwoordenboek heeft, en vervalt het uitvullen als dat
   ontbreekt.
2. **Het exhibit is een blok met vaste onderdelen in vaste volgorde.**
   MGI is daar het strengst in en het meest leesbaar: haarlijn, nummer,
   titel, eenheid, beeld, noot, bron. Die volgorde laat een lezer in
   vier regels beslissen of het beeld hem aangaat. Dat blok is
   overgenomen als `.exhibit`, met de SFNL-kleuren erop.
3. **De accentkleur draagt bij alle drie bijna geen letters.** Bij BMC
   is het zand een lijn en een hoofdstuknaam; bij MGI een run-in kop en
   een pijl in een grafiek; bij Bain een figuurlabel. Nooit een alinea.
   Dat is de reden dat oranje in deze skill een merkteken is en geen inkt
   — zie §4.
4. **Eén letterfamilie is genoeg.** BMC doet het hele rapport in
   Interstate, regular en bold, en het leest als het best ontworpen van
   de drie. SFNL heeft twee families en dat blijft zo, maar het zegt wel
   iets: variatie zit niet in de letter.
5. **De folio hoort aan de buitenkant.** Twee van de drie doen het;
   Bain centreert en dat is meteen de minst boekachtige van de drie.
   Een gebonden rapport wordt aan de buitenrand doorgebladerd.

Wat er níét is overgenomen: het formaat (SFNL houdt 210 × 275 mm, de
maat van de eigen jaarrapporten), de schreefletter van Bain, en de
gecentreerde kopregel.

---

## 2. Waar de lat ligt

Kijk naar `assets/rapport/maatstaf/` voordat je begint. Vier beelden:
het contactblad van een gezet rapport, de omslag, een hoofdstukopener en
een tekstpagina met een exhibit. Ze zijn met deze skill gebouwd, dus wat
je ziet is haalbaar en het is de ondergrens en niet het doel.

En kijk naar de drie keuzekaarten in `assets/rapport/keuzekaarten/`. Die
zijn geen plaatjes bij de vragen — het zijn echt gezette pagina's uit
dezelfde pijplijn, dus ze kunnen niet beloven wat de zetmotor niet doet.

**Wat een rapport goed maakt, in vier zinnen.**

- Een lezer die op pagina 40 opent, weet binnen twee seconden waar hij
  is. Dat doet de kopregel, en die is er dus altijd.
- Een lezer die doorbladert, ziet elke twee tot drie spreads iets anders
  dan een blok tekst. Dat is de enige harde eis aan het ritme, en
  `qa_rapport.py` telt hem als `tekstwand`.
- Twee pagina's die naast elkaar liggen, eindigen op dezelfde hoogte.
  Daarom is de zetspiegel een geheel aantal regels hoog.
- Niets op de pagina is er zonder reden, en elke reden is één van drie:
  het staat in de bron, het is navigatie, of het is een merkteken. Een
  vierde reden bestaat niet.

---

## 3. De weigerlijst

Zeventien dingen die een rapport eruit laten zien alsof een model het
heeft opgemaakt. De eerste vijf zijn de ernstige.

1. **Tekst veranderen om de vorm te laten kloppen.** Een kop inkorten
   omdat hij over drie regels loopt, een alinea splitsen om een figuur
   ertussen te krijgen, een opsommingsteken weghalen om er een echte
   lijst van te maken. Allemaal begrijpelijk, allemaal verboden zonder
   expliciete toestemming per geval. Dit staat bovenaan omdat het de
   enige fout is die de gebruiker niet terugziet: de opmaak ziet er
   beter uit en de tekst is stil anders. Er is één uitzondering en die
   is expliciet gemaakt: het gelijktrekken van verwijzingen telt als
   opmaak en niet als herschrijven — zie §9.
2. **Een citaat, een streamer of een kaderblok dat tekst herhaalt.** Een
   pull quote dubbelt een zin uit de tekst. Dat is een inhoudelijke
   toevoeging, ook al is er geen woord bijgeschreven, en dus vraag je
   erom.
3. **Een samenvatting, een conclusie of een "kernboodschap" die er niet
   stond.** Een rapport zonder samenvatting krijgt er geen. Het model dat
   "rapport" leest, weet dat daar een executive summary hoort, en dat is
   precies de fout.
4. **Een bijschrift verzinnen bij een figuur die er geen had.** Zonder
   bijschrift heeft een figuur geen eenheid en geen bron. Dat is een
   probleem, en het is niet jouw probleem om op te lossen: het gaat als
   voorstel naar de gebruiker.
5. **Een getal, een jaartal of een naam aanvullen.** Ook niet als het
   er duidelijk hoort te staan.
6. **Een lege kolom op elke pagina.** Het kantlijnmodel is prachtig met
   noten en het is een gat zonder. `qa_rapport.py` meet het; boven
   driekwart lege kantlijnen is `breed` het antwoord.
7. **Een kop onderaan een pagina met zijn tekst op de volgende.** De
   zetmotor voorkomt het op drie plekken; ziet u het toch, dan is er iets
   stuk.
8. **Eén losse regel boven- of onderaan een kolom.** Weduwe en wees. De
   zetmotor houdt er twee aan, en dat is niet netjesheid: één regel
   boven een kolom leest als een fout in de vorige.
9. **Een tabel die over een paginagrens breekt zonder zijn kolomnamen.**
   De kop hoort herhaald, en dan is het een toevoeging en die wordt
   gemarkeerd.
10. **Meer dan zeven lettergroottes.** Wie een achtste nodig heeft, heeft
    een compositieprobleem. De ladder staat in `rapport-stramien.md`.
11. **Oranje als inkt.** Oranje op wit haalt contrast 2,58 en dat draagt
    geen regel tekst. Het draagt een streep, een vierkantje, een cijfer
    van twee tekens. Zie §4.
12. **Een watermerkcijfer dat door zijn kader wordt afgesneden.** Half
    achter de titel is een merkteken; afgekapt op de kolomrand is een
    rechthoek.
13. **Een figuur die op een andere pagina staat dan de tekst die ernaar
    verwijst.** Wanneer dat niet te vermijden is, hoort er in de tekst
    een verwijzing te staan — en die staat er alleen als de bron hem
    heeft.
14. **Een inhoudsopgave met paginanummers die niet kloppen.** Ze komen
    uit de zetting en niet uit een schatting; `bouw.py` zet daarom
    meerdere keren en `qa_rapport.py` controleert het achteraf per
    blok-id.
15. **Een beeld onder 150 dpi over de volle breedte.** Op papier zichtbaar
    zacht. Onder 100 dpi is het een fout.
16. **Een rapport opleveren dat niet visueel bekeken is.** Er is geen
    route zonder renderer: zonder browser is er geen zetting.
17. **Een verwijzingsnummer dat nergens naar wijst.** Wie `[3]` in de
    tekst zet, moet een derde regel in de bronnenlijst hebben.
    `citaten.py` laat een verwijzing die hij niet kan koppelen staan
    zoals hij stond en meldt hem apart; die melding negeren is de fout.

---

## 4. Oranje is een merkteken en geen inkt

Dit is het enige punt waarop de skill van het SFNL-drukwerk afwijkt, dus
het staat hier met de meting erbij.

Oranje `#F87F4F` op wit haalt een contrastverhouding van **2,58**. De
drempel voor lopende tekst is 4,5 en voor grote tekst 3,0. Oranje haalt
geen van beide. Navy op oranje haalt 6,4 — daarom staat er in het
drukwerk navy *op* een oranje vlak, en niet oranje *op* wit.

Wat daaruit volgt:

- **Oranje draagt geen zin.** De run-in kop was in de eerste zetting
  oranje, zoals bij MGI, en is nu navy met een oranje vierkantje ervoor.
  De nummers in de inhoudsopgave waren oranje en zijn nu navy.
- **Oranje draagt wel een merkteken**: de streep boven een sectiekop,
  het vierkantje voor een opsommingsregel, het cijfer van een genummerde
  lijst, het streepje bij de folio, het label boven een exhibit, de
  kicker boven een hoofdstuktitel. Dat zijn tekens die je moet kunnen
  *vinden*, niet lezen.
- `qa_rapport.py` telt die tekens apart als `accentmerken`, met hun
  contrastwaarde erbij. Ze blokkeren niet en ze verdwijnen niet uit het
  verslag. Zo blijft het een keuze in plaats van een ongeluk.
- **Het oranje wordt niet donkerder gemaakt tot het haalt.** Een oranje
  dat 4,5 haalt op wit zit rond `#A6421C` en dat is een andere kleur.

Voor het `zacht`-register geldt hetzelfde met emerald, dat op wit nog
lager uitkomt.

---

## 5. Wat de opmaak mag toevoegen

Elf dingen, en ze dragen alle elf `data-toevoeging` in de markup zodat
`tekstcheck.py` ze kan onderscheiden van brontekst. De laatste vier
verschijnen alleen wanneer de bijbehorende keuze in `ontwerp.json` staat.

| toevoeging | wat | waarom het mag |
|---|---|---|
| `folio` | het paginanummer | navigatie; zonder is een rapport van tachtig pagina's onbruikbaar |
| `kopregel` | rapporttitel op de verso, hoofdstuknaam op de recto | navigatie |
| `inhoudsopgave` | de regels van de inhoudsopgave | navigatie; de tekst is een letterlijke kopie van de koppen |
| `nummer` | "Hoofdstuk 3", het watermerkcijfer, "Figuur 7" | nummering die uit de structuur volgt |
| `nootnummer` | het cijfer bij een voetnootverwijzing en voor de noot | de noten stonden al in de bron; alleen het cijfer is nieuw |
| `tabelkop` | de herhaalde kolomnamen op een vervolgtabel | zonder is de vervolgtabel onleesbaar |
| `omslag` | opdrachtgever, datum, ondertitel op de omslag | alleen als de gebruiker ze in `ontwerp.json` heeft opgegeven |
| `notenkop` | "Noten" boven een blok eindnoten | een reeks genummerde regels zonder kop is geen blok |
| `bronnummer` | `[3]` vóór een bronregel bij genummerd citeren | het nummer volgt uit de citatievolgorde in de tekst |
| `scheiding` | het woord "Bijlagen" op het scheidingsblad | alleen wanneer de bron zelf geen zo'n kop heeft — heeft hij die wel, dan is het gewoon brontekst |
| `beeldbijschrift` | het bijschrift bij een apart aangeleverd beeld | de gebruiker heeft het zelf geschreven; het staat niet in het rapport |

Alles wat hier niet in staat en geen `data-bron` heeft, is tekst die
niemand heeft goedgekeurd. `tekstcheck.py` noemt dat
`ongemarkeerd_toegevoegd`, schrijft het uit, en **blokkeert de
oplevering**. Op alle vier de modellen van het proefrapport is dat getal
nul, dus het is een drempel die je alleen raakt als er echt iets bij is
geschreven.

---

## 6. Het model kiezen, en waarom het meestal `breed` is

Vier modellen, en de keuze hangt aan twee dingen: hoe lang het rapport is
en of het noten heeft.

- **`breed`** — één kolom van 537 px, brood op 11/16,5 pt, 77 tekens (gemeten).
  De default, en de veiligste keuze voor een aangeleverde tekst waarvan
  je de structuur nog niet kent: het heeft nooit een lege kolom, nooit
  een figuur die niet past, en het leest op een scherm net zo goed als
  op papier. Dit is de maat van een Bain-rapport, iets smaller gezet.
- **`kantlijn`** — één kolom van 480 px plus een kantlijn van 140.
  Kies dit alléén als het rapport noten, bronnen of kanttekeningen
  heeft, want die vullen de kantlijn. Voetnoten gaan daar naartoe in
  plaats van naar de voet, en dan staat een noot naast de regel waar hij
  bij hoort. Zonder noten is dit `breed` met 170 px wit ernaast.
- **`dubbel`** — twee kolommen van 310 px, 48 tekens (gemeten). De maat van het
  SFNL-drukwerk zelf en de dichtste zetting van de vier: hetzelfde
  rapport is hier ongeveer 40 procent korter dan in `breed`. Kies het
  voor een lang, feitelijk rapport, en voor drukwerk. Het enige model dat
  uitvult, en dus het enige dat een afbreekwoordenboek nodig heeft.
- **`flexibel`** — `kantlijn` als basis, met per sectie de mogelijkheid
  naar `dubbel` of naar de volle breedte te gaan. Eén broodmaat voor het
  hele rapport, want een hoofdstuk op 11 pt naast een hoofdstuk op 10 pt
  leest als twee rapporten. Kies dit voor een rapport dat uit
  ongelijksoortige delen bestaat — een analyse met een bijlage vol
  tabellen.

**Wat het model níét bepaalt** is de kleur, de opener of het formaat. Dat
zijn drie eigen besluiten en ze hangen niet aan het model.

---

## 7. Het register kiezen

Eén register per rapport, en het verschil zit vooral in hoe een hoofdstuk
opent.

- **`helder`** — wit, navy, oranje accent. De default en het enige
  register dat tachtig pagina's volhoudt zonder te gaan schreeuwen.
- **`diep`** — dezelfde tekstpagina's, hoofdstukken op een heel navy
  blad. Kost een pagina per hoofdstuk en geeft er ritme voor terug. Pas
  vanaf veertig pagina's, want onder dat aantal is een pagina te duur.
- **`zacht`** — emerald in plaats van oranje, mint als tint. Voor een
  onderzoeksrapport of een evaluatie: minder nadruk, meer rust. Oranje
  blijft over voor de folio, zodat het merk niet verdwijnt.
- **`contrast`** — violet als hoofdaccent, oranje als tweede. Het
  register van de casespread Civitates, en het enige waarin twee accenten
  naast elkaar staan. Voor een rapport dat uit cases bestaat die van
  elkaar moeten verschillen.

**Het register bepaalt de kleur van de hoofdstukband, niet de
compositie.** Die is in alle vier hetzelfde: het tekstblok hangt
linksonder in het veld, de tonale bol bleedt linksboven half buiten het
blad, en het hoofdstukcijfer staat rechtsonder. Zie
`rapport-stramien.md` §7 voor de maten en de herkomst van elk onderdeel.
De bol is daar het stuk dat het werk doet — een band zonder is een
kleurvlak met tekst in de hoek, en dat leest als een onafgemaakt
ontwerp.

---

## 8. Beeld

Beeld is niet verplicht en het wordt niet verzonnen. Wat er is, komt uit
het brondocument; wat er niet is, blijft er niet.

- **De plek volgt de bron.** Een figuur staat waar hij in het
  Word-document stond, want dat is de plek waar de schrijver hem heeft
  bedoeld. De opmaak verplaatst hem alleen als hij niet past, en dan naar
  de eerstvolgende plek waar hij wél past.
- **Een figuur met een bijschrift wordt een exhibit**, met een nummer,
  een titel en de bronregel. Zonder bijschrift wordt het een beeldblok
  zonder nummer, want een genummerde figuur zonder titel is een cijfer
  zonder betekenis.
- **Een figuur breekt nooit over een paginagrens.** `break-inside:
  avoid`, en dat kost soms een halve pagina wit. Dat is de goede prijs.
- **De resolutie wordt gemeten.** Een beeld van 650 px over de volle
  zetspiegel komt op 96 dpi op papier. Onder 150 is het zichtbaar zacht
  en dat gaat als aanwijzing mee bij de oplevering; onder 100 is het een
  fout en dan vraag je een beter bestand.
- **Een lege plek is zichtbaar leeg.** Hoort er beeld te komen dat er nog
  niet is, dan staat er een gemarkeerd vlak en geen wit.

**En de vraag wordt gesteld, ook als het antwoord voor de hand ligt.**
`beeld` in `ontwerp.json` kent drie standen, en er is geen stand waarin
de skill zelf beslist wat er te zien is:

| | wat er gebeurt |
|---|---|
| `geen` | tekst en tabellen, verder niets — ook wanneer er beeld in het Word-document zat. Dat is een keuze en wordt als zodanig gemeld |
| `uit-bron` | wat in het document stond, op de plek waar het stond. De default zodra `lees_docx.py` beeld heeft uitgepakt |
| `aangeleverd` | de gebruiker wijst bestanden aan, en zegt erbij waar ze horen |

Bij `aangeleverd` hoort een `beeld.json` naast het rapport: per beeld het
bestand, het blok waarachter het moet komen, en een bijschrift als de
gebruiker er een heeft. Zonder die koppeling is er geen plaatsing — een
map met foto's is geen opdracht, want de skill weet niet welke foto bij
welke alinea hoort en gokken is hier hetzelfde als verzinnen. Het
bijschrift dat de gebruiker meelevert is de enige bijschrifttekst die
niet uit het rapport komt, en draagt daarom `data-toevoeging`.

---

## 9. Het verwijzingsapparaat

Een rapport dat citeert, doet dat op twee plekken tegelijk: kort in de
lopende tekst en volledig ergens anders. Dat zijn **twee besluiten die
los van elkaar staan**, en ze in één lijstje gooien is de fout die deze
skill eerst maakte. Voetnoten *en* een bronnenlijst achterin is de
gewoonste combinatie die er is; als je moet kiezen tussen die twee, is de
vraag verkeerd gesteld.

**Besluit één: waar de noten staan** (`noten` in `ontwerp.json`).

| | wat het doet | waarvoor |
|---|---|---|
| `geen` | de noten uit de bron worden niet gezet | alleen wanneer de gebruiker dat vraagt; het is het enige apparaat dat brontekst laat vervallen en het wordt dus expliciet gemeld |
| `voetnoot` | onder aan de pagina waar de verwijzing staat, of in de kantlijn bij het model `kantlijn` | de default, en de enige vorm waarbij de lezer de noot leest zonder de vinger ergens in te houden |
| `eindnoot-hoofdstuk` | een blok aan het eind van elk hoofdstuk | veel noten, of lange noten; het houdt de tekstpagina rustig zonder de noot onvindbaar te maken |
| `eindnoot-rapport` | één blok achterin | de academische vorm; kies het voor een rapport dat als geheel wordt geciteerd |

**Besluit twee: of de bronnenlijst wordt opgemaakt** (`bronnenlijst`).
Alleen aan te bieden wanneer de bron er een heeft: `lees_docx.py` zoekt
naar een kop als "Literatuur" of "Bronnen" en legt de regels ertussen
vast in `apparaat.bronnenlijst`. Zonder die kop is er geen keuze, want
een bronnenlijst maken betekent bronregels schrijven.

| | wat het doet |
|---|---|
| `geen` | de regels blijven staan waar ze staan, als gewone alinea's |
| `apa` | hangende inspringing van 1,7 em, op alfabet zoals aangeleverd |
| `genummerd` | `[1]`, `[2]` … op citatievolgorde, met dezelfde hangende inspringing |

**En dan de citatiestijl** (`citaatstijl`). Dit is het enige punt waar de
skill de tekst van de gebruiker aanraakt zonder per geval te vragen, en
dat is een besluit van de opdrachtgever geweest: *een verwijzing
gelijktrekken is opmaak, geen herschrijven.* De prijs die daarbij hoort
is betaald in het systeem zelf:

- `citaten.py` rekent de omzetting uit **voordat** er iets gebeurt en
  schrijft hem weg in `citaten.json` — welk blok, wat er stond, wat er
  komt te staan, en naar welke bronregel het wijst.
- `tekstcheck.py` speelt dat plan terug tegen de brontekst. Klopt een
  blok pas ná het toepassen van de omzettingen die ervoor gepland waren,
  dan heet het `omgezet` en gaat het door; klopt het dan nog niet, dan is
  het `gewijzigd` en **blokkeert het de oplevering**. Een omzetting die
  meer aanraakt dan hij mocht, komt er dus niet doorheen.
- Bij de oplevering staan ze allemaal in het verslag. Wat er verandert
  blijft zichtbaar; het gaat alleen niet meer per geval langs de
  gebruiker.

Drie stijlen: `zoals-aangeleverd` (de default, er verandert niets),
`uniform` (`e.a.` en `et. al.` worden `et al.`, en er komt een komma voor
het jaartal) en `genummerd` (`[3]`, alleen mogelijk mét bronnenlijst,
want het nummer moet ergens naar wijzen).

**Twee dingen die er bewust niet in zitten**, allebei omdat ze op de
proef een fout opleverden die je pas ziet als je de bron ernaast legt:

1. **`en` wordt geen `&`.** Het lijkt dezelfde ingreep en is het niet: in
   een verwijzing naar het "Ministerie van Sociale Zaken en
   Werkgelegenheid" hoort dat `en` bij de naam. De eerste versie van de
   regel maakte daar "Sociale Zaken & Werkgelegenheid" van — een
   organisatie die niet bestaat. Aan de tekst is niet te zien of een `en`
   twee auteurs scheidt of in een naam staat, dus blijft hij staan.
2. **Auteur-jaar wordt geen voetnootverwijzing.** Dat vraagt een
   noottekst per verwijzing, en die zou uit de bronregel gemaakt moeten
   worden. Dan staat dezelfde regel twee keer in het rapport en is er
   tekst bij geschreven. Wie dat effect wil, kiest `noten: voetnoot` met
   een bronnenlijst erbij: hetzelfde resultaat zonder nieuwe tekst.

En de faalwijze is expres saai: **een verwijzing die niet aan een
bronregel te koppelen is, blijft staan zoals hij stond** en wordt gemeld.
Liever één verwijzing die uit de toon valt dan een nummer dat nergens
naar wijst.

---

## 10. De dichtheid

Hoeveel er op een pagina mag. Drie standen, en het is een knop en geen
grens: de zetmotor houdt zich in alle drie aan dezelfde regels voor
weduwen, wezen en koppen — de dichtheid verschuift alleen waar de ruimte
vandaan komt.

| | regels zetspiegel | lucht tussen blokken | gemeten op het proefrapport |
|---|---|---|---|
| `ruim` | 47 | 3 × | 39 pagina's, 284 woorden per tekstpagina |
| `gemiddeld` | 50 | 2 × | 35 pagina's, 295 woorden per tekstpagina |
| `dicht` | 53 | 1,5 × | 35 pagina's, 318 woorden per tekstpagina |

Drie dingen die daar in staan en die het besluit dragen:

- **De letter verandert niet.** De dichtheid verandert het aantal regels
  in de zetspiegel en de lucht tussen de blokken, en verder niets. De
  zeven lettergroottes blijven zeven, en `ruim` en `dicht` zijn
  herkenbaar hetzelfde rapport.
- **Het verschil is kleiner dan het klinkt** — 34 woorden per pagina
  tussen de uitersten, ongeveer 12 procent. Wie een rapport substantieel
  korter wil, verandert het model (`dubbel` is 40 procent korter dan
  `breed`) en niet de dichtheid.
- **`dicht` levert niet altijd pagina's op.** Op de proef zijn
  `gemiddeld` en `dicht` allebei 35 pagina's, omdat de winst opgaat aan
  hoofdstukopeners en beeld dat niet meeschaalt. Dichter zetten is een
  keuze over hoe de bladspiegel oogt, niet een manier om te bezuinigen.

De default is `gemiddeld`. `ruim` is de goede keuze voor een rapport dat
op scherm gelezen wordt of dat veel koppen heeft; `dicht` voor een lang
en feitelijk stuk waar de lezer doorheen werkt.

---

## 11. De bijlagen

Een bijlage is geen hoofdstuk, en het rapport hoort dat te laten zien op
het moment dat je erin belandt.

- **Er komt een scheidingsblad**, met dezelfde compositie als een
  hoofdstukopener maar zonder cijfer: een streep, het woord "Bijlagen",
  en het veld van het register. Dat is de hele functie — de lezer die
  doorbladert weet dat het lopende betoog voorbij is.
- **Staat het woord al in de bron** — een kop die alleen "Bijlagen" of
  "Appendices" is — dan ís die kop het scheidingsblad en wordt er niets
  toegevoegd. Staat er meteen "Bijlage A: verantwoording", dan is dat de
  eerste bijlage en krijgt het scheidingsblad het woord als
  `data-toevoeging="scheiding"`.
- **Bijlagen tellen op letter**, A, B, C, en niet verder op het
  hoofdstuknummer. Een rapport met vijf hoofdstukken en drie bijlagen
  heeft geen hoofdstuk 8.
- **De folio loopt door.** Een bijlage is achterin, niet ernaast; de
  paginanummering breekt niet af en begint niet opnieuw.
- **In de inhoudsopgave staan ze onder een eigen groepskop**, met dezelfde
  witruimte ervoor als een hoofdstuk krijgt. Ze staan er wél in: een
  bijlage die je alleen vindt door te bladeren is een bijlage die niemand
  leest.

---

## 12. Wat er blijft liggen

Deze skill zet een aangeleverd rapport op. Wat hij niet doet:

- **Niet schrijven.** Is de tekst nog niet af, dan is schrijven de
  opdracht — dat is `sfnl-rapporttekst` of `sfnl-writer`.
- **Niet redigeren.** Een tekst korter en scherper maken is
  `sfnl-tekst-scherpen`.
- **Geen infographics ontwerpen.** Een figuur die uitgerekend moet
  worden, is `sfnl-infographic`, en die levert SVG die hier in een
  exhibit past.
- **Geen Affinity.** Moet het rapport in Affinity worden opgemaakt, dan
  is dat `sfnl-rapport`.
- **Geen kort drukwerk.** Een uitnodiging, een one-pager, een executive
  summary van vier pagina's: dat componeer je per pagina en dat is
  `sfnl-design-documents`.
- **Geen Word terug.** De oplevering is HTML en PDF. Een rapport dat de
  klant zelf verder typt, is een ander product.
