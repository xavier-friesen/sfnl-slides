# assets/fonts/ — fontbestanden voor de MÉTING

Deze map is de eerste plek waar `find_font_file()` in `scripts/_deck.py` zoekt. Wat hier
staat, kunnen `qa_fit.py`, `qa_text.py` en `fit_title.py` echt meten in plaats van te
schatten — op elke machine, ook in een Linux-sandbox of Cowork.

De map is nu leeg, en dat is een keuze, niet een vergissing:

| Familie | Licentie | Mag mee in de plugin |
|---|---|---|
| Gotham Bold | commercieel (Hoefler&Co) | **nee** — nooit meeleveren |
| Montserrat, Montserrat Light, Montserrat SemiBold | SIL Open Font License 1.1 | ja, met de OFL-tekst erbij |
| Lato, Lato Light | SIL Open Font License 1.1 | ja, met de OFL-tekst erbij |

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
  Dat is te dragen zolang je de tekenbudgetten uit `reference/layouts.md` aanhoudt en een
  titel korter schrijft in plaats van een font te verkleinen.

Ontbreken de fonts op een Linux-machine, dan substitueert de renderer ze. Een
fontconfig-alias maakt die render dichter bij het echte deck (zie de remediatieregel van
`preflight.py`), maar het maakt de meting niet exact: fit-oordelen uit zo'n render zijn
indicatief, compositie-oordelen zijn wél geldig.
