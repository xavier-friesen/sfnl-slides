# assets/folders/maatstaf/ — waar de lat ligt

Vier pagina's, gebouwd met deze skill, gerenderd met `scripts/folders/render.py`. Ze zijn niet om
na te tekenen maar om te weten wat "af" betekent. De bron van dezelfde vier staat in
`assets/folders/voorbeeld/`, als kale fragmenten.

| bestand | wat het laat zien |
|---|---|
| `00-contactblad.png` | de vier als spreads: 1 alleen, dan 2-3, dan 4. Kijk hier áltijd eerst naar |
| `01-omslag.png` | een omslag zonder foto: het huisverloop, één tonale bol, displaymaat, en drie labelblokken onderaan |
| `02-tekstpagina.png` | het gewone register: watermerkcijfer, chapeau, twee uitgevulde kolommen met aanheffen, een uitspraak, een feitenstrip |
| `03-kaarten-en-tabel.png` | drie kaarten op het verloop met gelijke hoogte, twee kolommen proza, een tabel naast een mintpaneel |
| `04-kleurpagina.png` | een heel blad in mint met een aflopende oranje band onderaan, genummerde badges, en het logo op de band |

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

Ze zijn opnieuw te maken uit `assets/folders/voorbeeld/`:

```bash
cp assets/folders/voorbeeld/*.dc.html <werkmap>/
python scripts/folders/bouw.py <werkmap> --uit wie-betaalt-de-preventie.html
python scripts/folders/render.py <werkmap>/wie-betaalt-de-preventie.html
```
