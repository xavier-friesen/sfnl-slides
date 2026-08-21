# assets/proeven/ — de kleur- en gevuldheidsproef

Zes renders uit één proef, gebouwd om twee besluiten uit het vragenvuur te toetsen: de gevuldheid
(besluit 2) en wat kleur codeert (besluit 3). Drie ervan zijn sinds die proef de drie waarden van
besluit 2 — `03` is de default (weinig accent), `01` is kaal, `02` is met kleur — en `04` is
expliciet afgekeurd. Ze zijn géén lat. `assets/maatstaf/` is de lat; dit zijn
de metingen die de regels in `vormentaal.md` §3 en §5 onderbouwen, met de opzet erbij zodat ze
te herhalen zijn.

**Opzet.** Dezelfde inhoud — vier meetdoelen met een gewicht en één regel toelichting — in zes
vormen: drie gevuldheden (wit, tint, verzadigd) maal twee kleurschema's (oranje als enige accent,
of een set van vier hues). Daarna drie gerichte proeven op wat daar uit kwam. Renderomgeving:
LibreOffice 24.2.7.2, fonts-lato 2.015-1, fonts-montserrat 7.222-2, pdftoppm 24.02.0, 1921 px
breed. Gotham Bold is gesubstitueerd, dus de titelregels zijn niet maatvast; de kleurmetingen
hieronder zijn dat wel.

| render | wat hij aantoont |
|---|---|
| `01-wit-oranje-koppen-inversie` | Oranje koppen op wit náást navy koppen: de navy items lezen sterker dan de oranje. Oranje haalt 2,58 op wit en navy 15,3, dus kleur als nadruk in de letter draait de hiërarchie om. Gemeten: 94 procent wit, 1 procent verzadigd. |
| `02-vier-hues-volle-rijlabels-14procent` | Vier volle rijlabels van 3,40 bij 0,98 in zijn samen 13,3 vierkante inch, en de slide meet 14 procent verzadigd. Een kolom rijlabels haalt de band van §5 (20 tot 37) dus niet, ook al voelt de slide vol. |
| `03-nadruk-in-een-chip` | Dezelfde nadruk, maar in een volle oranje chip met navy tekst en alle koppen navy. Nu leest de nadruk als nadruk. Dit is de vorm die de inversie uit `01` oplost. |
| `04-alleen-oranje-25procent` | **Afgekeurd, en daarom bewaard.** Eén volle oranje band van 12,52 bij 1,90 in (23,8 vierkante inch) plus vier kaarten: gemeten 25 procent verzadigd, dus binnen de band van 20 tot 37 die de winnende decks laten zien. En toch is dit de vorm die niet meer wordt aangemoedigd — het oppervlak is groot en draagt vier woorden, dus de vulling wordt het luidste element van de slide. Dat is de reden dat die band in §5 een meting is en geen doel. |
| `05-label-in-vier-behandelingen` | Hetzelfde kapitaallabel in vier kleuren, met de kern van de letter uitgemeten: `tx1` lumMod 65 (het huidige "grijs") is `#5176A7`, contrast 4,67, verzadiging 51 procent — een vijfde blauw. Navy 100 procent is `#201B5C` / 15,3 / 71. Navy op alpha 70 is `#625E8C` / 6,0 / 33. Oranje is `#F87F4F` / 2,58 / 68. |
| `06-spc-bij-alpha-klipt` | De laatste glyph van een alpharun met `spc` valt niet weg maar wordt geklipt, en het is geen aan-of-uit: bij `spc="60"` staat de L van `MEETDOEL` er half, bij 100 vrijwel niet, en `VERANTWOORDEN` verliest bij 100 de hele N. Een spatie achter het woord repareert het niet. Zonder `spc` rendert elke lengte volledig. |

## De lichtheidstrap van tx1, apart gemeten

Vier trappen van hetzelfde slot, met de verzadiging erbij, want de vraag was of er een stap
bestaat die als grijs leest:

