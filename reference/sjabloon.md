# Het SFNL-sjabloon

Feiten, geen voorschriften. Wat hier staat is wat het sjabloon doet en waar het je laat
vallen. Wat je ermee componeert staat in `vormentaal.md`.

Slideformaat: 13,333 × 7,5 inch. Alle maten in inch, tenzij anders vermeld. Eén inch is
914400 EMU.

## Welke layout waarvoor

Het sjabloon heeft 27 layouts, genummerd 1 t/m 17, 19 t/m 22 en 25 t/m 30. De nummers 18, 23
en 24 zijn eruit gehaald en de gaten zijn onschadelijk. `add_slide.py` verwacht de bestandsnaam,
dus `slideLayout19.xml`.

| Layout | Naam | Waarvoor |
|---|---|---|
| 19 | Titel, subtitel | **De contentslide.** Titel, optionele subtitel, een lege contentzone die je zelf componeert. Begin hier. |
| 20 | 1_Titel, subtitel, tekst | Één tekstplaceholder over de volle contentzone. Voor een slide waar doorlopende tekst de vorm is. |
| 21 | Titel, subtitel, twee tekstvakken | Twee kolommen over de volle hoogte. |
| 22 | 1_Titel, subtitel, twee tekstvakken | **De layout voor het tweeluik.** Twee kolommen met een geërfde kop per kolom. Die kop mag je herkleuren en verzwaren: 18pt Montserrat SemiBold met `spc="100"` in de hue van de kolom. Zo krijg je een gekleurde kop zonder een gevulde balk te tekenen. Alle vijf de winnende decks gebruiken deze layout. |
| 17 | Leeg | Blanco canvas: geen placeholders, geen header, geen dash. Voor full-bleed beeld of een schema over de volle hoogte. Draagt de slide een gewone titel, dan is het 19. |
| 1 | 1_Titelslide | Cover met het 2×2 kleurraster, foto rechtsboven, witte logokaart over het midden. |
| 4 | 7_Titelslide | Cover met een titel over de volle breedte. |
| 5 | Quote | Citaat over een foto, met de oranje band van de layout eronder. |
| 2, 3 | 5_ en 6_Titelslide | Oranje outro met logo. Afsluiter van een extern deck. |
| 6 t/m 16 | *_sectieslide_stijl1 | Sectiedividers met foto. Elf varianten die alleen in fotokeuze en compositie verschillen. |
| 25 t/m 30 | *_sectieslide_stijl2 | Agenda's en opsommingen; de lijst zit in idx 11. |

## De placeholders per layout

Op leesvolgorde, niet op idx-volgorde. Vul met `set_text.py`; wat je leeg laat haalt
`clean.py` eruit.

| Layout | idx | Rol | Doos (`x, y · b × h`) |
|---|---|---|---|
| 19, 20, 21, 22, 5 | 0 | titel, ALL CAPS | `0.48, 0.60 · 12.52 × 0.37` |
| 19, 20, 21, 22, 5 | 1 | subtitel, één zin | `0.48, 1.04 · 12.52 × 0.63` |
| 20 | 10 | contentzone als tekst | `0.48, 1.93 · 12.52 × 5.00` |
| 21 | 12 | **linker** kolom | `0.48, 1.96 · 5.91 × 5.00` |
| 21 | 13 | **rechter** kolom | `6.82, 1.96 · 5.91 × 5.00` |
| 22 | 13 | **linker** kolomkop | `0.48, 1.93 · 5.91 × 0.37` |
| 22 | 12 | **rechter** kolomkop | `6.82, 1.93 · 5.91 × 0.37` |
| 22 | 14 | linker kolomtekst | `0.48, 2.46 · 5.91 × 4.50` |
| 22 | 15 | rechter kolomtekst | `6.82, 2.46 · 5.91 × 4.50` |
| 1 | 14 | dektitel, ALL CAPS, één regel | `7.63, 5.79 · 5.33 × 0.56` |
| 1 | 13 | klant en datum | `7.63, 6.51 · 4.88 × 0.61` |
| 4 | 10 | dektitel, ALL CAPS, één regel | `-0.01, 4.22 · 13.32 × 0.63` |
| 6 | 14 | hoofdstukkop | `5.90, 1.57 · 5.96 × 0.56` |
| 6 | 11 | hoofdstukoverzicht | `5.90, 2.39 · 5.96 × 4.40` |
| 7 t/m 16 | 14 | hoofdstukkop | `6.07, 5.79 · 5.96 × 0.56` |
| 7 t/m 16 | 13 | ondersteunende regel | `6.06, 6.54 · 5.96 × 0.61` |
| 25 t/m 30 | 0 / 1 / 11 | kop / subregel / de lijst | `5.25, 1.63` / `5.25, 2.20` / `5.33, 3.04 · 7.41 × 3.51` |
| 2, 3, 17 | — | geen placeholders | |

## De contentzone

