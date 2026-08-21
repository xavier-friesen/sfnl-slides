# assets/maatstaf/ — de veertien voorbeelden, en waar ze de lat niet zijn

Deze veertien PNG's zijn de feitelijke lat naast `reference/vormentaal.md`. Ze zijn niet
foutloos, en de bekende defecten staan hieronder — anders wordt een defect in een
voorbeeld straks aangehaald als bewijs voor precies wat de maatstaf verbiedt.

Twee soorten. **`01` tot en met `10`** komen uit decks die de blinde vergelijking hebben
gewonnen. **`11` tot en met `14`** zijn reconstructies: vier slides die als de mooiste uit de
skill kwamen, met deze plugin nagebouwd uit een beschrijving van het origineel, omdat de
originelen alleen als schermafbeelding bestonden. Ze zijn de lat voor hún compositie en hún
merktekens — de cirkelbadge, de gestreepte nadruk, de puntenmeter, de dumbbell op schaal, de
post-itschematiek — en niet voor hun uitvoering in detail; wat in de reconstructie zwakker is
dan het origineel staat hieronder.

Kijk naar de compositie van deze slides, niet naar hun uitvoering.

**Vier van de veertien zijn ook het antwoord op een vraag uit het vragenvuur** (skill, stap 1),
en dat is de reden dat ze hier met een getal in de tabel staan. De drie dichtheden hangen elk aan
een slide — `13` en `14` zijn een spreekdeck (50 en 59 woorden inclusief titel), `12` is een licht
leave-behind (99), `11` een leave-behind (141) — en de twee kaarttalen staan naast elkaar: `11` is
afgerond met per kaart een 1pt-haarlijn in de eigen hue, `12` is recht en zonder haarlijn. Zo
heeft elk antwoord in dat blok een beeld, in plaats van alleen een default met een reden.

| slide | blijft de lat voor | is de lat NIET voor |
|---|---|---|
| `01-getallenrij-vier-hues` | de vier hues, de brede panelen eronder | het grote getal staat over zijn eigen label; de onderste helft van de vier kaarten is leeg |
| `04-twee-kolommen-teal-tegen-koraal` | twee hues voor een tegenstelling, proza als exhibit, een bronregel per kolom | de aanhef staat in Montserrat SemiBold binnen een Lato Light-alinea — twee families in één tekstregel, en dat mag sinds `vormentaal.md` §9 niet meer |
| `06-stroomschema-twee-rijen` | het schema zelf, de twee rijen | het grote getal staat over zijn eigen label |
| `08-tabel-naast-grafiek` | de tabelzetting naast een native grafiek | dezelfde omzetreeks staat twee keer op één slide (`adviesvorm.md` §2) |
| `11-vier-fasekaarten-tweede-uitgelicht` | de cirkelbadge in de hue van de kaart, de gestreepte oranje nadruk om één kaart, vier hues die vier fasen coderen, de afsluitband die één keer voorkomt; en als antwoord in het vragenvuur: kaarttaal afgerond met een haarlijn in de eigen hue, dichtheid leave-behind (141 woorden) | de body staat op 13pt in plaats van 16 (vier kaarten van 2,95 in laten niet meer toe) |
| `12-tabel-verzadigde-rijlabels-puntenmeter` | het volle rijlabel tegen het nauwelijks getinte paneel, de puntenmeter als merkteken voor gewicht, kolomkoppen in grijs; en als antwoord in het vragenvuur: kaarttaal recht zónder haarlijn — het volle rijlabel begrenst de rij al — en dichtheid licht leave-behind (99 woorden) | de kapitaallabels staan op 12pt omdat `VERANTWOORDEN` op 14pt niet in de cel past; dat is een gevolg van de kolombreedte, geen model |
| `13-dumbbell-plot-op-schaal` | positie draagt de informatie, twee hues voor twee meetmomenten, het lichte register: alleen lijnen en punten op wit, en een aslabel dat binnen de zone blijft terwijl de tik op schaal staat; en als antwoord in het vragenvuur: dichtheid spreekdeck (50 woorden) | — |
| `14-postitwand-drie-stappen` | het schema in abstracte vorm zonder tekst, het grote cijfer met de kaplabel op één baseline en een lijn eronder, de pijl die een volgorde draagt | tussen het schema en de drie kolommen staat 0,58 in wit en onderaan nog 0,67 in; de slide leest luchtiger dan het origineel |

