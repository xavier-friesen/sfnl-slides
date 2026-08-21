# Merktekens uit bestaande SFNL-decks

Geen patroonbibliotheek. Dit is een lijst **merktekens** — elementen die één ding tekenen en
één ding coderen — geoogst uit vijf decks die met de hand of met eerdere versies van deze skill
zijn gemaakt. Per merkteken staat er wat het codeert, waar het vandaan komt, en of de
primitievenlaag het al kan.

Waarom dit bestand bestaat: de laag kon lang alleen rechthoeken, lijnen en tekst, en wie alleen
dat heeft bouwt kaarten met tekst. `shapes.py` is inmiddels ruimer, maar het weten wat je kúnt
tekenen liep achter op het kunnen. Dit is die lijst. Gebruik hem zoals `assets/maatstaf/`:
niet om na te tekenen, maar om te weten wat er bestaat.

Bronnen, alle vijf SFNL-decks: `Eindrapport MBC MDT Maatjesprojecten` (67 slides),
`Handleiding 2 — Je eerste dashboard bouwen` (34), `Werksessie 1 impactmeten RO/RS` (23),
`Check-in 1` (12) en `Check-in 2` (13).

---

## 1. De accolade die een groep aan één uitkomst knoopt

**Codeert:** deze vier dingen leiden samen tot dat ene. Niet vier pijlen, één haak.

De effectenkaart in het eindrapport (slide 19 en 20) gebruikt hem acht keer, in oranje, tussen
elke kolom van de resultatenketen. Dat is wat die slide leesbaar houdt: vijf kolommen met
tientallen blokken, en de lezer ziet in één blik welke set bij welke uitkomst hoort. Met pijlen
was het een kabelbos geworden.

**Bouwbaar:** ja, sinds `adj` in `vlak()` werkt — `prst="rightBrace"` of `"leftBrace"` met een
`adj` voor de knikhoogte. Zonder eigen `adj` krijg je PowerPoints default en dan zit de punt
midden in plaats van bij de doelrij. Wat nog helpt: een merkteken dat de punt op de y van de
doelvorm zet in plaats van op het midden van de haak.

## 2. De kolomkopband met subkoppen eronder

**Codeert:** twee kolommen die samen één ding zijn.

Eindrapport slide 19: één oranje band `Sociaal maatschappelijke effecten` over de volle breedte
van twee kolommen, met daaronder twee kleinere oranje labels (`Jonge nieuwkomers`,
`Nederlandse jongeren`). Twee niveaus koptekst zonder een tweede tabel.

**Bouwbaar:** ja, met twee `vlak()`-rijen. Wat ontbreekt is de regel wanneer je dit doet in
plaats van vier losse kolomkoppen — dat is een hiërarchiebesluit en het hoort bij §12.

## 3. De gedraaide zijrail

**Codeert:** waar dit hele blok over gaat, zonder er een titelregel aan te kosten.

Eindrapport slide 19: een grijze balk links over de volle hoogte met gedraaide tekst
(`Deelnemers (jonge nieuwkomers en Nederlandse jongeren)`). Dat is de as van de hele exhibit,
en hij kost nul verticale ruimte.

**Bouwbaar:** ja, `vlak(..., rot=270)`. Nagemeten valkuil: een gedraaide vorm draait om zijn
middelpunt, dus een smalle hoge balk met `rot=270` heeft een andere doos nodig dan je op het
oog zou zetten. Reken de doos vóór de draai.

## 4. De genummerde badge in een pillenlijst

**Codeert:** volgorde, en waar je nu bent.

Handleiding slide 2: de agenda als een stapel navy pillen op een verzadigd halfpaneel, elk met
een cirkelbadge links. Check-in 2 slide 5 doet hetzelfde horizontaal: vier badges op een rij met
de aantallen eronder. De badge zelf zit al in `punt()`; wat deze twee toevoegen is dat de badge
buiten de kaart staat en de kaart zelf leeg blijft.

**Bouwbaar:** ja. Let op de badgekleur: `punt()` zet per §3 navy op een lichte hue, en wit op
een volle hue is een gedocumenteerde uitzondering.

## 5. De stappenbalk met badge boven en band onder

**Codeert:** een proces van vijf stappen waarvan er geen belangrijker is dan de andere.

Handleiding slide 4: vijf gelijke kolommen (`VRAAG · DATA · ANALYSE · VISUALISEREN · CONTROLE`),
elk met een badge boven de kolomkop, en onder de rij één band met de regel die voor alle vijf
geldt. Dat laatste is de vondst: de band draagt hier inhoud in plaats van een samenvatting, dus
hij valt niet onder het bandbudget van §10 als afsluiter.

