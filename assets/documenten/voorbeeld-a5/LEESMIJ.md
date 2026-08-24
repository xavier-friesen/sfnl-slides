# assets/documenten/voorbeeld-a5/ — het tweeluik, de korte route

Twee pagina's op A5, met de **titelbalk** als opening. **Dit is een voorbeeld en geen sjabloon:**
de tekst erin is verzonnen om de vorm te kunnen laten zien. Wat er in een echt document op de
pagina's komt, volgt uit het materiaal van de gebruiker — zie *De grens die deze skill bewaakt*
in de SKILL. Dit is het geval dat het vaakst voorkomt
en dat het minst op de vier-pagina-document lijkt: een uitnodiging, een tweeluik, een korte
notitie. De render staat in `assets/documenten/maatstaf/06-tweeluik-a5.png`.

| bestand | pagina |
|---|---|
| `Main.dc.html` | de voorkant: titelbalk in het huisverloop, chapeau, twee alinea's, en de gegevens onderaan |
| `Achterkant.dc.html` | een genummerde reeks met badges, een sluitregel achter een haarlijn, en een aflopende oranje band met het logo |

Waarom dit een ander document is dan een document van vier, en niet een kortere:

1. **Er is geen buitenste pagina om iets apart op te zetten.** In een document van vier is pagina
   4 die plek. Hier moet alles tussendoor: op de voorkant onder een haarlijn, op de achterkant in
   de aflopende band. Dat is een compositiebesluit en geen restje.
2. **Er is geen aanloop.** De chapeau is meteen de boodschap. Wie hier eerst context schrijft,
   heeft de helft van zijn document opgemaakt aan opwarmen.
3. **De opening is een titelbalk en geen titelblad.** Een titelblad zou de helft van het
   document kosten. De band kost een kwart van één pagina en zet de titel er net zo goed op.
4. **De letter staat hoger.** Op `a5` en `dl` zet `stijl.css` de body op 11 pt in plaats van
   10 pt, en de kleine maat op 9. Dat is geen smaak maar de maat: de zetspiegel is 473 px breed
   en dat is één kolom, dus op 10 pt kom je op 73 tekens per regel uit — tegen de bovengrens aan.
   Op 11 pt zijn het er 66.

De vulgraad staat op 0,88 en 0,72. Dat tweede getal is eerlijk: een uitnodiging mag ademen, en
de aflopende band onderaan draagt de rest van het blad. Het is de render die dat beslist en niet
het getal.
