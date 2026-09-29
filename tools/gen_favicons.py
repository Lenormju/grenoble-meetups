"""Regenerate static/favicon.ico and static/apple-touch-icon.png from static/favicon.svg.

Run with:  uv run --with pillow --with cairosvg tools/gen_favicons.py

Only needed when static/favicon.svg is redesigned; both outputs are committed.
"""

import io
from pathlib import Path

import cairosvg
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SVG = ROOT / "static" / "favicon.svg"
ICO = ROOT / "static" / "favicon.ico"
APPLE = ROOT / "static" / "apple-touch-icon.png"

# Sizes embedded in the .ico: 16 and 32 for browser tabs, 48 for the Windows
# taskbar and older shell surfaces.
ICO_SIZES = (16, 32, 48)

# Apple recommends 180x180 for recent iPhones; iOS downscales it for every
# other slot it needs.
APPLE_SIZE = 180


def render(svg: str, size: int) -> Image.Image:
    png = cairosvg.svg2png(
        bytestring=svg.encode(), output_width=size, output_height=size
    )
    return Image.open(io.BytesIO(png)).convert("RGBA")


def main() -> None:
    svg = SVG.read_text()

    # The .ico keeps the SVG's rounded corners and its transparency, which is
    # what browsers expect in a tab.
    frames = [render(svg, size) for size in ICO_SIZES]
    frames[-1].save(ICO, format="ICO", sizes=[(s, s) for s in ICO_SIZES])

    # iOS applies its own rounded mask to the touch icon, so the source must be
    # a full square: squaring the background rect avoids doubly-rounded corners
    # with transparent notches. Flattening onto the gradient's own start colour
    # also removes the alpha channel, which older iOS versions render as black.
    squared = svg.replace(
        '<rect width="100" height="100" rx="18" fill="url(#bg)"/>',
        '<rect width="100" height="100" fill="url(#bg)"/>',
    )
    if squared == svg:
        raise SystemExit(
            "favicon.svg no longer contains the expected background rect — "
            "update the replacement in tools/gen_favicons.py"
        )

    icon = render(squared, APPLE_SIZE)
    flattened = Image.new("RGB", icon.size, "#93c5fd")
    flattened.paste(icon, mask=icon.split()[3])
    flattened.save(APPLE, format="PNG")

    print(f"wrote {ICO.relative_to(ROOT)} ({', '.join(str(s) for s in ICO_SIZES)})")
    print(f"wrote {APPLE.relative_to(ROOT)} ({APPLE_SIZE}x{APPLE_SIZE})")


if __name__ == "__main__":
    main()
