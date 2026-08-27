---
name: sfnl-deck-check
description: >
  Controleer en schoon een bestaande PowerPoint van Social Finance NL op: tekst,
  interpunctie, spelling, consistentie en huisstijl, en lever een opgeschoond .pptx
  met een wijzigingslogboek op. Gebruik deze skill wanneer er een .pptx wordt
  aangeleverd of wanneer de gebruiker vraagt "check dit deck", "schoon deze
  presentatie op", "kijk of dit klopt", "fix dit deck", "review deze presentatie",
  "opmaak nakijken", "spelling in de slides", "consistentie", "klopt de huisstijl
  hier", of iets met SFNL of Social Finance NL combineert met nakijken, controleren,
  opschonen of corrigeren. Ook bij een deck dat niet uit het SFNL-sjabloon komt.
  **Niet** voor het maken van een deck: "maak een presentatie", "bouw een deck",
  "nieuwe slides" en "voeg een slide toe" gaan naar de skill `sfnl-slides`, die een deck
  uit het sjabloon bouwt. Deze skill verandert tekst en meldt vorm; hij ontwerpt niets.
---

# Deck-check

Een deck dat er al is, nakijken en opschonen. De tekst wordt opgeschoond volgens regels die
mechanisch vast te stellen zijn; alles wat een oordeel vraagt wordt gemeld en niet gewijzigd.

Er is dus een harde grens door deze skill heen, en die is het hele ontwerp: **tekst wijzig je,
vorm meld je.** Een dubbele spatie is een fout die niemand hoeft te bevestigen. Een kaart die
één regel te vol staat is een compositiebesluit, en dat neemt een mens op de render. Wie die
grens laat verschuiven, levert een deck op waarin de vormgeving stil is veranderd en de
gebruiker niet meer weet waar hij naar kijkt.

Twee bestanden gaan er altijd uit: het opgeschoonde `.pptx` en het wijzigingslogboek als CSV.
Ook als er niets veranderd is — dan is de lege lijst de uitkomst.

## Voordat je begint

**Alle paden in dit document staan vanaf de plugin-map**, dus vanaf `${CLAUDE_PLUGIN_ROOT}` —
niet vanaf de map waarin dit bestand staat en niet vanaf het project. `reference/voice.md` is
dus `${CLAUDE_PLUGIN_ROOT}/reference/voice.md`, en `scripts/deckcheck/plan.py` is
`${CLAUDE_PLUGIN_ROOT}/scripts/deckcheck/plan.py`. Dat is een keer misgegaan: een agent die de
leeslijst vanaf de skillmap probeerde te openen, vond geen van de documenten en moest de repo
doorzoeken voordat hij kon beginnen.

Lees, in deze volgorde, en één keer voor de hele deck:

1. `reference/voice.md` — de taal op de slide. Titels in kapitalen zonder punt en zonder
   uitroepteken, de subtitel in zinsvorm en niet in kapitalen, typografische apostrofs en
   aanhalingstekens, het euroteken in plaats van EUR, de eenheid bij het getal. Dit is het
   beleid dat de opschoning uitvoert; het staat daar en wordt hier niet herhaald.
2. `reference/vormentaal.md` §9 (Zetting) — eindinterpunctie, slashspatiëring, het en-streepje,
   regelafstand, insets, `noAutofit`, één familie per regel. Daarnaast §2 (de vier maten), §7
   (uitlijning) en §8 (lijnwerk, één kaarttaal) voor de vlaggen die je gaat lezen.
3. `reference/merk.md` — het merkcontract: de kleuren met hun hex, de letterfamilies, het logo,
   en de weigerlijst die in elk medium geldt. Hier staat waarom een harde hex op een slide een
   fout is en waarom lopende tekst nooit puur zwart is.
4. `reference/sjabloon.md` — welke placeholder waar staat, de kleurslots, en de valkuilen die
   stil misgaan (Calibri, `srgbClr`, autofit, idx-volgorde).
5. De docstring van `scripts/deckcheck/tekstregels.py` — de tekstregels zoals ze werkelijk
   worden uitgevoerd, met de beschermingslaag ervoor.

