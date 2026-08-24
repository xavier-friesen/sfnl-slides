# assets/folders/maatstaf/ — waar de lat ligt

Zes renders, gebouwd met deze skill met `scripts/folders/render.py`: vijf pagina's van één
folder op het SFNL-formaat, plus een tweeluik op A5 als tweede geval. Ze zijn niet om
na te tekenen maar om te weten wat "af" betekent. **Het zijn voorbeelden en geen sjablonen:** de
tekst erin is verzonnen om de vorm te kunnen laten zien, en zegt niets over wat er in een echte
folder hoort te staan. De bron van dezelfde vier staat in
`assets/folders/voorbeeld/`, als kale fragmenten.

| bestand | wat het laat zien |
|---|---|
| `00-contactblad.png` | de vijf als spreads: 1 alleen, dan 2-3, dan 4-5. Kijk hier áltijd eerst naar |
| `01-omslag.png` | de opening als **titelblad**: het huisverloop, één tonale bol, displaymaat, en drie labelblokken onderaan. Geen foto, want die was er niet |
| `02-tekstpagina.png` | het gewone register: watermerkcijfer, chapeau, twee uitgevulde kolommen met aanheffen, een uitspraak, een feitenstrip |
| `03-titelbalk-en-infographic.png` | een `.titelbalk` in violet om één pagina apart te zetten — het derde gebruik van de band, niet de dektitel en niet een hoofdstuk — met een infographic als drager in een `.beeldkader` op schaal 1:1 |
| `04-kaarten-en-tabel.png` | drie kaarten op het verloop met gelijke hoogte, twee kolommen proza, een tabel naast een mintpaneel |
| `05-kleurpagina.png` | een heel blad in mint met een aflopende oranje band onderaan, genummerde badges, en het logo op de band |
| `06-tweeluik-a5.png` | de korte route: twee pagina's op A5 met de **titelbalk** als opening, en de body op 11 pt in plaats van 10. Bron in `assets/folders/voorbeeld-a5/` |

## Wat deze vier hebben gekost

Ze zijn niet in één keer goed geweest, en de fouten staan in `folders-vormentaal.md` omdat ze
allemaal de eerste inval waren:

- De eerste render kwam in Helvetica uit de loop, want Chromium had geen internet en de letters
  kwamen van Google Fonts. Dat is de reden dat ze nu ingesloten zijn.
- Het logo had een `viewBox` van 384 en sneed de laatste letter van FINANCE af, zonder dat de
  markup er verkeerd uitzag.
- De drie kaarten op pagina 3 waren 232, 204 en 204 px hoog, want de rij stond op
  `align-items: start`. Daar is `kolommen--gelijk` voor.
- Alle vier de pagina's hadden een gat in het midden van 224 tot 372 px, van
  `justify-content: space-between` en van één `margin-top: auto` te veel. Dat was het duidelijkst
  zichtbare defect van de hele folder en het is de reden dat `qa_folder.py` nu `gat` meet.
- De kaarttekst stond wit op oranje, contrast 2,6. Nu is navy de inkt op elk oranje veld.
- De infographic op pagina 3 voerde zijn eigen lettermaten in — 12, 13 en 15 px binnen de SVG,
  naast de zes van de ladder. Een `<svg>` op schaal 1:1 rendert zijn `font-size` in dezelfde px
  als de pagina, dus hij hoort dezelfde ladder te gebruiken. `qa_folder.py` telde acht maten.
- Diezelfde pagina hield op 63 procent op. Het beeld is de drager, dus die mocht groeien: de
  viewBox van 268 naar 372 in de hoogte, met de breedte op 680 zodat de schaal 1:1 bleef en de
  letters binnen de SVG niet meegroeiden.

Ze zijn opnieuw te maken uit `assets/folders/voorbeeld/`:

```bash
cp assets/folders/voorbeeld/*.dc.html <werkmap>/
python scripts/folders/bouw.py <werkmap> --uit wie-betaalt-de-preventie.html
python scripts/folders/render.py <werkmap>/wie-betaalt-de-preventie.html
python scripts/folders/qa_folder.py <werkmap>/wie-betaalt-de-preventie.html
```
