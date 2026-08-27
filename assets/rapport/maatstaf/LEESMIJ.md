# De maatstaf

Vier beelden uit één gezet rapport. Niet om na te tekenen maar om te
weten waar de lat ligt.

| bestand | wat |
|---|---|
| `00-contactblad.png` | het hele rapport als spreads: omslag alleen rechts, daarna 2-3, 4-5 |
| `01-omslag.png` | de omslag — opdrachtgever boven, titel in het midden, datum en logo onder |
| `02-hoofdstukopener.png` | een hoofdstuk dat opent met `nummer`: kicker, titel, watermerkcijfer half erachter |
| `03-tekstpagina-met-exhibit.png` | een tekstpagina met een exhibit: haarlijn, nummer, titel, beeld |

Gezet in het `kantlijn`-model, register `helder`, formaat `sfnl`, opener
`nummer`, met omslag en inhoudsopgave, dubbelzijdig.

## Hoe ze gemaakt zijn

De brontekst is `PROEF` uit `scripts/rapport/keuzekaart.py` — echte
SFNL-tekst en geen blindtekst, want op blindtekst zie je niet of de
zetting Nederlandse woorden aankan. Met een figuur erin: een vlak van
1200 × 640 px in mint, aangeleverd via `beeld.json` achter `b0009`, de
laatste regel van de eerste opsomming.

```bash
# de brontekst uit het script halen
python - <<'PY'
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location("kk", "scripts/rapport/keuzekaart.py")
m = importlib.util.module_from_spec(spec)
try: spec.loader.exec_module(m)
except SystemExit: pass
pathlib.Path("proef.md").write_text(m.PROEF, encoding="utf-8")
PY

python scripts/rapport/lees_docx.py proef.md --uit werk
# ontwerp.json schrijven met de besluiten hierboven, plus de omslagregels:
#   opdrachtgever "In opdracht van het ministerie van SZW", datum "maart 2025",
#   ondertitel "Een analyse van vijftien Nederlandse social impact bonds,
#   hun ontwerp en hun uitkomsten"
# beeld.json: [{"bestand": "figuur.png", "na": "b0009",
#               "bijschrift": "Verdeling van de vijftien bonds naar
#               opdrachtgever en jaar van start."}]
python scripts/rapport/bouw.py werk --uit maatstaf.html
python scripts/rapport/render.py werk/maatstaf.html --schaal 1.4
python scripts/rapport/render.py werk/maatstaf.html --pagina 1 --schaal 1.4
python scripts/rapport/render.py werk/maatstaf.html --pagina 3 --schaal 1.4
python scripts/rapport/render.py werk/maatstaf.html --pagina 4 --schaal 1.4
```

Vijf pagina's: omslag, inhoudsopgave, de hoofdstukopener, de tekstpagina
met het exhibit en de tabel, en een slotpagina.

Verandert er iets in `rapport.css` of in de zetmotor waardoor deze
beelden niet meer kloppen, dan maak je ze opnieuw. Een maatstaf die
achterloopt op wat de skill bouwt, is erger dan geen maatstaf.