**Bouwbaar:** ja.

## 6. De KPI-pil op een verzadigd paneel

**Codeert:** één feit dat je moet onthouden, in het verzadigde register.

Handleiding slide 8: op een navy halfpaneel twee lichte pillen met `210 DEELNEMERS` en
`DATA IS NIET PERFECT`. Dit is hoe je een drager in het verzadigde register zet zonder een
getal van 40pt: de pil maakt het feit een object.

**Bouwbaar:** ja, `vlak(prst="roundRect")` met een absolute radius op een vol vlak.

## 7. De chiprij als tabelkolom

**Codeert:** een categorie per rij, als label in plaats van als woord.

Check-in 2 slide 12: een tabel waarvan de derde kolom geen tekst is maar een stapel kleine
gekleurde chips (`GELIJK`, `ANDERS`, `ALLEEN GZ`). De kleur codeert de uitkomst en de chip maakt
hem scanbaar; in tekst was het een derde kolom die je moest lezen.

**Bouwbaar:** ja. Dit is de compacte variant van de puntenmeter uit `maatstaf/12`: gebruik de
meter voor een graduatie, de chip voor een categorie.

## 8. Het abstracte mockupblok

**Codeert:** dit is een scherm, en let op de indeling en niet op de inhoud.

Handleiding slide 9: een minidashboard van een tabelletje plus vier tegels met `Visual 1`,
`Visual 2`, `Visual 3`. Zelfde idee als de post-itwand in `maatstaf/14`: de vorm staat voor het
ding, en de tekst hoeft er niet in.

**Bouwbaar:** ja, met `vlak()` en `streep()`.

## 9. De genestelde waarschuwing

**Codeert:** hier gaat het mis, en het hoort bij dít blok.

Handleiding slide 5 en 11: een koraal of grapefruit kader ín een kolom, met `Let op` of
`En altijd`. Het is geen band onderaan de slide maar een uitzondering binnen het blok waar hij
over gaat, en daarmee ontsnapt hij aan de eenvormigheid van de afsluitband.

**Bouwbaar:** ja.

## 10. De divider met foto op de helft in plaats van over de volle slide

**Codeert:** hoofdstukgrens, maar stiller.

Alle vijf de decks doen dit, en consequent: foto links, verzadigd paneel rechts met de
hoofdstuknaam en een korte regel. Het eindrapport gebruikt daarnaast dividers met een groot wit
lijnicoon op een verzadigd vlak plus de subhoofdstukken eronder als lijst — een inhoudsopgave
per hoofdstuk.

**Niet bouwbaar zoals het sjabloon nu staat:** dit zijn eigen layouts, en de fotolayouts 6 t/m 16
in `sfnl-sjabloon.potx` zetten de tekst over de volle foto. Wie dit wil, tekent het paneel zelf
over de foto heen. Dat werkt, maar het is geen geërfde chrome meer. Openstaand besluit: hoort dit
in het sjabloon of blijft het handwerk.

---

# Tweede oogst: vijf decks erbij

`Kickoff Zilveren Kruis` (22), `Baanbrekers WP2 fase 1 verandertheorie` (22),
`Baanbrekers WP2 S1 kickoff` (32), `Analyse risicoleerlingenlijst Gouda` (51) en
`Kick-off Aidsfonds` (22, Engels). Vijftien merktekens erbij, en één techniek die geen merkteken
is maar een manier van doen.

## 11. De uitspraakslide

**Codeert:** stop even, dit is de vraag waar het om gaat.

Aidsfonds slide 9: een volledig oranje slide met één vraag tussen aanhalingstekens, gecentreerd,
verder niets — geen titel, geen logo behalve het merk. Dit is het verzadigde register in zijn
zuiverste vorm en het is precies wat een spreekdeck nodig heeft: de slide waar de spreker een
minuut stil kan vallen.

De plugin kent dit niet. Zijn enige volledig verzadigde slide is de oranje outro, en die is een
slot. Een uitspraakslide midden in de deck is een ander instrument, en het is het goedkoopste
antwoord op besluit 5 (twee registers) én op de dichtheid: nul woorden op de slide behalve de
vraag zelf.

**Bouwbaar:** ja, met een vol vlak over de hele slide op een layout zonder titel (17) en één
gecentreerde `drager()`. Let op: op oranje is de tekst navy tenzij hij op 40pt staat (§3).

## 12. Het gestreepte groepeerkader met een label, en de opbouw over drie slides