## De meting bij `04`

De aanhefjes op `04` (`Vaste contactpersoon.`, `Twee loketten.`) zijn nagemeten op de PNG,
1920 px bij 144 dpi, en ze zijn werkelijk Montserrat:

* `Vaste` is 92 px breed bij een kapitaalhoogte van 23 px, verhouding 4,00. Montserrat
  SemiBold zet 4,00; Lato Semibold 3,35.
* `noemen` in de rest van de regel is 106 px bij een x-hoogte van 17 px, verhouding 6,2.
  Lato Light zet 6,8; Montserrat Light 8,0. De rest is dus Lato.
* De regel nagebouwd op 16pt in Montserrat SemiBold + Lato Light valt op de pixel over het
  origineel; in Lato Semibold + Lato Light is de aanhef ruim 14 procent korter en breekt de regel
  elders.

De regel in §9 overruled hier dus een gemeten patroon uit een winnende deck, en niet een
verkeerde meting. Dat is een besluit, met de reden erbij: twee families binnen één
tekstregel zetten twee letterbouwen en twee x-hoogtes op dezelfde maat naast elkaar, en dat
leest als een zetfout in plaats van als hiërarchie. De aanhef staat sindsdien in
`Lato Semibold`, en `para()` in `scripts/shapes.py` weigert de mix.


## Twee dingen die in `11` tot `14` openstonden, en hoe ze beslecht zijn

**Cursief: toegestaan, beperkt.** `vormentaal.md` §9 zei "Cursief niet", en `run()` in
`scripts/shapes.py` weigerde het; het origineel van `11` heeft per kaart een cursieve
datumregel, en in de eerste reconstructie is daar een eigen run omheen gebouwd. Het besluit is
dat cursief mag voor een **korte, niet-lopende regel** — een datum, een eenheid, een bron, een
scenario-aanduiding — van één regel en ten hoogste 48 tekens, en verboden blijft voor lopende
tekst en voor alles van meer dan één regel. `run(..., cursief=True)` laat precies die regel door
en weigert de rest met een foutmelding die zegt wat je in plaats daarvan doet. §9 is
bijgeschreven; de datumregel op `11` is dus geen omzeiling meer maar de vorm zelf.

Eén meting die daarbij hoort, want ze kostte een ronde: een cursieve run zonder `i="1"` ziet er
op de render bijna hetzelfde uit als een rechte run in een licht gewicht op 11pt. De
tussenversie waarin het attribuut ontbrak is naast het origineel gelegd en pas op de derde blik
als niet-cursief herkend. Toets cursief dus in de XML en niet met het oog.

**Grijs met letterspatiëring: opgelost in de kleurtabel.** Het huisrecept voor een grijs
kapitaallabel — `label()` met navy op alpha — laat in de LibreOffice-render de laatste letter
van de run weg (`MEETDOEL` wordt `MEETDOE`, `GEWICHT` wordt `GEWICH`). De oorzaak is alpha op de
tekstkleur samen met `spc`; elk van de twee apart rendert goed. Dat is een **renderobservatie op
LibreOffice 24.2.7.2** en geen OOXML-feit: of echte PowerPoint dezelfde glyph laat vallen is
hier niet te toetsen.

`shapes.py` kent nu de kleur `"grijs"`: het voetnootgrijs dat `sjabloon.md` onder Kleur al als
hét grijs documenteert, `tx1` met `lumMod 65000` / `lumOff 35000`. Daarmee is een grijs
kapitaallabel één argument (`label("MEETDOEL", 11, "grijs")`) in plaats van een eigen run, en
`label()` weigert een alphakleur met de reden erbij. Het `GRIJS`-recept blijft geldig waar het
altijd goed was: op een gewone regel zonder spatiëring, de bronregel van §11.

Twee gevolgen voor de rij hierboven. Op `13` staat `TYPE PROJECT` in navy terwijl de aslabels
grijs zijn — dat verschil was een renderomweg en geen keuze, en het is nu met één kleur op te
lossen. En het aslabel dat buiten de zone liep is nu `binnen()` in `shapes.py`: het label wijkt,
de positie van het punt niet.
