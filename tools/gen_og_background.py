#!/usr/bin/env python3
"""Génère assets/og/card-bg.png, le fond commun à toutes les cards sociales.

Seuls les éléments identiques sur toutes les cards sont dessinés ici (dégradé,
barre d'accent, domaine) ; le texte variable est ajouté au build par Hugo via
`images.Text` dans layouts/partials/og-image.html.

    uv run --with pillow tools/gen_og_background.py

À relancer uniquement si le visuel du fond change. Le PNG produit est commité.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "og" / "card-bg.png"
FONT_BOLD = ROOT / "assets" / "fonts" / "Inter-Bold.ttf"

WIDTH, HEIGHT = 1200, 630
MARGIN = 80

# Palette du site (voir CLAUDE.md) — bleu ciel → bleu roi, accent ambre.
GRAD_FROM = (147, 197, 253)  # #93c5fd
GRAD_TO = (29, 78, 216)      # #1d4ed8
AMBER = "#f59e0b"

# Barre d'accent, en haut à gauche.
BAR = (MARGIN, 84, MARGIN + 88, 92)

DOMAIN = "grenoble-meetups.fr"
DOMAIN_Y = 552


def diagonal_gradient(size, start, end):
    """Dégradé diagonal ↘, calculé en petit puis agrandi (lisse et rapide)."""
    w, h = 80, 42
    pixels = []
    for y in range(h):
        for x in range(w):
            t = (x / (w - 1) + y / (h - 1)) / 2
            pixels.append(tuple(round(a + (b - a) * t) for a, b in zip(start, end)))
    small = Image.new("RGB", (w, h))
    small.putdata(pixels)
    return small.resize(size, Image.Resampling.LANCZOS)


img = diagonal_gradient((WIDTH, HEIGHT), GRAD_FROM, GRAD_TO)
draw = ImageDraw.Draw(img)

draw.rounded_rectangle(BAR, radius=4, fill=AMBER)

# Pied de card : « </> » en ambre puis le domaine en blanc.
f_domain = ImageFont.truetype(str(FONT_BOLD), 28)
tag = "</> "
draw.text((MARGIN, DOMAIN_Y), tag, font=f_domain, fill=AMBER)
tag_w = draw.textlength(tag, font=f_domain)
draw.text((MARGIN + tag_w, DOMAIN_Y), DOMAIN, font=f_domain, fill="#ffffff")

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, "PNG", optimize=True)
print(f"{OUT.relative_to(ROOT)} — {img.size[0]}×{img.size[1]}")