**Codeert:** dit deel van het schema is waar we het nu over hebben.

Baanbrekers-kickoff slide 18, 19 en 20: driemaal dezelfde verandertheorie-canvas, met daarover
een gestreept kader dat één keer om de linkerhelft ligt, dan om het middendeel, dan om de rest,
elk met een eigen label (`WP 1`, `WP 2 — SESSIE 1`, `WP 3`). Het kader is niet decoratief maar
een scopemarkering, en de herhaling maakt van één exhibit een verhaal van drie stappen.

**Dit is de techniek, niet het merkteken:** hetzelfde beeld drie slides achter elkaar met één
element dat verschuift. Het kost drie slides en het leest sneller dan drie verschillende
composities, want de lezer hoeft zich maar één keer te orienteren. De plugin waarschuwt terecht
tegen twee gelijke plattegronden naast elkaar (§10) — dit is de uitzondering, en die uitzondering
hoort erbij: gelijke plattegronden zijn een defect wanneer ze toevallig gelijk zijn, en een
middel wanneer ze bedoeld gelijk zijn.

**Bouwbaar:** ja, `duplicate_slide.py` plus `place_shapes.py` om het kader te verschuiven, en
`lijn=(hue, 2, "dash")` voor het kader. Wat helpt: een regel in §10 die de bedoelde herhaling
van de toevallige onderscheidt.

## 13. Het ronde portret met rollabel

**Codeert:** wie dit doet, en in welke rol.

Aidsfonds slide 4: vier ronde portretfoto's op een rij, met boven elke foto het rollabel in caps
(`PROJECT-MANAGER`, `CONSULTANT`, `EXPERT`, `EXPERT`) in wisselende hues, en eronder de naam en de
functie. De kolommen zijn gescheiden door gestreepte verticale lijnen.

**Bouwbaar:** de ronde uitsnede is een `prstGeom="ellipse"` met een `blipFill` — een foto in een
vorm in plaats van een los plaatje. Dat kan de laag nu níet: er is geen weg naar `blipFill`. Dit
is het tweede echte gat na de accolade, en het is een teamslide die in elk voorstel terugkomt.

## 14. De sectiekoprij binnen een tabel

**Codeert:** vanaf hier begint een ander deel van dezelfde tabel.

Aidsfonds slide 8 en handleiding slide 17: een tabel waarin `Phase 1` en `Phase 2` als volle
gekleurde rij over de volle breedte tussen de gewone rijen staan. Twee tabellen worden zo één
tabel, zonder een tweede kop en zonder een tweede blok.

**Bouwbaar:** `add_table.py` kent dit niet — het verdeelt rijen gelijk en kent geen rij die zijn
cellen samenvoegt. Werkbaar alternatief: twee tabellen met een gevulde band ertussen, wat er
vrijwel hetzelfde uitziet.

## 15. De pijltabketen, en de tweede rij eronder

**Codeert:** een route met richting, waarbij elke stap zijn eigen kleur heeft.

Baanbrekers-kickoff slide 9 en baanbrekers-vt slide 5: drie pijltabs op een rij
(`VERANDERTHEORIE` → `EFFECTENKAART` → `MAATSCHAPPELIJKE BUSINESSCASE`), en op slide 9 een tweede
rij eronder met dezelfde vorm voor de producten. Gouda slide 12 doet het met drie genummerde
chevrons in coral, navy en sky.

De vondst zit in de tekstplaatsing: **de uitleg staat ónder de pijltab, niet erin.** Dat is de
oplossing voor het probleem dat een chevron zijn tekst de schuine kant in duwt — een valkuil die
bij het nabouwen van de maatstaf twee ronden kostte. Pijltab is de kop, de kolom eronder is de
inhoud.

**Bouwbaar:** ja, `prst="homePlate"` of `"chevron"` met een eigen `adj`.

## 16. De rondbadge-icoonrij met de uitkomst als laatste

**Codeert:** vier dingen die samen naar één ding leiden.

Baanbrekers-kickoff slide 11: vier grote ronde badges met een icoon
(`LEREN`, `STUREN`, `COMMUNICEREN`, `VERDUURZAMEN`), waarvan de laatste in emerald staat en met een
pijl uit de eerste drie volgt. De hue doet het werk: drie in dezelfde kleur zijn de middelen, de
vierde in een andere kleur is het doel.

**Bouwbaar** op de badge na: de iconen zijn plaatjes. Zonder icoonbibliotheek wordt het een
cirkel met een kort woord erin, en dat werkt (§3 zegt dat een kop in zijn hue de categorie
sneller draagt dan een pictogram) — maar dan is het merkteken de kleurwissel op de laatste, niet
het icoon.

