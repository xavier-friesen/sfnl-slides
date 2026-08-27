# assets/documenten/fonts/ — de ingesloten letters

`fonts.css` draagt Montserrat en Lato als `@font-face` met een `data:`-URI. Gegenereerd door
`scripts/documenten/haal_fonts.py`; niet met de hand bijwerken.

**Deze map heet `documenten/` maar is inmiddels van drie skills.** Naast `fonts.css` voor de
twee HTML-drukroutes zijn de losse woff2-bestanden hiernaast de **metriekbron** van
`sfnl-infographic`: `vind_font()` in `scripts/infographic/svg.py` leest ze met fontTools, want
een woff2 is een gecomprimeerde TrueType. Daardoor breekt een infographic uit de doos op echte
metriek af, ook op een machine zonder systeemfonts en zonder netwerk, en `render_svg.py` sluit
`fonts.css` in zodat zijn render dezelfde letters zet als een document. Twee dingen om te weten
als je hier iets verandert: het is de **latin-subset**, dus het promillageteken zit er niet in
en wordt als cijferbreedte geschat, en Montserrat is **variabel met standaardgewicht 100** —
`svg.py` instantieert het op 300 en 600, want de rauwe `hmtx` is Thin en dat is vier procent op
de regel. Verhuist deze map, dan verhuizen `INGESLOTEN_MAP` in `svg.py` en `FONTS_CSS` in
`render_svg.py` mee.

**Waarom ingesloten en niet van Google Fonts.** Drie dingen gaan anders mis, en alle drie stil:

1. De render valt terug op Helvetica zodra Chromium geen internet heeft. De eerste proefdocument van
   deze skill kwam er zo uit, en dan meet je de verkeerde regelafbreking en beoordeel je de
   verkeerde vorm.
2. De PNG- en PDF-export van het design-canvas kan een Google Font niet meenemen; geëxporteerde
   tekst valt terug op de systeemletter.
3. Een document dat alleen mét internet goed staat, is geen bestand maar een verzoek.

**Licentie.** Montserrat en Lato staan onder de SIL Open Font License 1.1, dus meeleveren en
insluiten mag, met de licentietekst erbij. `OFL-Montserrat.txt` en `OFL-Lato.txt` staan hiernaast
en horen mee te reizen met elke kopie. **Gotham Bold is commercieel en gaat deze repo nooit in.**
Montserrat ExtraBold is de substituut, en dat is niet gekozen maar overgenomen: het SFNL-drukwerk
zelf zet zijn display-regels al in Montserrat ExtraBold — gemeten in de casespread Civitates.

**Wat erin zit.** Alleen de `latin`-subset, negen sneden in zes faces: Montserrat komt als één
variabel bestand dat het hele bereik 300–800 dekt, Lato als vijf statische sneden (300, 400, 700
en twee cursieven). Samen 146 kB woff2, 197 kB als base64-CSS. Vier keer hetzelfde
Montserrat-bestand insluiten was de eerste versie en kostte 258 kB voor niets.

**Wat het kost in de PDF.** Chromium sluit het variabele Montserrat als Type3 in, dus een
drukkerij ziet daar geen normale lettertypenaam. Lato komt wel gewoon als Lato-Light mee. De PDF
drukt en de tekst is te selecteren; het staat in de SKILL onder Opleveren zodat je het kunt melden.

Opnieuw ophalen:

```bash
python scripts/documenten/haal_fonts.py
python scripts/documenten/haal_fonts.py --controleer
```
