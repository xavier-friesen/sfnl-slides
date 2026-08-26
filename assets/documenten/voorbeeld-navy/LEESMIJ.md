# assets/documenten/voorbeeld-navy/ — het voorblad van een executive summary

Één artboard, en het staat er om één regel te laten zien: **een executive summary staat op navy.**
Dat is geen kleurvoorkeur maar de stand van dat stuk — het gaat naar een bestuurstafel — en de
skill vraagt er dus niet naar. Elk ander document staat in principe op oranje, tenzij de gebruiker
om iets anders vraagt.

Wat er verder aan te zien is: het skelet is letterlijk hetzelfde als dat van het oranje voorblad in
`../voorbeeld/Main.dc.html`. Dezelfde `.omslag` met zijn drie zones, dezelfde vier velden, dezelfde
twee maten. Alleen `data-veld` en `data-inkt` verschillen, plus de plek van de tonale bol. Dat is
precies wat een component oplevert dat in `stijl.css` staat in plaats van per document te worden
gecomponeerd: het kleurregister is een attribuut en geen herontwerp.

De render staat in `../maatstaf/07-voorblad-navy.png`.

```bash
cp assets/documenten/voorbeeld-navy/Main.dc.html <werkmap>/
python scripts/documenten/bouw.py <werkmap> --uit executive-summary.html
python scripts/documenten/render.py <werkmap>/executive-summary.html --schaal 1.2 --alleen-paginas
```
