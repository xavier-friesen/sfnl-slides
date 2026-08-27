# De maatstaf voor `online-design`

Eén gebouwd SFNL-scherm, gerenderd in beide thema's op twee breedtes. Dit is waar de lat ligt.

```
kwartaalstand.frag.html      het fragment: alleen de pagina, zoals je hem schrijft
png/contactblad.png          de vier renders naast elkaar — hier kijk je naar
png/pagina-licht-1440.png    de losse renders, om een detail na te kijken
png/pagina-donker-1440.png
png/pagina-licht-420.png
png/pagina-donker-420.png
```

Herbouwen:

```bash
python scripts/online/bouw.py assets/online/maatstaf/kwartaalstand.frag.html \
    --uit /tmp/kwartaalstand.html --artifact
python scripts/online/render.py /tmp/kwartaalstand.html --uit assets/online/maatstaf/png
python scripts/online/qa_online.py /tmp/kwartaalstand.html
```

Het gebouwde HTML-bestand staat er met opzet niet bij: het is 247 kB, waarvan 197 kB ingesloten
letters, en het is uit het fragment in één opdracht terug te maken.

## Waarvoor dit de lat is

- **Dat een scherm in beide thema's hetzelfde ding is.** Leg de twee kolommen van het contactblad
  naast elkaar: de koprand is in beide standen identiek oranje met navy inkt, en alles eromheen
  klapt om. Dat ene onveranderlijke element is wat de twee standen aan elkaar knoopt. De reden
  staat in `reference/online-vormentaal.md` §2: een vol merkvlak wisselt niet mee met het thema,
  want oranje is een lichte kleur in beide thema's.
- **Dat de maatladder niet meegroeit.** Vergelijk 1440 en 420: de titel staat op beide 30 px, de
  body op 16, de as-labels van de grafiek op 13. Wat verandert is het aantal kolommen, de marge
  en de regelval — niet één lettermaat.
- **Hoe je een grafiek bouwt die zijn letters niet meeschaalt.** De plot is SVG met
  `preserveAspectRatio="none"`; de as-labels, de punten en de legenda staan in HTML rond en over
  de plot heen. Op 420 px is de plot 40 procent smaller en zijn de labels precies zo groot.
- **Hoeveel er op één scherm past.** Drie kerncijfers, één grafiek, één tabel van vier rijen, één
  uitspraak. Op 1440 px is dat 2029 px hoog, dus ongeveer twee vensters. Wie er twee grafieken en
  acht tegels bij zet, maakt vier vensters en dan leest niemand de onderste twee.
- **Hoe een tabel zich op een smal scherm gedraagt.** In een `.tabelhouder` met `tabindex="0"` en
  een `aria-label`, met de titel als `.label` erbóven en niet als `<caption>` erin, en met de
  bronregel die zegt dat hij schuift.
- **Waar een gat hoort te staan.** Twee `[MARKERINGEN]` — `[NAAM ASSESSOR]` en
  `[DATUM FONDSVERGADERING]` — staan er met opzet in. Zo hoort een onbekend feit eruit te zien.

## Waarvoor dit níet de lat is

- **Geen sjabloon.** Er is geen dashboardbibliotheek en deze compositie is er geen. Drie
  kerncijfers naast elkaar is niet *de* SFNL-kerncijferrij; het zijn er drie omdat er drie feiten
  waren. Wie dit natekent, kiest niet meer maar vult in.
- **Geen inhoud.** De cijfers, de gemeenten en het fonds zijn verzonnen voor deze proef. Er
  bestaat geen Outcomesfonds Jeugd met deze getallen; gebruik er niets uit.
- **Geen interactie-maatstaf.** De filterrij op de pagina is opgemaakt en filtert niet: hij toont
  hoe hij eruitziet en wat hij aan `aria-pressed` draagt. Wat een filter dóet, hoort uit de
  opdracht te komen.
- **Geen grafiekmethode.** Waarom hier een lijn staat en niet een staaf, hoe de hover werkt en
  wanneer het geen grafiek is maar een kerncijfer: dat staat in de `dataviz`-skill. Wat je hier
  ziet zijn de SFNL-parameters in die methode.
- **Geen drukwerk.** Dit scherm drukt netjes af via `scripts/gedeeld/naar_pdf.py`, en dat is een
  afdruk van een scherm. Moet het gedrukt worden, dan is dat `ontwerp-documenten` — daar zit de
  snijrand, het formaat en de katernsom.

## Wat er op de renders is gerepareerd, en in welke ronde

De maatstaf is niet in één keer goed geweest, en dat hoort in de maatstaf te staan. Wat de eerste
renderronde en `qa_online.py` opleverden:

| bevinding | hoe gevonden | waar de reparatie staat |
|---|---|---|
| het oranje "NL" van het logo op een oranje band: contrast 1,00, en niemand zag dat het weg was | `qa_online.py`, niet de render | `stijl.css` §7.11 — op een vol merkvlak is het logo éénkleurig |
| `.kicker` in `var(--accent)`: 2,51 op wit en 6,29 op navy | `qa_online.py` | `stijl.css` §7.2 — het merkvierkant vóór de regel, tekst op de stille inkt |
| een oranje band van 190 px met vier woorden erin, door dubbele verticale marge | de render op 1440 px | `stijl.css` §7.10 — `.koprand > .dek { padding-block: 0 }` |
| een tintpaneel van 16 procent viel op donker samen met de grond | de render, donker | `stijl.css` §1 — 32 procent, met de meting erbij |
| de rasterlijn van de grafiek was op donker luider dan de tabelregel op licht | de twee renders naast elkaar | `stijl.css` §1 — `--lijn` en `--rasterlijn` gesplitst |
| een stompje zware streep onder elk rijlabel van de tabel | de render op 1440 px | `stijl.css` §7.9 — `thead th` in plaats van `th` |
| de `<caption>` liep op 420 px de scrollport uit | de render op 420 px | `stijl.css` §7.9 — de titel als `.label` boven de houder |
| vijf punten op de lijn, vier labels op de as | de render | het fragment |
| `€ 1.02 mln` met een punt in plaats van een komma | de render | het fragment |
