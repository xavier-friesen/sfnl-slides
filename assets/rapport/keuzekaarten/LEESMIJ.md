# De keuzekaarten

Drie beelden die met het vragenvuur meegaan. Ze horen **gestuurd** te
worden en niet gelezen: dan kosten ze geen tokens en ziet de gebruiker
waar hij tussen kiest in plaats van vier woorden.

| bestand | wat erop staat | bij welk besluit |
|---|---|---|
| `modellen.png` | één tekstpagina per layoutmodel, op dezelfde tekst, met de kolommaat en de gemeten tekens per regel eronder | besluit 1, het model |
| `registers.png` | de eerste twee pagina's per kleurregister | besluit 2, het register |
| `openers.png` | de drie manieren waarop een hoofdstuk begint, met wat elk kost | besluit 4, de hoofdstukopener |

## Hoe ze gemaakt zijn

```bash
python scripts/rapport/keuzekaart.py
python scripts/rapport/keuzekaart.py --alleen modellen
```

Het script bouwt elke variant **echt**, via dezelfde route als een echt
rapport: `lees_docx.py`, dan `bouw.py`, dan de gezette pagina's naast
elkaar. Dat is bewust duur. Een kaart die met de hand is nagemaakt kan
iets beloven wat de zetmotor niet doet, en dan is de kaart erger dan
geen kaart.

Verandert er een model, een register of een opener, dan bouw je ze
opnieuw. Dat is onderhoud en geen bouwstap.