Op layout 19 t/m 22 is de zone waarin je zelf componeert:

```
x 0.48    y 1.93    b 12.52    h 5.00
rechts 13.00        onder 6.93
```

In EMU: `x 438912, y 1764792, b 11448288, h 4572000`.

Boven `y = 1.93` staat de geërfde header: de titel, de subregel en de oranje dash op
`y = 1.72`. Daar tekent de bouwer nooit iets. De dash wordt ook nooit nagetekend; hij komt uit
de layout en staat er al.

Op layout 17 is er geen header en geldt het hele canvas:

```
x 0.36    y 0.40    b 12.64    h 6.57
rechts 13.00        onder 6.97
logo 0.36, 7.07 · 1.10 × 0.29     paginanummer 12.60, 7.12 · 0.62 × 0.24
```

De linkermarge 0,36 lijnt uit met het logo en 0,48 met de contentlayouts. Staat de slide
tussen contentslides, kies dan 0,48.

## Kolomrasters

Voor eigen vormen in de contentzone:

| Kolommen | x-posities | Breedte | Goot |
|---|---|---|---|
| 2, gevuld | 0.48, 6.86 | 6.14 | 0.24 |
| 2, proza | 0.48, 6.82 | 5.91 | 0.43 |
| 3 | 0.48, 4.65, 8.82 | 3.94 | 0.24 |
| 4 | 0.48, 3.61, 6.74, 9.87 | 2.89 | 0.24 |

De goot hangt af van de vulling. Bij **gevulde** blokken doet de vulling het scheidingswerk, dus
0,20 tot 0,24 in is genoeg — een bredere goot maakt het raster los. Bij **ongevulde**
prozakolommen heeft de tekst die lucht wél nodig; dan is 0,43 in de maat, en dat is precies wat
layout 21 en 22 zelf gebruiken (5,91 op x 0,48 en x 6,82). Bouw je náást een placeholder van die
layouts, volg dan hun maat.

Voor *n* elementen met goot *g*: breedte is `(12.52 - g × (n - 1)) / n` en element *i* staat op
`0.48 + i × (breedte + g)`.

Voor *n* elementen over de volle contentbreedte met een goot *g*: breedte is
`(12.52 - g × (n - 1)) / n` en element *i* staat op `0.48 + i × (breedte + g)`.

## Tekstinsets

Een vak met een vulling krijgt insets `l 0.2, r 0.2, t 0.15, b 0.15`. Een tekstvak zonder
vulling — een label, een getal, een voetnoot, een losse regel — krijgt insets 0, want dan
lijnt de tekst uit met de vakrand en dus met de rest van de kolom.

## Kleur

Uitsluitend `schemeClr` met transformaties, nooit `srgbClr`. Binnen `<a:schemeClr>` komt
`satMod` vóór `lumMod`, en `lumMod` vóór `lumOff`.

| Kleur | Themaslot |
|---|---|
| oranje | `accent1` |
| grapefruit | `accent2` |
| royal | `accent3` |
| sky | `accent4` |
| emerald | `accent5` |
| navy | `dk2` |
| wit | `lt2` |
| grijs (voetnoot) | `tx1` met `lumMod 65000`, `lumOff 35000` |

### Een lichte vulling maak je met alpha

Niet met `lumMod`. In de vijf decks die de blinde vergelijking wonnen komt `lumMod` geen enkele
keer voor: élke lichte vulling is de volle kleur met `<a:alpha>` erover.

```xml
<a:solidFill><a:schemeClr val="accent5"><a:alpha val="10000"/></a:schemeClr></a:solidFill>
```

Per hue gekalibreerd, want navy is veel donkerder dan emerald:

| hue | alpha voor een container |
|---|---|
| navy (`dk2`) | 7000 |
| royal, sky, emerald | 10000 |
| grapefruit | 9000 |
| oranje | 12000 |

Navy op 7000 is de **neutrale container**: koel, kleurloos, en de default zodra er niets te
onderscheiden valt. Boven ongeveer 14000 wordt een container een kleur in plaats van een
achtergrond — dat mag, maar dan betekent het vlak iets.

Waarom dit uitmaakt: `lumMod 20000` / `lumOff 80000` levert een vlak dat één stap te donker is
en daardoor als eigen kleur meedoet. Bij navy komt daar `#C6C3ED` uit, een verzadigd lavendel
dat naast geen van de zes merkkleuren staat, en daarvoor moest een apart verbod bestaan. Met
alpha is die uitzondering niet meer nodig. Warmgrijs (`accent1` met `satMod`) komt in geen
enkele winnende deck voor en kun je laten liggen.

### Contrast

**Op een volle vulling.** Dit is leesbaarheid, geen smaak.

| Vulling | Tekst |
|---|---|
| navy vol, royal vol | wit |
| oranje, grapefruit, sky, emerald vol | navy |

