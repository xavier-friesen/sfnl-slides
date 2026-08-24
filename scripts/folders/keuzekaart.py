#!/usr/bin/env python3
"""De keuzekaart voor het vragenvuur, gerenderd uit de echte stijl.

Vier besluiten, per besluit de opties naast elkaar als echt gezet voorbeeld,
met de meting eronder. De gebruiker ziet waar hij tussen kiest in plaats van
drie woorden te lezen.

Waarom dit een script is en geen plaatje in de repo dat iemand ooit heeft
getekend: de kaart wordt gerenderd uit `stijl.css`. Verandert de maatladder of
een kleur, dan is de kaart één aanroep later weer waar. Een getekende kaart
loopt achter zonder dat iemand het merkt, en dan kiest de gebruiker iets anders
dan hij krijgt.

Dit is onderhoud, geen bouwstap. Je draait hem als de stijl verandert, niet per
folder.

Gebruik:

    python keuzekaart.py
    python keuzekaart.py --uit ergens/kaart.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
from _browser import browser, wacht_op_letters  # noqa: E402

WORTEL = HIER.parent.parent
STIJL = WORTEL / "assets" / "folders" / "stijl.css"
FONTS = WORTEL / "assets" / "folders" / "fonts" / "fonts.css"
UIT = WORTEL / "assets" / "folders" / "keuzekaarten" / "vragenvuur.png"

KAART = """<!doctype html>
<html lang="nl"><head><meta charset="utf-8"><style>
{stijl}
body {{ background: #FFFFFF; margin: 0; padding: 34px 38px 30px; width: 1240px; }}
h1 {{ font-family: var(--display); font-weight: 800; font-size: 25px; color: var(--navy);
     margin: 0 0 4px; letter-spacing: -.01em; }}
.intro {{ font-family: var(--brood); font-size: 13px; color: var(--navy); opacity: .72;
          margin: 0 0 26px; max-width: 92ch; }}
.blok {{ margin-bottom: 26px; }}
.blok > h2 {{ font-family: var(--display); font-weight: 700; font-size: 12.5px;
             letter-spacing: .1em; text-transform: uppercase; color: var(--oranje);
             margin: 0 0 2px; }}
.blok > .vraag {{ font-family: var(--brood); font-weight: 700; font-size: 14px;
                 color: var(--navy); margin: 0 0 13px; }}
.opties {{ display: grid; gap: 16px; align-items: stretch; }}
.optie {{ display: flex; flex-direction: column; gap: 8px; }}
.proef {{ position: relative; overflow: hidden; height: 132px;
          box-shadow: inset 0 0 0 1px rgba(32,27,92,.22); background: #fff; }}
.proef > .in {{ position: absolute; inset: 0; padding: 12px 13px; }}
.naam {{ font-family: var(--brood); font-weight: 700; font-size: 12.5px; color: var(--navy); margin: 0; }}
.meet {{ font-family: var(--brood); font-weight: 300; font-size: 11.5px; color: var(--navy);
         opacity: .74; margin: 0; line-height: 15px; }}
.dft {{ display: inline-block; font-family: var(--display); font-weight: 700; font-size: 8.5px;
        letter-spacing: .1em; text-transform: uppercase; color: #fff; background: var(--navy);
        padding: 2px 6px; margin-left: 6px; vertical-align: 1px; }}
.mini {{ font-family: var(--brood); font-weight: 300; font-size: 4.6px; line-height: 6.4px;
         color: var(--navy); text-align: justify; hyphens: auto; }}
.minikop {{ font-family: var(--display); font-weight: 800; font-size: 9px; color: var(--navy);
            line-height: 1.1; margin: 0 0 4px; }}
.minilabel {{ font-family: var(--display); font-weight: 400; font-size: 5px; letter-spacing: .14em;
              text-transform: uppercase; color: var(--oranje); margin: 0 0 3px; }}
.g2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 7px; }}
.g3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; }}
</style></head><body>
<h1>Vijf besluiten v&oacute;&oacute;r de eerste regel tekst</h1>
<p class="intro">Elk besluit heeft een default. Volg je die, dan hoef je niets te motiveren.
Wijk je af, dan staat de reden bovenaan de outline. De vlakjes hieronder zijn echt gezet
in de folderstijl, op ware verhouding maar verkleind &mdash; het gaat om de verdeling, niet om de tekst.</p>
{blokken}
</body></html>
"""


def _lorem(n: int = 5) -> str:
    zin = ("Preventie loont, maar de opbrengst valt bij een andere partij dan die "
           "de investering doet. Zolang die twee boekhoudingen gescheiden blijven, "
           "blijft elk programma een pilot die na drie jaar stilvalt. ")
    return f'<p class="mini">{zin * n}</p>'


def _blok(nummer: str, vraag: str, opties: list[tuple[str, str, str, bool]]) -> str:
    kaarten = []
    for naam, proef, meting, default in opties:
        merk = '<span class="dft">default</span>' if default else ""
        kaarten.append(
            f'<div class="optie"><div class="proef"><div class="in">{proef}</div></div>'
            f'<p class="naam">{naam}{merk}</p><p class="meet">{meting}</p></div>')
    kol = f"grid-template-columns: repeat({len(opties)}, minmax(0, 1fr));"
    return (f'<div class="blok"><h2>{nummer}</h2><p class="vraag">{vraag}</p>'
            f'<div class="opties" style="{kol}">{"".join(kaarten)}</div></div>')


def bouw_html() -> str:
    stijl = STIJL.read_text(encoding="utf-8")
    if FONTS.exists():
        stijl = FONTS.read_text(encoding="utf-8") + "\n" + stijl

    kop = '<p class="minikop">Wie betaalt<br>de preventie?</p>'
    lab = '<p class="minilabel">Aanleiding</p>'

    blokken = [
        _blok("Besluit 1 &mdash; formaat", "Op welke maat wordt dit gedrukt of gelezen?", [
            ("SFNL-rapportformaat",
             f'<div style="height:100%;display:flex;gap:6px">'
             f'<div style="width:76px;height:100px;box-shadow:inset 0 0 0 1px rgba(32,27,92,.3);padding:6px">{lab}{kop}</div>'
             f'<div style="flex:1">{_lorem(3)}</div></div>',
             "210 &times; 275 mm &mdash; 794 &times; 1039 px. Het formaat van de jaarrapporten: "
             "iets breder dan A4 aanvoelt en korter, waardoor het als magazine leest.", True),
            ("A4",
             f'<div style="height:100%;display:flex;gap:6px">'
             f'<div style="width:71px;height:100px;box-shadow:inset 0 0 0 1px rgba(32,27,92,.3);padding:6px">{lab}{kop}</div>'
             f'<div style="flex:1">{_lorem(3)}</div></div>',
             "210 &times; 297 mm. Voor iets dat door de printer op kantoor moet, of dat "
             "als bijlage bij een aanbesteding gaat.", False),
            ("A5",
             f'<div style="height:100%;display:flex;gap:6px">'
             f'<div style="width:56px;height:80px;box-shadow:inset 0 0 0 1px rgba(32,27,92,.3);padding:5px">{lab}{kop}</div>'
             f'<div style="flex:1">{_lorem(2)}</div></div>',
             "148 &times; 210 mm. Een uitnodiging of programmaboekje &mdash; &eacute;&eacute;n "
             "kolom, grotere letter, minder woorden per pagina.", False),
            ("Liggende spread",
             f'<div style="height:100%;display:flex;align-items:center">'
             f'<div style="width:100%;height:64px;box-shadow:inset 0 0 0 1px rgba(32,27,92,.3);display:flex">'
             f'<div style="width:22px;background:var(--navy)"></div>'
             f'<div style="flex:1;padding:5px">{_lorem(2)}</div>'
             f'<div style="flex:1;padding:5px">{_lorem(2)}</div></div></div>',
             "420 &times; 275 mm. De dubbelpagina uit het rapport, voor &eacute;&eacute;n "
             "case of &eacute;&eacute;n verhaal over twee bladzijden.", False),
        ]),

        _blok("Besluit 2 &mdash; omvang", "Hoeveel pagina's, en telt de folder als spreads?", [
            ("Eén blad",
             f'<div style="height:100%;display:flex;justify-content:center">'
             f'<div style="width:76px;height:100px;box-shadow:inset 0 0 0 1px rgba(32,27,92,.3);padding:6px">{lab}{kop}{_lorem(1)}</div></div>',
             "Een uitnodiging, een one-pager. Alles moet op &eacute;&eacute;n vlak "
             "en er is geen tweede kans.", False),
            ("Vier pagina's",
             f'<div style="height:100%;display:flex;gap:4px;justify-content:center">'
             + "".join(f'<div style="width:36px;height:47px;box-shadow:inset 0 0 0 1px rgba(32,27,92,.28)"></div>' for _ in range(4))
             + '</div>',
             "Omslag, twee inhoudspagina's, achterkant. De gewone folder, en de default "
             "als de opdracht niets zegt.", True),
            ("Acht tot twaalf",
             f'<div style="height:100%;display:flex;gap:3px;flex-wrap:wrap;justify-content:center;align-content:center">'
             + "".join(f'<div style="width:26px;height:34px;box-shadow:inset 0 0 0 1px rgba(32,27,92,.28)"></div>' for _ in range(8))
             + '</div>',
             "Een samenvatting of proposal met hoofdstukken. Vanaf hier horen er "
             "kopregels en folio's op, en een inhoudsopgave loont.", False),
            ("Zestien of meer",
             f'<div style="height:100%;display:flex;gap:2px;flex-wrap:wrap;justify-content:center;align-content:center">'
             + "".join(f'<div style="width:19px;height:25px;box-shadow:inset 0 0 0 1px rgba(32,27,92,.28)"></div>' for _ in range(16))
             + '</div>',
             "Een rapport. Overweeg of dit niet in delen moet: zestien pagina's schrijven "
             "kost meer dan zestien pagina's opmaken.", False),
        ]),

        _blok("Besluit 3 &mdash; kleurregister",
              "Hoeveel kleur draagt de folder, en welk accent staat naast oranje?", [
            ("Wit met oranje accent",
             f'<div style="height:100%">{lab}{kop}<hr style="border:0;height:3px;width:38px;background:var(--oranje);margin:5px 0 6px">{_lorem(3)}</div>',
             "Wit papier, navy letter, oranje voor de labels en de streep. Het rustigste "
             "register en het meest gebruikt in het rapport.", True),
            ("Kleurvlakken als ritme",
             f'<div style="height:100%;display:flex;gap:5px">'
             f'<div style="flex:1">{lab}{kop}{_lorem(2)}</div>'
             f'<div style="width:52px;background:var(--mint-tint);padding:6px">{_lorem(2)}</div></div>',
             "Witte pagina's met hier en daar een heel vlak in mint, oranje of violet. "
             "Zo krijgt een folder van acht pagina's een ritme.", False),
            ("Oranje dominant",
             f'<div style="height:100%;margin:-12px -13px;padding:12px 13px;background:var(--verloop);color:var(--navy)">'
             f'<p class="minilabel" style="color:#fff;opacity:.85">Aanleiding</p>'
             f'<p class="minikop" style="color:#fff">Wie betaalt<br>de preventie?</p>'
             f'<div style="color:var(--navy)">{_lorem(2)}</div></div>',
             "Het huisverloop over hele pagina's. Krachtig op een omslag; de lopende tekst "
             "gaat er navy op, want wit haalt maar 2,6 contrast.", False),
            ("Navy dominant",
             f'<div style="height:100%;margin:-12px -13px;padding:12px 13px;background:var(--navy);color:#fff">'
             f'<p class="minilabel">Aanleiding</p>'
             f'<p class="minikop" style="color:#fff">Wie betaalt<br>de preventie?</p>'
             f'<div style="color:#fff">{_lorem(2)}</div></div>',
             "Donker en formeel. Voor een proposal of een bestuurlijke samenvatting; "
             "beeld werkt hier beter dan veel tekst.", False),
        ]),

        _blok("Besluit 4 &mdash; tekst tegenover beeld",
              "Draagt de tekst het verhaal, of het beeld?", [
            ("Tekstgedreven",
             f'<div style="height:100%">{lab}{kop}<div class="g2" style="margin-top:5px">{_lorem(4)}{_lorem(4)}</div></div>',
             "Twee of drie uitgevulde kolommen, een uitspraak, een tabel. 300 tot 400 "
             "woorden per pagina. Voor een samenvatting die alleen gelezen wordt.", False),
            ("Gebalanceerd",
             f'<div style="height:100%">{lab}{kop}'
             f'<div style="margin:5px 0 5px;height:34px;background:var(--navy-tint);'
             f'box-shadow:inset 0 0 0 1px rgba(32,27,92,.22);display:flex;'
             f'align-items:center;justify-content:center">'
             f'<span class="minilabel" style="margin:0;opacity:.7">Infographic</span></div>'
             f'<div class="g2">{_lorem(2)}{_lorem(2)}</div></div>',
             "Kolommen afgewisseld met kaarten, een tabel of een beeld. 150 tot 250 woorden "
             "per pagina. De gewone folder.", True),
            ("Beeldgedreven",
             f'<div style="height:100%;display:flex;flex-direction:column;gap:5px">'
             f'<div style="height:58px;background:var(--verloop)"></div>'
             f'<div>{kop}{_lorem(1)}</div></div>',
             "Grote vlakken, aflopende beelden, weinig woorden. 60 tot 120 per pagina. "
             "Werkt alleen met echt beeldmateriaal &mdash; zonder foto's wordt dit leeg.", False),
        ]),

        _blok("Besluit 5 &mdash; de opening",
              "Hoe komt de dektitel op de folder? Dit gaat over pagina 1, eenmalig.", [
            ("Titelblad",
             f'<div style="height:100%;display:flex;gap:7px;align-items:center">'
             f'<div style="width:70px;height:94px;background:var(--verloop);padding:7px 6px;'
             f'display:flex;flex-direction:column;justify-content:space-between">'
             f'<p class="minilabel" style="color:#fff;opacity:.85;margin:0">Uitnodiging</p>'
             f'<p class="minikop" style="color:#fff;font-size:10px;margin:0">Wie betaalt de preventie?</p>'
             f'<div style="display:flex;gap:2px;align-items:center">'
             f'<div style="width:7px;height:7px;border-radius:50%;background:#fff"></div>'
             f'<div style="width:7px;height:7px;background:#fff"></div></div></div>'
             f'<div style="width:70px;height:94px;box-shadow:inset 0 0 0 1px rgba(32,27,92,.3);'
             f'padding:6px;overflow:hidden">{lab}{_lorem(2)}</div>'
             f'<div style="flex:1"></div></div>',
             "Pagina 1 is helemaal de titel; de inhoud begint op pagina 2. Wat elk "
             "SFNL-drukwerk doet, en het kost een hele pagina.", True),
            ("Titelbalk",
             f'<div style="height:100%;display:flex;justify-content:center;align-items:center">'
             f'<div style="width:70px;height:94px;box-shadow:inset 0 0 0 1px rgba(32,27,92,.3);'
             f'display:flex;flex-direction:column;overflow:hidden">'
             f'<div style="background:var(--oranje);color:var(--navy);padding:6px 6px 5px">'
             f'<p class="minikop" style="margin:0;font-size:8px">Wie betaalt de preventie?</p></div>'
             f'<div style="flex:1;padding:5px 6px">{_lorem(2)}</div></div></div>',
             "Geen aparte pagina: een aflopende band bovenaan pagina 1, met de inhoud "
             "eronder. Kost een kwart pagina in plaats van een hele.", False),
            ("Gewoon titel",
             f'<div style="height:100%;display:flex;justify-content:center;align-items:center">'
             f'<div style="width:70px;height:94px;box-shadow:inset 0 0 0 1px rgba(32,27,92,.3);'
             f'padding:6px;overflow:hidden">'
             f'<p class="minikop" style="margin:0 0 3px;font-size:8px">Wie betaalt de preventie?</p>'
             f'<hr style="border:0;height:2px;width:22px;background:var(--oranje);margin:0 0 5px">'
             f'{_lorem(3)}</div></div>',
             "De titel staat gewoon in de zetspiegel en de tekst loopt door. Voor "
             "&eacute;&eacute;n blad, of voor een intern stuk dat alleen gelezen wordt.", False),
        ]),
    ]
    return KAART.format(stijl=stijl, blokken="".join(blokken))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--uit", type=Path, default=UIT)
    a = ap.parse_args()
    a.uit.parent.mkdir(parents=True, exist_ok=True)
    tijdelijk = a.uit.with_suffix(".html")
    tijdelijk.write_text(bouw_html(), encoding="utf-8")
    with browser() as b:
        page = b.new_page(viewport={"width": 1240, "height": 600},
                          device_scale_factor=1.6)
        page.goto(tijdelijk.resolve().as_uri())
        wacht_op_letters(page)
        page.screenshot(path=str(a.uit), full_page=True)
    tijdelijk.unlink()
    print(f"{a.uit} ({a.uit.stat().st_size / 1024:.0f} kB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