Draai daarna één keer:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py"
```

Dat zegt of er een interpreter, de Python-afhankelijkheden en een renderer zijn. **Zonder
renderer kun je de tekst opschonen maar de vorm niet beoordelen**, en dan zeg je dat bij de
oplevering met zoveel woorden — zie **Zonder renderer** onderaan.

`$S` hieronder is `${CLAUDE_PLUGIN_ROOT}/scripts`.

## Stap 1 — Het bestand vinden, en dit is de poort

Vóór alles: welk bestand controleer je? Een deck komt langs drie oppervlakken binnen en staat op
elk op een andere plek.

```bash
python $S/deckcheck/vind.py --map .
```

De JSON geeft `pad` en `bron`, of `kandidaten` met de vraag die je moet stellen. Drie regels:

- **Is `pad` gevuld, dan vraag je niets.** Het bestand is er al; om een upload vragen die er
  ligt is de fout waar deze stap voor bestaat.
- Staan er meerdere kandidaten, dan stel je **één** korte vraag: welke moet ik controleren?
- Is er niets, dan stel je de vraag die in `vraag` staat. Die verschilt per oppervlak: in de
  PowerPoint-plugin is "sleep het bestand hierheen" geen bruikbaar antwoord, en dan vraag je de
  gebruiker het bestand op te slaan of met Opslaan als een kopie te maken.

Werk daarna op een **kopie**. Het aangeleverde bestand blijft zoals het was; het opgeschoonde
deck is een nieuw bestand met een eigen naam.

## Stap 2 — PLAN: lezen, en niets schrijven

```bash
python $S/deckcheck/plan.py <deck.pptx> --json plan.json
```

Dit leest de hele deck en levert één plan op: per alinea de tekst zoals hij is, de tekst zoals
hij wordt, de regels die dat verklaren, en daarnaast alle vlaggen die géén tekstwijziging zijn.
Er wordt niets geschreven. Lees de JSON; hij is de agenda voor de rest van de route.

Waarom lezen en schrijven gescheiden zijn: wie tijdens het lezen al schrijft, ziet de deckbrede
uitkomsten — de meerderheidstaal, de uitlijning per rol, de terminologie, de eindinterpunctie —
pas nadat de eerste tien slides al veranderd zijn. Dan gelden er twee regimes in één bestand.

### Wat er wordt gelezen

Alle bewerkbare tekst: vormen, placeholders, groepen (recursief), tabelcellen, en de titel van
een grafiek waar die via het tekstmodel te bereiken is. Tekst in een afbeelding, een screenshot
of een niet-bewerkbare grafiekrender wordt niet aangeraakt en niet nagekeken — een grafiek
zonder bereikbare titel krijgt de vlag `grafiektekst-niet-bewerkbaar`, zodat het gat benoemd is
in plaats van stil.

### De roldetectie

Elk element krijgt een rol, want de regels verschillen per rol. Twee passes:

- **Titel en subtitel** op placeholdertype. Is er geen subtitelplaceholder — een deck dat niet
  uit het SFNL-sjabloon komt — dan geldt de heuristiek: een korte, brede regel direct onder de
  titel in de bovenste 35 procent van de slide, van ten hoogste 120 tekens.
- **Body** is al het andere, inclusief alles onder de onderkant van de subtitel.

In het SFNL-sjabloon is de titel idx 0 en de subtitel idx 1 (`reference/sjabloon.md`), dus de
heuristiek slaat daar vrijwel nooit aan. Hij staat er voor decks van buiten.

### De beschermingslaag: Do Not Touch

Vóór elke regel gaat deze laag. Wat hier onder valt, gaat ongewijzigd door:

- URL's (met `://` of beginnend met `www.`) en e-mailadressen
- breuken en verhoudingen als `3/4`, en eenheden als `km/u`
- getallen, bedragen, percentages, datums en duizendtal- en decimaalscheiders
- bestandsnamen en formule- of codeachtige tokens (`>=`, `==`, `++`)

Is een alinea vrijwel helemaal beschermd, dan krijgt hij **alleen** witruimteopschoning. Zonder
deze laag maakt de interpunctieregel iets anders van `www.socfin.nl/cases` en zet de slashregel
spaties in `3/4`.

### De tekstregels

Deze regels voert `plan.py` uit via `tekstregels.py`. Ze staan hier zodat je weet wat er
gebeurt; je typt ze niet zelf na.