Wit op de lichte accenten haalt 2,0 tot 3,1 en is dus geen default. Eén uitzondering, nagemeten
in de sterkste referentieslide: vanaf ongeveer 40pt mag wit ook op emerald, oranje en sky, want
daar leest het cijfer als vorm en niet als tekst. Bewuste keuze, op de render te controleren.

**Als tekstkleur op wit.** Deze helft ontbrak, waardoor de tabel als verbod las en kleur alleen
in vlakken terechtkwam. Uitgerekende verhoudingen:

| kleur | op wit | mag dragen |
|---|---|---|
| navy | 15,3 | alles, ook een alinea |
| royal | 5,7 | alles, ook een alinea |
| grapefruit | 3,1 | een kop vanaf 18pt |
| oranje | 2,6 | displaymaat, of een kop vanaf 18pt |
| sky | 2,3 | idem |
| emerald | 2,0 | idem |

### Volgorde binnen de XML

Bindend, en het schema keurt het af als je het omdraait:

- in `<p:spPr>`: `xfrm` → `prstGeom` → vulling → `a:ln`
- in `<a:pPr>`: `lnSpc` → `spcBef` → `spcAft` → de bullet-elementen
- in `<a:rPr>`: `solidFill` vóór `a:latin`
- in `<a:schemeClr>`: `satMod` vóór `lumMod` vóór `lumOff`; `alpha` mag achteraan

### Vormen

Een `roundRect` zonder expliciete `adj` krijgt PowerPoints default van 16,67 procent van de
korte zijde. Een blok van 1 in hoog wordt dan een pil en een blok van 2,5 in een nette kaart:
vier verschillende radii in één deck zonder dat iemand er iets aan koos. Zet de radius
expliciet, absoluut in inch, en reken hem per vorm terug:

```
adj = 100000 × radius_in_inch / min(breedte, hoogte)
```

In de winnende decks staat de `adj` op 4000 tot 6000, wat bij die maten neerkomt op ongeveer
0,08 tot 0,12 in. Gebruik in de hele deck dezelfde absolute radius, ook als de blokken
verschillend hoog zijn.

Een lijn om een kaart heeft **dezelfde hue als de vulling**. Een grijze of contrasterende rand
is de Word-tabellook.

## Fonts

Toegestaan: Gotham Bold, Montserrat, Montserrat Light, Montserrat SemiBold, Lato Light.

Gotham Bold schrijf je nooit zelf; die komt uit de layout. Montserrat voor labels,
kolomkoppen en getallen. Lato Light voor lopende tekst. Montserrat Light voor een citaat.

## Valkuilen

Acht dingen die stil misgaan en die je niet kunt afleiden.

1. **Calibri.** Een eigen vorm erft `otherStyle`, en dat is 18pt `+mn-lt` = Calibri. Élke run
   in een eigen vorm draagt dus een expliciete `<a:latin typeface="..."/>`. Vergeet je dat,
   dan staat er Calibri op de slide en zie je dat pas op de render.
2. **`schemeClr`, niet `srgbClr`.** Een hardgecodeerde hex drijft weg van het thema zodra
   iemand het sjabloon bijwerkt.
3. **Eén `<a:p>` per lijstitem.** Nooit twee items in één alinea met een regeleinde ertussen;
   dan werkt de alinea-afstand niet en breekt de tekst verkeerd.
4. **Géén `xml:space="preserve"` op `<a:t>`.** Dat is WordprocessingML; in DrawingML keurt het
   schema het af en dan valideert de deck niet meer. Voor- en achterloopruimte blijft in
   DrawingML gewoon staan. (Deze naslag schreef eerder het omgekeerde voor.)
5. **`<a:noAutofit/>` in élke `<a:bodyPr>` die je zelf schrijft.** Zonder die keuze mag
   PowerPoint de tekst schalen, en één vak op 90 procent haalt een hele rij uit de lijn. Past
   de tekst niet, dan wordt het vak groter of de tekst korter — nooit het font kleiner.
6. **Entiteiten voor de typografische aanhalingstekens** in de XML.
7. **`idx 0` bestaat niet op elke layout.** Op de covers (1, 4) en de sectiedividers (6 t/m 16)
   is er geen titelplaceholder met idx 0; de kop is daar idx 10 of idx 14.
8. **Idx-volgorde is geen leesvolgorde.** Op layout 21 is idx 12 de linkerkolom, maar op
   layout 22 is idx 13 de linkerkolom en idx 12 de rechter. De twee tweekolomslayouts hebben
   de omgekeerde conventie. Controleer de doos, niet het nummer.
9. **Een negatieve `axId` in een grafiek nooit repareren.** Dat is geldige OOXML; verander je
   hem, dan opent PowerPoint het bestand niet meer.

En één procesval die geen XML is: `python-pptx` herschrijft de deck bij het opslaan, en dat
sloopt de grafieken die `add_chart.py` heeft toegevoegd. `add_chart.py` en `add_table.py` gaan
dus ná de laatste `pack`, niet ervoor.
