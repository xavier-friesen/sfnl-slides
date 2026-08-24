# assets/folders/fonts/ — de ingesloten letters

`fonts.css` draagt Montserrat en Lato als `@font-face` met een `data:`-URI. Gegenereerd door
`scripts/folders/haal_fonts.py`; niet met de hand bijwerken.

**Waarom ingesloten en niet van Google Fonts.** Drie dingen gaan anders mis, en alle drie stil:

1. De render valt terug op Helvetica zodra Chromium geen internet heeft. De eerste proeffolder van
   deze skill kwam er zo uit, en dan meet je de verkeerde regelafbreking en beoordeel je de
   verkeerde vorm.
2. De PNG- en PDF-export van het design-canvas kan een Google Font niet meenemen; geëxporteerde
   tekst valt terug op de systeemletter.
3. Een folder die alleen mét internet goed staat, is geen bestand maar een verzoek.

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
python scripts/folders/haal_fonts.py
python scripts/folders/haal_fonts.py --controleer
```
