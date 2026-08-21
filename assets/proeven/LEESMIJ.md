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
| `11-poppend-vol-label-wit-paneel` | Dezelfde vier meetdoelen als `02`, maar met een wit paneel en een haarlijn in de hue van de rij in plaats van de accenttint. Gemeten: 76 procent wit, 9 procent tint, 15 procent verzadigd. Dit is het poppende register, en sinds 21 augustus 2026 de default. |
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

**En diezelfde dag is de default teruggedraaid, op een echt deck in plaats van op deze proef.**
`260821_Procesanalyse_ZK`, 26 slides, gebouwd met deze skill en met "met kleur" als keuze van de
gebruiker: op 12 van de 20 contentslides een volle hue als label met datzelfde accent op
containersterkte als paneel eronder — 13 keer grapefruit op 9000, 7 keer oranje op 12000, royal,
sky en emerald op 10000. Afgekeurd op de render, met één zin: dit hoort te poppen, en die
lichtgroene, lichtrode en lichtblauwe vlakken horen alleen in een deck waar iemand expliciet om
een ingetogen stijl heeft gevraagd.

**En daar is één render bij gekomen, want een register dat je niet kunt zien is een intentie.**
`11-poppend-vol-label-wit-paneel` is dezelfde vier meetdoelen als `02`, in dezelfde maten en met
dezelfde hues, maar in het poppende register: het rijlabel staat vol, het paneel ernaast is wit met
een haarlijn van 1pt in de hue van de rij, en het gewichtslabel draagt die hue in de letter. Naast
elkaar zijn dit de twee kleurregisters, en op de keuzekaart staan ze dan ook als de twee opties van
besluit 2.

De meting van de twee, in dezelfde ronde als de render (LibreOffice 24.2.7.2, 1921 px):

| render | register | wit | tint | verzadigd |
|---|---|---|---|---|
| `11-poppend-vol-label-wit-paneel` | poppend | 76 | 9 | 15 |
| `02-vier-hues-volle-rijlabels-14procent` | ingetogen | 80 | 6 | 14 |
| `260821_Procesanalyse_ZK` slide 6 | ingetogen, over de hele slide | 58 | 30 | 12 |

Wat die drie regels samen zeggen, en het is niet wat je zou verwachten: op één slide zijn de twee
registers in de meting bijna niet te onderscheiden — 76/9/15 tegen 80/6/14. De tint van `02` is zó
licht dat hij als wit meet. Het verschil ontstaat op de slide waar het paneel het grootste vlak van
de compositie is, en dat is ZK slide 6: vier volle labels van een derde breedte met vier
pastelpanelen van twee derde ernaast, en dan staat de deck op 58 procent wit met 30 procent tint. De
regel uit §4 hangt dus niet aan de alpha alleen maar aan het oppervlak dat hem draagt, en dat is
precies de reden dat de weigering in `shapes.py` op de vulling zit en niet op een percentage: wie
per rij een paneel tint, weet tijdens het bouwen niet dat hij bij de dertig procent uitkomt.

Wat er daarop is veranderd, en het is meer dan een default:

- Besluit 2 heeft nu eerst een **kleurregister** — poppend (default) of ingetogen — en alleen de
  gebruiker kiest ingetogen. "Kies jij maar" is daar geen vrijbrief voor pastel.
- In het poppende register is de default gevuldheid **met kleur** in plaats van weinig accent.
  Weinig accent bleef de default in het ingetogen register.
- De accenttint van 9000 tot 14000 is het instrument van het ingetogen register geworden, en
  `shapes.py` weigert hem daarbuiten. Navy op 7000 blijft de neutrale container en mag overal.

Wat deze zes renders daar niet over zeggen: ze zijn gebouwd met één slide inhoud, en de
pastelstapeling die de deck afkeurde ontstaat pas over 26 slides. Dat is de les die de proef zelf
niet kon geven — een gevuldheid die op één slide het beste leest, is niet dezelfde als de
grondtoon die een deck heel houdt.

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
