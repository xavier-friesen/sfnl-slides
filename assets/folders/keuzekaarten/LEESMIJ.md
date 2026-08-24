# assets/folders/keuzekaarten/ — het beeld bij het vragenvuur

`vragenvuur.png` hoort bij stap 1 van de SKILL. Vier besluiten, per besluit de opties naast
elkaar als echt gezet voorbeeld met de meting eronder.

**Stuur het bestand, lees het niet.** Dan kost het geen tokens en ziet de gebruiker waar hij
tussen kiest in plaats van vier woorden. Stel de vragen daarna met `AskUserQuestion` en gebruik
de optienamen van de kaart, zodat het beeld en de vraag hetzelfde heten.

Hij wordt gerenderd uit `assets/folders/stijl.css` en niet met de hand getekend. Verandert de
maatladder of een kleur, dan is de kaart één aanroep later weer waar:

```bash
python scripts/folders/keuzekaart.py
```

Dat is onderhoud, geen bouwstap. Een getekende kaart loopt achter zonder dat iemand het merkt, en
dan kiest de gebruiker iets anders dan hij krijgt.