1. **Eindinterpunctie.** Een titel en een subtitel eindigen niet op een punt of een komma
   (`voice.md`); een lijstitem eindigt zonder punt (`vormentaal.md` §9). Er gaat ten hoogste
   één teken af. Een vraagteken blijft staan, een ellips blijft staan, en een afkorting met
   punten (`o.a.`, `U.S.`) wordt nooit afgeknipt. Een uitroepteken in een titel wordt **gemeld
   en niet weggehaald**: `voice.md` verbiedt hem, maar de reparatie is de titel herschrijven en
   dat is geen opschoning.
   Een losse regel zonder bullets — een label, een cel, een regel in een kaart — wordt níet
   gecorrigeerd maar geteld: staat de deck er deels mét en deels zonder punt, dan komt de
   minderheid als `eindinterpunctie-inconsistent` naar boven. Welke van de twee de deck
   aanhoudt is een keuze; één van de twee is de regel.
2. **Slashspatiëring.** Een slash die twee begrippen scheidt krijgt een spatie aan beide
   zijden: `zorg / welzijn`. Een samentrekking (`en/of`), een breuk, een eenheid en een pad
   houden hun slash zonder spaties.
3. **Dubbele spaties** worden één spatie. Een harde ruimte naast een gewone spatie gaat eruit;
   een lósse harde ruimte blijft staan, want die houdt de eenheid bij het getal (`voice.md`).
   Witruimte aan het eind van een alinea gaat eruit.
4. **Interpunctiespatiëring.** Geen spatie vóór `,` `.` `;` `:` `!` `?`; één spatie ná `,` `;`
   `:` `!` `?` wanneer er een woord volgt; geen zwerfspatie binnen haakjes.
5. **Kapitalisatie.** De titel gaat naar kapitalen (`voice.md`), behalve wat beschermd is en
   in kapitalen van betekenis verandert: een URL, een e-mailadres, een bestandsnaam. De
   **subtitel gaat juist níet** naar kapitalen — hij staat in zinsvorm met een hoofdletter aan
   het begin. Een subtitel die wél in kapitalen staat wordt gemeld en niet omgezet:
   terugzetten naar zinsvorm raadt naar de eigennamen die erin staan.
6. **Bullets en nummering.** De niveaus blijven zoals ze zijn en er wordt geen bulletteken
   overschreven. Wat er wél komt is een vlag: `bullet-glyph-inconsistent` (de deck gebruikt
   meer dan één teken), `bullet-parallellie` (de items beginnen deels met een hoofdletter),
   `bullet-niveau-sprong`, `enkel-lijstitem`, en `handmatige-nummering-gemeld` of
   `handmatige-bullet-gemeld` voor een `1.` of een `-` die iemand zelf heeft getypt.
   **Waarom hier niet gecorrigeerd wordt:** een bulletteken op de slide overschrijft de layout,
   en dan is layout-first opgegeven voor één teken. Handgetypte nummers herstel je met
   `set_text.py` en `"num": true`, en dat is een bouwstap.
7. **Aanhalingstekens en streepjes.** Een rechte apostrof binnen een woord wordt `’`
   (`risico’s`); een recht aanhalingsteken om een citaat wordt **gemeld**, want er een
   typografisch paar van maken kan aan de verkeerde kant landen. Een reeks krijgt een
   en-streepje (`2023–2025`), een dubbel koppelteken wordt een en-streepje, gestapelde
   interpunctie (`..`, `??`) wordt één teken, en drie punten worden één ellips.
8. **Spelling en lichte grammatica**, per taal, uit een kleine gecureerde lijst. Nederlands en
   Engels; er wordt **nooit vertaald**. Een direct verdubbeld woord van vier letters of meer
   gaat eruit; korter dan dat wordt gemeld, want `dat dat` en `heel heel` kunnen kloppen.
   De lijst is met opzet klein: een spellingcontrole die alles nakijkt, corrigeert ook
   projectnamen en jargon, en dan verandert er tekst waar niemand om vroeg.

### De vlaggen die geen tekst raken

Ze staan alle in de JSON en in de CSV, en geen ervan blokkeert:

- `mogelijke-overloop` — de tekst meet meer dan zijn vak, gemeten met `hoogte_van()` uit
  `shapes.py`. Een schatting: kijk ernaar op de render. De reparatie is korter schrijven of een
  groter vak, nooit een kleiner font (`vormentaal.md` §9). Titels gaan hier niet langs; die
  hebben een echte meting met het huisstijlfont in `fit_title.py --check`.
- `positie-afwijkend-[rol]` — een placeholder staat meer dan 0,08 in van de plek waar dezelfde
  placeholder in de layout staat. Melden, niet verplaatsen: iemand kan hem met een reden hebben
  verschoven, en het gaat mis zodra je de titelrij van een deck automatisch gelijktrekt.
- `uitlijning-afwijkend-[rol]` — binnen één rol staat de uitlijning niet overal gelijk. Melden;
  uitlijning is een compositiebesluit (`vormentaal.md` §7). Tabelcellen tellen niet mee, want
  daar is uitlijning per kolom juist wél een besluit.
- `regelafstand-extreem` en `alinearuimte-afwijkend` — zetting die niet uit een besluit komt
  maar uit een kopieerslag. De norm staat in `vormentaal.md` §9.
- `gemengde-taal` — minstens een kwart van de tekst op één slide staat in de andere taal.
- `termconsistentie` — dezelfde term in meer dan één schrijfwijze over de deck.
- `formaat-euroteken`, `formaat-procent`, `formaat-decimaal`, `formaat-duizendtal` — de
  getalconventies van `voice.md` die niet worden aangehouden.
- `niet-lopende-zin-gemeld` — de regel eindigt op een voegwoord, of draagt een verdubbeling of
  gestapelde interpunctie. Een heuristiek, dus lees hem zelf na.
- `geen-titel` — een contentslide zonder titel: de bewering van de slide staat nergens. Let op:
  een ontbrekende **subtitel** is nooit een bevinding (`voice.md`, Subtitels zijn optioneel), en
  je meldt hem dus ook niet.
- `restplaceholder` — een `{{MARKER}}` die nooit gevuld is. De tekstregels gaan er niet over
  heen: `{{SUBTITEL}}` kapitaliseren levert een bevinding op over tekst die weg hoort. De
  reparatie is vullen of `clean.py`, en `qa_text.py` meldt hem als `critical`.
- `open-opmerking` en `presentatienotitie-aanwezig` — wat er in het bestand staat en niet op de
  slide. Opgeloste opmerkingen komen alleen in de samenvatting.

### Wat je hier níet zelf gaat nakijken

Deze vier scripts doen het al, en ze zijn de andere helft van de controle. Draai ze op het
áángeleverde deck, zodat je weet wat je aantreft:

```bash
python $S/qa_text.py <deck.pptx>
python $S/qa_tellingen.py <deck.pptx>
python $S/inspect_deck.py <deck.pptx>
python $S/office/unpack.py <deck.pptx> werk      # fit_title werkt op de boom
python $S/fit_title.py werk --check
```

- `qa_text.py` — restplaceholders, `{{MARKER}}`, sjabloonprompts, Calibri en andere off-brand
  fonts, een harde hex in plaats van `schemeClr`, autofit die stil verkleint, een titel in
  onderkast, een lege slide, de drager buiten zijn band of op te veel slides.
- `qa_tellingen.py` — meer dan één maat per rol, twee letterfamilies in dezelfde alinea, de hoge
  punt als scheiding, bandfrequentie, nul exhibits in een deck met cijfers, woorden per slide.
- `fit_title.py --check` — passen de titels met het echte Gotham Bold, en klopt de titelmodus.
  Dit werkt op de uitgepakte boom, dus `office/unpack.py` eerst.
- `inspect_deck.py` — wat de deck doet: layouts, composities, vormnamen, fonts, taal.

Neem hun bevindingen mee in dezelfde oplevering. Wat een `critical` uit `qa_text.py` is, is ook
hier een blokkade — zie **Wat blokkeert**.

## Stap 3 — GLOBAL: wat alleen deckbreed te beslissen is

`plan.py` doet dit in dezelfde run, en het staat hier apart omdat je de uitkomsten moet lezen
voordat je iets toepast:

- **de meerderheidstaal** van de deck, waarnaar elementen gaan waarvan de taal niet vast te
  stellen is. Klopt die niet, dan overrule je hem met `--taal nl` of `--taal en` en draai je
  `plan.py` opnieuw. Doe dat voordat je toepast, niet erna.
