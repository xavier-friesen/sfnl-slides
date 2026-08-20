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

| slide | blijft de lat voor | is de lat NIET voor |
|---|---|---|
| `01-getallenrij-vier-hues` | de vier hues, de brede panelen eronder | het grote getal staat over zijn eigen label; de onderste helft van de vier kaarten is leeg |
| `04-twee-kolommen-teal-tegen-koraal` | twee hues voor een tegenstelling, proza als exhibit, een bronregel per kolom | de aanhef staat in Montserrat SemiBold binnen een Lato Light-alinea — twee families in één tekstregel, en dat mag sinds `vormentaal.md` §9 niet meer |
| `06-stroomschema-twee-rijen` | het schema zelf, de twee rijen | het grote getal staat over zijn eigen label |
| `08-tabel-naast-grafiek` | de tabelzetting naast een native grafiek | dezelfde omzetreeks staat twee keer op één slide (`adviesvorm.md` §2) |
| `11-vier-fasekaarten-tweede-uitgelicht` | de cirkelbadge in de hue van de kaart, de gestreepte oranje nadruk om één kaart, vier hues die vier fasen coderen, de afsluitband die één keer voorkomt | de body staat op 13pt in plaats van 16 (vier kaarten van 2,95 in laten niet meer toe), en de cursieve datumregel omzeilt het cursiefverbod uit §9 — zie hieronder |
| `12-tabel-verzadigde-rijlabels-puntenmeter` | het volle rijlabel tegen het nauwelijks getinte paneel, de puntenmeter als merkteken voor gewicht, kolomkoppen in grijs | de kapitaallabels staan op 12pt omdat `VERANTWOORDEN` op 14pt niet in de cel past; dat is een gevolg van de kolombreedte, geen model |
| `13-dumbbell-plot-op-schaal` | positie draagt de informatie, twee hues voor twee meetmomenten, het lichte register: alleen lijnen en punten op wit | `TYPE PROJECT` staat in navy en de kolomkoppen op `12` in grijs, terwijl het dezelfde rol is — dat verschil is een renderomweg en geen keuze |
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


## Twee dingen die in `11` tot `14` openstaan

**Cursief.** `vormentaal.md` §9 zegt "Cursief niet", en `run()` in `scripts/shapes.py` weigert
het. Het origineel van `11` heeft per kaart een cursieve datumregel, en die is in de
reconstructie met een eigen run omheen gebouwd. Zo staat het er nu: de maatstaf en de
primitievenlaag spreken elkaar tegen op deze ene plek. Dat is een besluit dat genomen moet
worden — cursief toestaan voor een korte, niet-lopende regel (datum, eenheid, bron), of de regel
bevestigen en de datumregel in het origineel als defect van het origineel benoemen.

**Grijs met letterspatiëring.** Het huisrecept voor een grijs kapitaallabel — `label()` met
navy op alpha — laat in de LibreOffice-render de laatste letter van de run weg (`MEETDOEL`
wordt `MEETDOE`). De oorzaak is alpha op de tekstkleur samen met `spc`; elk van de twee apart
rendert goed. `12` en `13` gebruiken daarom het voetnootgrijs uit `sjabloon.md` (`tx1` met
lumMod/lumOff) in plaats van alpha. Of echte PowerPoint dezelfde glyph laat vallen is hier niet
te toetsen; de omweg volgt hoe dan ook de kleur die `sjabloon.md` als het grijs documenteert.
