# assets/folders/voorbeeld/ — vier pagina's zoals je ze schrijft

Dit is de vorm waarin je zelf een pagina schrijft: alleen het `<div class="pagina">`-blok, zonder
`<head>`, zonder `<style>` en zonder de 200 kB ingesloten letters. `bouw.py` stempelt dat erin.

De gerenderde versie staat in `assets/folders/maatstaf/`, met de fouten die eruit zijn gehaald.

| bestand | pagina |
|---|---|
| `Main.dc.html` | de opening als titelblad. Het eerste artboard moet Main heten; dat is een eis van de canvashelper |
| `Aanleiding.dc.html` | de tekstpagina |
| `Geldstroom.dc.html` | een `.titelbalk` om één pagina apart te zetten, met een infographic als drager |
| `Routes.dc.html` | kaarten plus tabel |
| `Programma.dc.html` | de kleurpagina met de aflopende band |

Let bij het lezen op vier dingen, want die zijn niet vanzelfsprekend:

1. **Aflopend werk staat buiten `.zetspiegel`**, als broer ervan. De marge zit op de zetspiegel
   en niet op het blad, precies zodat een aflopend vlak de rand kan raken.
2. **Klassen voor het systeem, inline styles voor het geval.** Het raster en de maatrollen zijn
   klassen; een specifieke breedte of afstand staat inline, want dat is wat het
   eigenschappenpaneel van het canvas bewerkt.
3. **De tekst staat letterlijk in de markup**, niet als variabele. Alleen dan kan de gebruiker hem
   in het canvas ter plekke overtypen.
4. **`data-volgnr` bepaalt de volgorde**, niet de bestandsnaam.
5. **`--balk` staat op de `.pagina`**, niet op de `.titelbalk`. De balk én de zetspiegel lezen
   dezelfde waarde, dus je noemt de bandhoogte maar één keer.
6. **De infographic is inline SVG op schaal 1:1** — `viewBox="0 0 680 372"` in een kader met
   `aspect-ratio: 680 / 372`. Alleen dan rendert de `font-size` binnen de SVG in dezelfde px als
   op de pagina en blijft hij op de ladder.