## 17. Het vraagkader

**Codeert:** dit is wat wij aan jullie vragen, en het is geen conclusie.

Baanbrekers-kickoff slide 6, 15 en 16: een koraal omlijnd kader met de vraag erin, en een klein
tekstballonnetje in de hoek. Het staat naast de inhoud in plaats van eronder, en daarmee is het
geen afsluitband — het ontsnapt aan het bandbudget van §10 om dezelfde reden als de genestelde
waarschuwing (nummer 9).

Dit is het merkteken dat een werksessiedeck het meest nodig heeft, en het bijgeleverde
werksessiedeck deed het met een oranje band onderaan elke slide. Eén kader naast de inhoud zegt
hetzelfde en kan wél tien keer terugkomen zonder dat het gaat dreunen, omdat het niet de volle
breedte pakt.

**Bouwbaar:** ja. Het ballonnetje niet (plaatje), en dat hoeft ook niet.

## 18. De foto met sluier onder een uitspraak

**Codeert:** deze tekst hoort bij dit beeld.

Aidsfonds slide 5: een foto over de halve slide met een doorschijnend oranje paneel eroverheen
waarin de samenvattende alinea staat. `adviesvorm.md` §4 verbiedt stockfoto-sfeer in de
contentzone, en terecht — maar dit is niet sfeer, het is een dragende alinea met een beeld
eronder in plaats van naast.

**Bouwbaar:** een vol vlak op alpha over een foto kan. De foto zelf in de contentzone is de
uitzondering die je motiveert; zonder sluier is de tekst onleesbaar en dan is de regel uit §4
gewoon van kracht.

## 19. Het planningsraster met mijlpaalmarkers

**Codeert:** wanneer wat klaar is, en hoeveel dagen het kost.

Aidsfonds slide 11: rijen met activiteiten, kolommen per maand, kleine markers waar een mijlpaal
valt, en een smalle rechterkolom met het aantal dagen. Dat laatste is de vondst: de dagen staan
niet in de balk maar in een eigen kolom, zodat de tijdlijn leesbaar blijft én de inspanning
optelbaar is.

**Bouwbaar:** ja, met `schaal()` voor de maandkolommen en `punt()` voor de markers. Dit is het
sterkste argument voor `schaal()`: een planning waarvan de x-positie niet op schaal staat, is een
lijst met datums.

## 20. De gelaagde vraagbanden

**Codeert:** dezelfde vraag op drie niveaus, van breed naar smal.

Gouda slide 11: drie gestapelde banden in grapefruit, sky en emerald —
`MAATSCHAPPELIJKE VRAAGSTUK`, `AANPAK GEMEENTE GOUDA`, en onderaan `VRAAG AAN SFNL`. De trechter
zit in de volgorde en in de kleur, niet in de vorm.

**Bouwbaar:** ja. Let op dat dit drie banden zijn en dus het bandbudget van §10 raakt: hier is
het één compositie van drie delen op één slide, en dat telt als één.

## 21. De genummerde kaartenrij die eindigt in de conclusie

**Codeert:** vier bevindingen, en wat er dan volgt.

Gouda slide 9: vier genummerde tint-kaarten op een rij (`1 BETERE REGISTRATIE`,
`2 VERSTERKTE SAMENWERKING`, …) en als vijfde cel een verzadigde kaart met `CONCLUSIE` en het
bedrag erin. De rij en de conclusie staan op één lijn, dus je leest ze in één beweging.

