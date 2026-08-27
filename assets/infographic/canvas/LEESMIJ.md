# assets/infographic/canvas/ — de conceptkeuze zoals hij eruit hoort te zien

Drie artboards en een manifest, geschreven door `assets/infographic/voorbeeld/drie_schetsen.py`. Dit is de
uitvoer van stap 2D: dezelfde drie concepten als in `assets/infographic/maatstaf/schetsen-drie-concepten.png`,
maar dan als canvas in plaats van als contactblad.

| bestand | wat het is |
|---|---|
| `Main.dc.html` | concept A, de geldstroom. Heet Main omdat de canvashelper dat eist; de leesbare naam staat in het manifest |
| `ConceptB.dc.html` | concept B, de tijdlijn op schaal |
| `ConceptC.dc.html` | concept C, het rooster — één van de drie, nooit meer |
| `canvas.json` | de plaatsing, plus de vier regels per concept als notitie ernaast |

**Wat een artboard is.** Het omhulsel van een `.dc.html` met de SVG erin die `schets.py` toch al
maakte. Niet meer dan dat, en dat is een keuze: een schets is er om de plattegrond te
beoordelen, niet om aan te schuiven, dus hij hoeft niet per element bewerkbaar te zijn. Het
kost daardoor niets extra's — `artboard_=` in het bouwscript, en klaar.

**Waarom dit het contactblad verving.** De vier regels per concept staan naast hun eigen schets
in plaats van in de `description` van een keuzemenu; drie concepten met verschillende
canvasmaten passen naast elkaar op ware verhouding, waar een contactblad alles even breed maakt
en een naaf dus laat verliezen van een band op een eigenschap die na de keuze verdwijnt; en de
gebruiker kijkt rond en wijst aan in plaats van een van drie opties aan te vinken.

**Het contactblad is niet weg.** Je kijkt er altijd zelf naar vóór je iets voorlegt, en het is
de terugval wanneer `node` of de design-skill ontbreekt — wat regelmatig gebeurt, want die skill
wordt per sessie onder een versienummer uitgepakt. `preflight.py` zegt het.

Seeden en publiceren staat in stap 2D van de SKILL. Het gezaaide bestand van ruim 2 MB hoort
niet in deze map thuis: dat maak je per opdracht opnieuw.