| trap | render | contrast op wit | verzadiging |
|---|---|---|---|
| lumMod 40 | `#93ABCA` | 2,35 | 27 procent |
| lumMod 50 | `#7796BD` | 3,05 | 37 procent |
| lumMod 65 (het huidige "grijs") | `#5176A7` | 4,67 | 51 procent |
| lumMod 80 | `#3D597E` | 7,17 | 52 procent |

Er is dus geen stap die neutraal is: `tx1` is `#233348` en elke verlichting houdt de blauwzweem.
Het palet heeft geen grijs. Dat is de reden dat `vormentaal.md` §3 een stil label nu als navy op
alpha zet en het lumMod-recept beperkt tot een deck waarin sky en royal niet meedoen.

## Het besluit dat hierop is genomen

Op deze zes renders is besluit 2 herschreven van "twee registers" naar drie gevuldheden, met
`03` als default: een deck staat in weinig accent, met soms een kale slide en soms een gekleurde.
`04` valt af. Dat is een keuze van Xavier op de renders, 21 augustus 2026, en de reden staat
erbij: het oppervlak van een grote vulling moet iets dragen, en in `04` draagt het vier woorden.

## Wat deze proef niet zegt

Niets over echte PowerPoint: de klipping in `06` is een observatie op LibreOffice 24.2.7.2. En
niets over aantrekkelijkheid — welke van de zes vormen de mooiste is, beslist het oog op de
render en niet deze tabel. Wat hier staat zijn de getallen eronder.

## Twee renders die er later bij kwamen

`07-modus-b-divider` en `08-modus-b-hoofdstuktitel` zijn geen proef maar een gat dat gedicht is:
titelmodus B stond alleen in `voice.md` en was nergens te zien. Dit is de vorm — een sectiedivider
uit fotolayout 6 met de hoofdstuknaam, en daarachter een contentslide met diezelfde hoofdstuknaam
als titel en de bewering in de subtitel. Kijk hier naar de titelzone, niet naar de compositie
eronder: die is uit `03` overgenomen om alleen de titelrij te laten verschillen.

## De keuzekaart

`assets/keuzekaarten/vragenvuur.png` is uit deze renders samengesteld: per besluit de opties naast
elkaar als detailuitsnede, met de meting eronder. Die kaart gaat bij het vragenvuur naar de
gebruiker en wordt door de skill niet gelezen, dus hij kost geen tokens. Verandert er een optie,
dan bouwt `python scripts/keuzekaart.py` hem opnieuw uit de renders die dan in de repo staan.

## De icoonproef

`09-iconen-getekend` en `10-iconen-met-en-zonder` horen bij `vormentaal.md` §14 en bij `icoon()`
in `shapes.py`. Op `09` staan zes zelfgetekende iconen op 0,72 in — document, mensen, kringloop,
euro, doel, klok — met ernaast dezelfde twee op 1,0 / 1,5 / 2,0pt en hetzelfde icoon op 0,44 /
0,72 / 1,10 in, plus de zes hues en één in wit op een vol vlak. Daaruit komen de waarden in §14:
1,5pt is de dikte (1,0 leest als een schets, 2,0 concurreert met de kop), en 0,44 in is de
ondergrens omdat de lijnen daaronder in elkaar lopen.

`10` is de vraag of het icoon iets doet: dezelfde drie stappen boven met een icoon per rij en
onder zonder. De onderste helft is de rustigere — naast een kop die `VERZAMELEN` zegt voegt een
poppetje niets toe — en daar komt de regel uit dat een icoon een soort moet coderen, iets moet
markeren dat terugkomt, of een zin in een schema moet vervangen. Op deze slide staan de iconen
in oranje, en dat is meteen het contrastpunt: een lijn van 1,5pt in oranje (2,6 op wit) leest
lichter dan zijn eigen kop ernaast.

Eén ronde ging verloren aan de kringloop: de pijlkop stond op geschatte coördinaten en zweefde
los van de boog. Het eindpunt van een boog is uit te rekenen (`cx + r·cos`, `cy + r·sin`, met de
klok mee, y naar beneden) en de kop staat op de tangens, 90 graden terug. In de code was dat niet
te zien, op de render meteen.