- **de eindinterpunctie op losse regels**: de meerderheid bepaalt wat de deck aanhoudt en de
  minderheid wordt gemeld.
- **de uitlijning per rol**, de **terminologie** en de **getalformaten** over de hele deck.

## Stap 4 — APPLY: één keer schrijven

```bash
python $S/deckcheck/toepassen.py <deck.pptx> --plan plan.json \
    --uit opgeschoond.pptx --logboek wijzigingen.csv
```

Dit is de enige stap die schrijft, en hij schrijft alleen wat in het plan staat. Per adres wordt
de tekst van één run vervangen, dus vet, cursief, onderstreping, maat, kleur en font blijven
staan: er wordt geen alinea opnieuw opgebouwd. Dat is precies de fout die een fixer maakt — de
alinea herbouwen en de opmaak van de tweede helft van de zin verliezen.

Wil je eerst alleen zien wat er zou gebeuren, dan is dat `--alleen-logboek`: dan komt er een CSV
en geen nieuw deck.

Lees daarna de JSON die eruit komt:

- `toegepast` is het aantal alinea's dat is gewijzigd.
- `mislukt` moet leeg zijn. Staat er iets in — een vorm die niet meer te vinden is, of tekst die
  inmiddels anders is — dan is het plan verouderd: draai `plan.py` opnieuw en pas opnieuw toe.
- `beeld` vergelijkt de grafieken en tabellen vóór en na het opslaan. `python-pptx` herschrijft
  het pakket bij opslaan, en dat is de plek waar in deze repo eerder grafieken verdwenen
  (`reference/sjabloon.md`, de procesval onderaan). Klopt het niet, dan lever je niet op.

Controleer het resultaat daarna nog één keer met `qa_text.py`. Wat de opschoning heeft
gerepareerd, hoort daar weg te zijn.

## Stap 5 — Kijken wat geen script ziet

De tekst is nu schoon. De vorm is nog niet beoordeeld, en dat is een aparte stap:

```bash
python $S/render.py opgeschoond.pptx png
python $S/thumbnail.py png raster-1 --cols 4
```

Kijk zelf eerst naar het contactblad en open op volle grootte alleen wat er verkeerd uitziet.
Zet daarna de `deck-visual-reviewer` op diezelfde renders, met het pad erbij zodat hij niet
opnieuw rendert. Render naar een pad waar hij bij kan — een subagent leest alleen binnen de
aangesloten mappen, en renders in een tempmap van de shell zijn voor hem onzichtbaar.

Wat je op de render nakijkt zijn de vlaggen uit stap 2 die over vorm gaan (overloop, positie,
uitlijning, zetting) plus wat geen vlag heeft: overlap, dood wit, kleur die niets codeert,
eenvormigheid over de deck.

**En hier repareer je niets zonder te vragen.** Zie je een compositie die anders moet, dan is
dat een herbouw en geen opschoning: meld het, met de slide erbij en wat er zou moeten gebeuren,
en laat de gebruiker kiezen. Zegt hij ja, dan is `sfnl-slides` aan zet — die skill bouwt de
contentzone en kent de vormentaal die erbij hoort. Deze skill verandert geen geometrie, geen
kleur, geen maat en geen layout.

Loop tot slot de leespas van `voice.md` af op de tekst die er nu staat: elk getal dat iemand
zelf heeft uitgerekend, de modaliteit die in de bron stond (`circa`, `naar verwachting`), en de
vraag of de titelrij hardop nog een verhaal is. Dat is geen scriptcheck en wordt er ook geen.

## Stap 6 — Opleveren

Twee bestanden, altijd beide:

1. `opgeschoond.pptx` — het gecorrigeerde deck, met een naam zonder apostrofs of andere tekens
   die een browser bij downloaden verhaspelt.
2. `wijzigingen.csv` — het wijzigingslogboek, met de kolommen `slide, origineel, nieuw, regel,
   toelichting`. Ook als er nul wijzigingen zijn.

En in het antwoord zelf, in deze orde:

1. **Eén alinea samenvatting**: hoeveel slides er zijn nagekeken, hoeveel tekstwijzigingen er
   zijn, welke bevindingen eruit springen, op welke slides er presentatienotities staan, hoeveel
   opmerkingen er zijn en hoeveel daarvan open staan, en op welke slides er mogelijk
   niet-lopende zinnen, gemengde taal of uitlijningsverschillen staan.
