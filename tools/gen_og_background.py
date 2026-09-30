#!/usr/bin/env python3
"""Génère assets/og/card-bg.png, le fond commun à toutes les cards sociales.

Seuls les éléments identiques sur toutes les cards sont dessinés ici (dégradé,
liseré ambre, cadre de la pastille date, domaine) ; le texte variable est
ajouté au build par Hugo via `images.Text` dans layouts/partials/og-image.html.

    uv run --with pillow tools/gen_og_background.py

À relancer uniquement si le visuel du fond change. Le PNG produit est commité.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "og" / "card-bg.png"
FONT_BOLD = ROOT / "assets" / "fonts" / "Inter-Bold.ttf"

WIDTH, HEIGHT = 1200, 630
MARGIN = 64

# Bleu profond plutôt que le bleu ciel du favicon : la card est vue sur le fil
# blanc de LinkedIn, où un fond sombre ressort, et le texte blanc y gagne le
# contraste qui manquait en haut à gauche de l'ancien dégradé.
GRAD_FROM = (37, 99, 235)   # #2563eb
GRAD_TO = (12, 30, 74)      # #0c1e4a
AMBER = "#f59e0b"

# Liseré vertical, bord gauche : repère de marque qui survit à la vignette.
RULE_W = 12

# Cadre de la pastille date. Les textes (jour, mois, nombre) sont posés par
# Hugo ; seul le cadre est ici. Voir les repères dans og-image.html.
BADGE_X, BADGE_Y, BADGE_W, BADGE_H = MARGIN, 78, 272, 372
BADGE_HEAD_H = 82
BADGE_RADIUS = 22

DOMAIN = "grenoble-meetups.fr"
DOMAIN_Y = 556
DOMAIN_SIZE = 26


def diagonal_gradient(size, start, end):
    """Dégradé diagonal ↘, calculé en petit puis agrandi (lisse et rapide)."""
    w, h = 96, 50
    pixels = []
    for y in range(h):
        for x in range(w):
            t = (x / (w - 1) + y / (h - 1)) / 2
            pixels.append(tuple(round(a + (b - a) * t) for a, b in zip(start, end)))
    small = Image.new("RGB", (w, h))
    small.putdata(pixels)
    return small.resize(size, Image.Resampling.LANCZOS)


# L'image reste en RGB : c'est ce qui fait que le mode « RGBA » du Draw
# compose les fills semi-transparents au lieu d'écraser le canal alpha.
img = diagonal_gradient((WIDTH, HEIGHT), GRAD_FROM, GRAD_TO)
draw = ImageDraw.Draw(img, "RGBA")

draw.rectangle((0, 0, RULE_W, HEIGHT), fill=AMBER)

# Corps de la pastille : blanc très transparent, pour rester lisible quel que
# soit l'endroit du dégradé sur lequel il tombe.
draw.rounded_rectangle(
    (BADGE_X, BADGE_Y, BADGE_X + BADGE_W, BADGE_Y + BADGE_H),
    radius=BADGE_RADIUS, fill=(255, 255, 255, 30),
)
# Bandeau ambre : arrondi en haut, carré en bas pour se raccorder au corps.
draw.rounded_rectangle(
    (BADGE_X, BADGE_Y, BADGE_X + BADGE_W, BADGE_Y + BADGE_HEAD_H),
    radius=BADGE_RADIUS, fill=AMBER,
)
draw.rectangle(
    (BADGE_X, BADGE_Y + BADGE_RADIUS, BADGE_X + BADGE_W, BADGE_Y + BADGE_HEAD_H),
    fill=AMBER,
)

# Pied de card : « </> » en ambre puis le domaine en blanc. Volontairement le
# seul texte sous 38 px — c'est la mention de marque, pas l'information.
f_domain = ImageFont.truetype(str(FONT_BOLD), DOMAIN_SIZE)
tag = "</> "
draw.text((MARGIN, DOMAIN_Y), tag, font=f_domain, fill=AMBER)
tag_w = draw.textlength(tag, font=f_domain)
draw.text((MARGIN + tag_w, DOMAIN_Y), DOMAIN, font=f_domain, fill="#ffffff")

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, "PNG", optimize=True)
print(f"{OUT.relative_to(ROOT)} — {img.size[0]}×{img.size[1]}")
