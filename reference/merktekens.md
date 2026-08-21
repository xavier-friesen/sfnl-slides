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

## Wat hiervan nog code vraagt

1. **Een accolade die zijn punt op de doelvorm legt** in plaats van op zijn eigen midden. Dit is
   het merkteken met het hoogste rendement van de tien: het is de reden dat de effectenkaart met
   dertig blokken leesbaar is.
2. **Een doosberekening voor gedraaide vormen**, zodat een zijrail op zijn plek staat zonder
   proberen.
3. **Een regel in §12 over het verschil tussen meter en chip**: graduatie tegen categorie. Nu
   staat alleen de meter beschreven.

## Wat hiervan geen code hoort te worden

De effectenkaart zelf. Vijf kolommen, dertig blokken, ruim driehonderd woorden: als exhibit in
een rapport werkt hij, en de kleurdiscipline erin is voorbeeldig — sky is een effect, lavendel
een geaggregeerd effect, emerald een financiële baat, blauw een stakeholder, en dat houdt hij
zeventig blokken lang vast. Maar hij is geen slide voor een presentatie en hij hoort niet in
`assets/maatstaf/`, want als lat voor tekstlast is hij het tegendeel van wat §13 vraagt. Wie hem
nabouwt bouwt een rapportpagina, en dan is `sfnl-rapport` de skill.