2. **De twee bestanden**, elk met een eigen regel: `Download het opgeschoonde deck` en
   `Download het wijzigingslogboek (CSV)`.
3. **Het logboek als tabel** in het antwoord. Is het lang, dan de eerste vijftig rijen met het
   totaal erbij.
4. **Wat je niet hebt kunnen beoordelen.** Geen renderer betekent geen vormbeoordeling, en dat
   zeg je met zoveel woorden. Zijn de huisstijlfonts gesubstitueerd, noem dan één concrete plek
   waar de gebruiker moet kijken in plaats van een voorbehoud over de hele deck.

## Wat blokkeert

Vier dingen. Ze gaan alle vier over "dit bestand is stuk" of "dit mag niet naar een klant", en
geen ervan gaat over vormgeving — dat oordeel komt van de render.

1. **Er is geen bestand.** Zonder `pad` uit stap 1 begin je niet, en je verzint geen deck.
2. **`mislukt` in de uitvoer van `toepassen.py` is niet leeg**, of `beeld` verschilt vóór en na
   het opslaan: er is een grafiek of een tabel verdwenen.
3. **`qa_text.py` meldt een `critical`** op het opgeschoonde deck: een restplaceholder, een
   `{{MARKER}}`, een sjabloonprompt, een slide zonder inhoud, Gotham Bold in de contentzone, of
   autofit die de tekst stil mag krimpen. Dat laatste is geen opschoningsvraag maar een
   bouwvraag; meld het en laat de gebruiker kiezen of `sfnl-slides` het repareert.
4. **Er staat een open opmerking in het bestand.** Dat blokkeert de oplevering niet, maar het
   blokkeert wél de bewering dat het deck klaar is: noem ze, met slide en tekst, en zeg dat er
   iemand over moet beslissen.

## Zonder renderer

Meldt `preflight.py` `qa-only`, dan schoon je de tekst gewoon op — dat is de helft van deze
skill en die is niet visueel. Wat er niet gebeurt is stap 5. `qa_text.py`, `qa_tellingen.py` en
`plan.py` zien geen overlap, geen contrast, geen dood wit en geen baseline; ze meten wat in de
XML staat. `mogelijke-overloop` is dan een schatting die niemand heeft nagekeken.

Zeg dat bij de oplevering met zoveel woorden: dit deck is niet visueel geverifieerd. Blind
opschonen is geen probleem; blind opschonen zonder het te zeggen is dat wel.

## Wat deze skill niet is

- **Geen bouwskill.** Een deck maken, slides toevoegen, een contentzone componeren: dat is
  `sfnl-slides` (het bestand heet nu nog `skills/sfnl-slides/SKILL.md`), die uit het sjabloon bouwt
  en de vormentaal uitvoert. Vraagt de gebruiker om nieuwe
  slides, dan verwijs je daarnaar in plaats van hier iets te tekenen.
- **Geen vormgevingspolitie.** Er komt geen script dat compositie afkeurt. De vlaggen zijn
  aanwijzingen, de render is het oordeel, en een mens beslist. Een script dat compositie telt,
  groeit uit zichzelf naar een script dat compositie afkeurt, en dan vermijdt de bouwer regels
  in plaats van slides te maken.
- **Geen herschrijver.** Zinnen korter maken, jargon eruit halen, de toon bijstellen: dat is
  `sfnl-humanizer` en `sfnl-tekst-scherpen`. Deze skill raakt de inhoud van een zin niet aan.
  Ziet hij een zin die niet loopt, dan meldt hij hem.
- **Geen vertaler.** Nederlands blijft Nederlands en Engels blijft Engels. Gemengde taal is een
  vlag, geen opdracht.
- **Geen kleur- of maatcorrector.** Een harde hex, een off-brand font of een maat die uit de
  toon valt is een bevinding met een vindplaats in `reference/merk.md`, `sjabloon.md` of
  `vormentaal.md` §2 — en een reparatie in de bouwroute, niet hier.

En één ding dat je nooit zegt: dat je geen rechten hebt om het bestand te bewerken. Je bewerkt
een kopie, en het origineel blijft staan.
