# assets/infographic/maatstaf/ — waar de lat ligt

Zes afgemaakte infographics en één contactblad met schetsen. Dit is de norm: zo ziet een
opgeleverde SFNL-infographic eruit. De bouwscripts staan in `assets/infographic/voorbeeld/`; in elke
docstring staat waarom de compositie is zoals hij is en wat er in de eerste versie misging.

| bestand | vorm | canvas | register | drager |
|---|---|---|---|---|
| `m1-geldstroom` | sankey | breed, 960 × 320pt | bijna helemaal wit, één accent | `€ 1,2 mln` op 40pt in oranje |
| `m2-tijdlijn` | tijdlijn op schaal | breed, 960 × 320pt | bijna helemaal wit, één accent | `33 maanden` op 40pt, rechtsboven |
| `m3-afweging` | divergerende staaf | breed, 960 × 320pt | wit, twee coderende hues | `+ € 0,08 mln` op 36pt in emerald |
| `m4-rasterplot` | rasterplot | vierkant, 560 × 560pt | wit, één accent | `71 aan het werk` op 40pt |
| `m5-powerpoint` | waterval | slide, 13,33 × 7,50 in | bijna helemaal wit, drie coderende hues | `+ € 0,08 mln` op 40pt in emerald |
| `m6-tinttrap` | verdeelde band, één hue in drie tinten | breed, 960 × 288pt | wit, één accent plus een tinttrap | `15,3 pp` op 36pt in oranje |
| `schetsen-drie-concepten` | wireframes: twee figuren, één rooster | breed | geen | n.v.t. |

**Wat ze gemeen hebben, en wat je ervan overneemt.** Alle zes zijn een figuur: er is een meting
die een maat bepaalt — de dikte van een stroom, de x van een moment, de lengte van een staaf, het
aantal vierkantjes, de hoogte van een trede. Verandert het getal, dan verandert de tekening. Geen
van de zes is een rij kaarten, en dat is geen toeval maar de norm waar dit mapje voor staat.

Geen van de zes heeft een containervulling: de hiërarchie komt uit maat, gewicht en kleur in de
letter, en de scheiding uit haarlijnen. Wat gevuld is, draagt inhoud — een staaf, een kolom, een
stroom, een vierkantje. Alle zes hebben één drager op 36 tot 40pt en niets anders dat groot is. Alle zes
hebben een optische marge van ongeveer 30pt, want alleen een volvlak bloedt af en los tekstwerk
tegen de rand leest als een schermafbeelding. En alle zes sluiten af met een haarlijn plus een
sluitregel, of met een volle band — nooit met een kader.

`m5` is de enige in PowerPoint. Layout 17 erft het SFNL-logo en het paginanummer uit de master;
`scripts/infographic/blanco.py` haalt die weg, zodat er een witte pagina overblijft met alleen de compositie
erop. Er staat ook geen bronregel op: bij de intake is gekozen voor "de container draagt de
bron". Gaat zo'n beeld los rondzwerven, dan hoort de bronregel er alsnog op.

`m6` is de enige die kleur binnen één categorie laat variëren, en hij staat er om te laten
zien wanneer dat mag. De vier uitvoerders dragen allemaal dezelfde grootheid, dus vier hues
zouden vier soorten suggereren die er niet zijn; de breedte draagt het deelnemersaantal en de
navytint het plaatsingspercentage, en nergens anders in het beeld staat dat percentage als
lengte. Drie stappen en niet vier: navy is de donkerste hue die er is en draagt er drie —
`svg.trap_draagt("navy")` rekent het uit, §6b van de vormentaal legt het uit. De prijs staat
er ook in: twee uitvoerders die 0,3 procentpunt uit elkaar liggen krijgen dezelfde tint, en
het label lost dat op.

`schetsen-drie-concepten` laat zien hoe een conceptkeuze eruit hoort te zien: A is een sankey,
B een tijdlijn op schaal, C een rooster van vier kolommen. Twee figuren en ten hoogste één
rooster, want een set van drie roosters is geen keuze maar één concept in drie uitvoeringen. Je
ziet in het beeld zelf wat C kost: hij zegt wie er meedoen en niet hoeveel of wanneer.

**Wat er nog aan mankeert.** In `m2` staan de twee maatbalken dicht op de bronregel. In `m5`
staat de tekst in gesubstitueerde fonts breder dan in echte PowerPoint, dus kijk daar één keer
naar in PowerPoint zelf. Dat is geen valse bescheidenheid: de render blijft het enige oordeel
over de vorm, ook over deze zes.

**En één ding is hier gerepareerd, want het staat er als les.** De eerste vijf zijn opnieuw gebouwd
toen de skill in de plugin kwam en de fontmetriek van geschat naar gemeten ging. `m1` veranderde
zichtbaar: de drager stond er als `€ 1,2` boven `mln`, op twee regels, en de bronregel liep ook
over twee. Met de ruime schatting paste "€ 1,2 mln" op 40 pt niet in zijn blok van 240 pt, dus
brak de regelafbreking hem af — precies de gebroken drager waar §4 van de vormentaal tegen
waarschuwt, in het beeld dat de norm hoort te zijn. Dat is wat een geschatte metriek doet: hij
faalt niet, hij zet iets anders neer dan je bedoelde. Bouw je deze bestanden opnieuw, controleer
dan eerst met `preflight.py` dat `meting_echt` op `true` staat.
