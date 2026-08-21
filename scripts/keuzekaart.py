"""Bouwt de keuzekaart voor het vragenvuur: per besluit de opties als detailuitsnede.

ONDERHOUDSGEREEDSCHAP, geen bouwstap. De skill roept dit nooit aan tijdens een deck: de kaart
staat als PNG in `assets/keuzekaarten/` en gaat daar ongelezen naar de gebruiker, dus hij kost
geen tokens en geen render. Draai dit script alleen wanneer een optie verandert of er een
referentie bijkomt:

    python scripts/keuzekaart.py

Alle uitsnedes komen uit renders die al in de repo staan (`assets/maatstaf/`,
`assets/proeven/`), dus er wordt hier niets gerenderd.

Maten in fracties van de slide, zodat het onafhankelijk is van de renderbreedte.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent      # de plugin-map, niet dit script
UIT = REPO / "assets/keuzekaarten/vragenvuur.png"
LATO = "/usr/share/fonts/truetype/lato/Lato-Regular.ttf"
LATO_B = "/usr/share/fonts/truetype/lato/Lato-Semibold.ttf"
NAVY, GRIJS, WIT = (32, 27, 92), (98, 94, 140), (255, 255, 255)

f_rij = ImageFont.truetype(LATO_B, 30)
f_opt = ImageFont.truetype(LATO_B, 25)
f_txt = ImageFont.truetype(LATO, 22)

CEL_W, CEL_H = 430, 250        # de uitsnede na schalen
MARGE, GOOT = 40, 26
LABEL_H, RIJKOP_H = 62, 46

RIJEN = [
    ("1  DICHTHEID", [
        ("spreekdeck", "50-60 woorden per slide", "assets/maatstaf/13-dumbbell-plot-op-schaal.png", (0.0, 0.04, 1.0, 0.94)),
        ("licht leave-behind  ·  default", "90-110", "assets/maatstaf/12-tabel-verzadigde-rijlabels-puntenmeter.png", (0.0, 0.04, 1.0, 0.94)),
        ("leave-behind", "120-145", "assets/maatstaf/11-vier-fasekaarten-tweede-uitgelicht.png", (0.0, 0.04, 1.0, 0.94)),
    ]),
    ("2  KLEURREGISTER", [
        ("poppend  ·  default", "vol label, wit paneel: 76% wit, 9% tint",
         "assets/proeven/11-poppend-vol-label-wit-paneel.png", (0.02, 0.24, 0.58, 0.54)),
        ("ingetogen  ·  vraag ernaar", "de hue verdund als paneel: 80% wit, 6% tint",
         "assets/proeven/02-vier-hues-volle-rijlabels-14procent.png", (0.02, 0.24, 0.58, 0.54)),
    ]),
    ("3  GEVULDHEID", [
        ("met kleur  ·  default", "76% wit, 15% vol", "assets/proeven/11-poppend-vol-label-wit-paneel.png", (0.02, 0.24, 0.58, 0.54)),
        ("weinig accent", "92% wit, 3% vol", "assets/proeven/03-nadruk-in-een-chip.png", (0.02, 0.26, 0.58, 0.56)),
        ("kaal", "94% wit, 1% vol", "assets/proeven/01-wit-oranje-koppen-inversie.png", (0.02, 0.24, 0.58, 0.54)),
    ]),
    ("4  WAT KLEUR CODEERT", [
        ("alleen oranje  ·  default", "nadruk in een vlak", "assets/proeven/03-nadruk-in-een-chip.png", (0.24, 0.28, 0.76, 0.58)),
        ("een tweede hue", "twee kanten van een afweging", "assets/maatstaf/04-twee-kolommen-teal-tegen-koraal.png", (0.02, 0.24, 0.62, 0.52)),
        ("een set van vier", "vier categorieen deckbreed", "assets/proeven/02-vier-hues-volle-rijlabels-14procent.png", (0.02, 0.24, 0.42, 0.80)),
    ]),
    ("5  TITELMODUS", [
        ("A  de titel is de bewering  ·  default", "geen subtitel", "assets/proeven/03-nadruk-in-een-chip.png", (0.02, 0.05, 0.98, 0.26)),
        ("B  de titel is het hoofdstuk", "subtitel draagt de bewering", "assets/proeven/08-modus-b-hoofdstuktitel.png", (0.02, 0.05, 0.98, 0.26)),
        ("B vraagt een divider per hoofdstuk", "uit de fotolayouts 6 t/m 16", "assets/proeven/07-modus-b-divider.png", (0.0, 0.04, 1.0, 0.94)),
    ]),
]

kol = len(RIJEN[0][1])
breedte = MARGE * 2 + kol * CEL_W + (kol - 1) * GOOT
hoogte = MARGE * 2 + len(RIJEN) * (RIJKOP_H + LABEL_H + CEL_H + 34)
kaart = Image.new("RGB", (breedte, hoogte), WIT)
d = ImageDraw.Draw(kaart)

y = MARGE
for rijkop, cellen in RIJEN:
    d.text((MARGE, y), rijkop, font=f_rij, fill=NAVY)
    d.line([(MARGE, y + 40), (breedte - MARGE, y + 40)], fill=(220, 220, 230), width=2)
    y += RIJKOP_H
    for i, (naam, onder, pad, box) in enumerate(cellen):
        x = MARGE + i * (CEL_W + GOOT)
        d.text((x, y), naam, font=f_opt, fill=NAVY)
        d.text((x, y + 30), onder, font=f_txt, fill=GRIJS)
        im = Image.open(REPO / pad).convert("RGB")
        W, H = im.size
        uit = im.crop((int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H)))
        uit.thumbnail((CEL_W, CEL_H), Image.LANCZOS)
        top = y + LABEL_H + (CEL_H - uit.size[1]) // 2
        kaart.paste(uit, (x, top))
        d.rectangle([x, y + LABEL_H, x + CEL_W - 1, y + LABEL_H + CEL_H - 1],
                    outline=(225, 225, 235), width=1)
    y += LABEL_H + CEL_H + 34

UIT.parent.mkdir(parents=True, exist_ok=True)
kaart.save(UIT, optimize=True)
print(f"{UIT} — {kaart.size[0]} bij {kaart.size[1]} px, {UIT.stat().st_size // 1024} kB")