**Bouwbaar:** ja, en dit is een goede vervanger voor de afsluitband: de conclusie staat ín de rij
in plaats van eronder. §10 noemt dit als alternatief ("doordat de laatste rij zelf de conclusie
is"); hier staat hoe dat eruitziet.

## 22. De fasenstapel met sleutelparen

**Codeert:** vijf fasen, elk met dezelfde drie feiten.

Baanbrekers-vt slide 8 en baanbrekers-kickoff slide 16: vijf kolommen of banden, elk in een eigen
hue, en binnen elke fase steeds dezelfde labels (`Activiteit`, `Duur`, `Uitkomst`). Herhaalde
labels zijn hier géén defect zoals in de rijkoptoets van §13, en dat is het onderscheid dat de
moeite waard is: **herhaalde labels binnen één rij zijn een tabel in vermomming; herhaalde labels
per kolom in een fasenschema zijn een sleutel.** Het verschil is of de lezer ze naast elkaar
vergelijkt (tabel) of per kolom leest (sleutel).

**Bouwbaar:** ja.

## 23. De mini-logicamodel als leeslegenda

**Codeert:** zo moet je het grote schema hierna lezen.

Gouda slide 17: onder een alinea proza staat een kleine keten van vier vakjes
(`ACTIVITEITEN` → `OUTPUTS` → `OUTCOMES` → `IMPACT`) als legenda, en op de slides erna staat het
volle schema in dezelfde vier kleuren. Een sleutel vooraf, één regel hoog.

**Bouwbaar:** ja, en het is goedkoop: vier `vlak()` en drie pijlen.

## 24. De logowand en de mede-merk-cover

**Codeert:** dit doen we samen met hen.

Baanbrekers-kickoff slide 1 en 4: op de cover staan drie partnerlogo's in de witte logokaart in
plaats van alleen het SFNL-merk, en slide 4 is een aparte logowand met vijf logo's op wit.

**Niet bouwbaar zoals het sjabloon staat:** de witte logokaart op layout 1 is geërfde chrome met
één logo erin. Een partnerlogo erbij is een plaatje in de kaart, en de laag kan geen plaatjes
plaatsen. Dit is hetzelfde gat als het ronde portret (nummer 13): **er is geen weg naar een
afbeelding.** Voor een deck met partners is dat geen detail.

## 25. Het artefactvoorbeeld

**Codeert:** dit is wat je straks krijgt.

Baanbrekers-kickoff slide 10: een verkleinde afbeelding van de publiekssamenvatting-infographic,
met een koraal notitiekader ernaast. Het toont het eindproduct als object in plaats van het te
beschrijven.

**Niet bouwbaar:** zie 13 en 24 — geen afbeeldingen. Wel het notitiekader ernaast.

## 26. De pictogramladder

**Codeert:** een trap waarvan elke trede meer betekent, met een figuur per trede.

Baanbrekers-vt slide 19: de participatieladder als een reeks kleine menselijke figuren die
oplopende treden bestijgen. Charmant en direct leesbaar, en het is de enige plek in tien decks
waar een pictogram werkelijk iets doet wat een woord niet doet.

**Niet bouwbaar** zonder icoonbibliotheek. De trap zelf wel (`maatstaf`-achtige treden), en dan
draagt de trede het label.

---

## Wat hiervan nog code vraagt

1. **Een accolade die zijn punt op de doelvorm legt** in plaats van op zijn eigen midden. Dit is
   het merkteken met het hoogste rendement van de tien: het is de reden dat de effectenkaart met
   dertig blokken leesbaar is.
2. **Een doosberekening voor gedraaide vormen**, zodat een zijrail op zijn plek staat zonder
   proberen.
3. **Een regel in §12 over het verschil tussen meter en chip**: graduatie tegen categorie. Nu
   staat alleen de meter beschreven.
4. **Een weg naar een afbeelding.** Dit is na de accolade het grootste gat en het raakt drie
   merktekens uit de tweede oogst: het ronde portret (13), de logowand en de mede-merk-cover (24)
   en het artefactvoorbeeld (25). Nodig is een `blipFill` in een vorm — een foto in een ellips of
   een logo in een vak — met de bestaande discipline eromheen. Elk voorstel met een teamslide en
   elk project met partners loopt hier nu vast, en het handmatige alternatief is een plaatje in
   PowerPoint erin slepen ná de bouw, waarmee het deck niet meer herbouwbaar is.
5. **Een sectiekoprij in `add_table.py`** (14): een rij die zijn cellen samenvoegt en een volle
   vulling draagt. Nu is het antwoord twee tabellen met een band ertussen.
6. **Een regel in §10 die bedoelde herhaling van toevallige onderscheidt** (12). Drie keer
   dezelfde canvas met een verschuivend scopekader is een middel; drie keer dezelfde plattegrond
   zonder reden is het defect. De huidige tekst kan alleen het tweede zien.

## Wat hiervan geen code hoort te worden

De effectenkaart zelf. Vijf kolommen, dertig blokken, ruim driehonderd woorden: als exhibit in
een rapport werkt hij, en de kleurdiscipline erin is voorbeeldig — sky is een effect, lavendel
een geaggregeerd effect, emerald een financiële baat, blauw een stakeholder, en dat houdt hij
zeventig blokken lang vast. Maar hij is geen slide voor een presentatie en hij hoort niet in
`assets/maatstaf/`, want als lat voor tekstlast is hij het tegendeel van wat §13 vraagt. Wie hem
nabouwt bouwt een rapportpagina, en dan is `sfnl-rapport` de skill.
