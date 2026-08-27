# assets/fonts/ — fontbestanden voor de MÉTING

Deze map is de eerste plek waar `find_font_file()` in `scripts/_deck.py` zoekt, en ook de
eerste waar `vind_font()` in `scripts/infographic/svg.py` kijkt. Wat hier staat, kunnen
`qa_text.py`, `fit_title.py`, de fontmeting van `preflight.py` en de regelafbreking van de
infographicroute echt meten in plaats van schatten — op elke machine, ook in een
Linux-sandbox of Cowork.

**En let op waar de letters wél al staan.** `assets/documenten/fonts/` draagt Montserrat en
Lato als woff2, omdat `fonts.css` ze als data-URI insluit voor de twee HTML-drukroutes.
`svg.py` leest diezelfde bestanden als tweede keus, dus de infographicroute meet uit de doos
echt. Twee dingen die deze map daarnaast nog toevoegen: een **volledige** snede in plaats van
de latin-subset (het promillageteken zit niet in de subset), en een **statische** snede in
plaats van het variabele Montserrat, dat op `wght=100` staat en dus geïnstantieerd moet worden
op 300 of 600. Staat hier een `.ttf`, dan gaat die vóór.

Voor de deckroute — `qa_text.py` en `fit_title.py` — is die woff2 geen alternatief:
`_deck.py` zoekt op `.ttf`, `.otf` en `.ttc`.

De map is nu leeg, en dat is een keuze, niet een vergissing:

| Familie | Licentie | Mag mee in de plugin |
|---|---|---|
| Gotham Bold | commercieel (Hoefler&Co) | **nee** — nooit meeleveren |
| Montserrat, Montserrat Light, Montserrat SemiBold | SIL Open Font License 1.1 | ja, met de OFL-tekst erbij |
| Lato, Lato Light, Lato Semibold | SIL Open Font License 1.1 | ja, met de OFL-tekst erbij |

Wil je de meting echt maken in plaats van geschat: zet de `.ttf`/`.otf`-bestanden van
Montserrat en Lato hier neer, met hun `OFL.txt` ernaast. De scripts pakken ze op zonder
verdere configuratie — er is geen lijst om bij te werken. `preflight.py` meldt in
`fonts.found` per familie welk bestand het gevonden heeft.

Twee dingen om te weten:

- **Op een Office-machine staan Montserrat en Lato al**, maar niet in
  `C:/Windows/Fonts`: Office haalt ze als cloud font binnen naar
  `%LOCALAPPDATA%/Microsoft/FontCache/4/CloudFonts/<Familie>/`, met een nummer als
  bestandsnaam. `_deck.py` zoekt daar en leest de familie uit de nametable van het
  bestand — precies daarom stond er in de QA lang `fonts_measured: []` terwijl de render
  de fonts wél goed zette.
- **Gotham Bold zal vrijwel nooit meetbaar zijn.** Titelregels worden daar dus geschat.
  Dat is te dragen zolang je het tekenbudget van de titel aanhoudt — op 24pt Gotham Bold over
  12,52 in gaat er ongeveer 48 tekens op een regel (`skills/slides/SKILL.md`, stap 2) — en
  een titel korter schrijft in plaats van een font te verkleinen.

Ontbreken de fonts op een Linux-machine, dan substitueert de renderer ze. Een
fontconfig-alias maakt die render dichter bij het echte deck (zie de remediatieregel van
`preflight.py`), maar het maakt de meting niet exact: fit-oordelen uit zo'n render zijn
indicatief, compositie-oordelen zijn wél geldig.
