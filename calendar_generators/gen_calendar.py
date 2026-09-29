#!/usr/bin/env python3
"""
Generate a visual calendar for one month of Grenoble meetups.

    cd calendar_generators
    uv run --with pilmoji --with pyyaml python3 gen_calendar.py --month 2026-10

Events are read from content/meetups/YYYY-MM/, so the image always matches
the site. Titles that are too long for a cell can be overridden in
SHORT_LABELS below, keyed by file name (without .md).
"""

import calendar as cal_module
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji

from meetup_data import (
    FR_MONTHS, holidays_in, load_events, month_arg_parser, month_label, parse_month,
)

# ── Per-event overrides ──────────────────────────────────────────────────────
# Only for titles that don't fit a cell. Everything else comes from the front
# matter as-is. Keep the trailing emoji — it's part of the visual language.
SHORT_LABELS: dict[str, str] = {}

# ── Layout — square canvas (1600×1600 for 5-week months) ─────────────────────
WIDTH = 1600
HEADER_H = 150   # gradient band: title + url + day names
FOOTER_H = 75

# Header gradient: indigo → violet
GRAD_L = (67, 56, 202)    # #4338ca
GRAD_R = (124, 58, 237)   # #7c3aed

# Palette
BG        = "#f8fafc"
C_NORMAL  = "#ffffff"
C_WEEKEND = "#f8fafc"
C_EMPTY   = "#edf0f4"
C_EVENT   = "#eef2ff"
C_HOLIDAY = "#fff7ed"
C_BORDER  = "#e2e8f0"
C_ACCENT  = "#4338ca"   # left-border stripe on event cells
ACCENT_W  = 3

PILL_BG = "#4f46e5"
PILL_FG = "#ffffff"
PILL_PX = 9    # horizontal inner padding
PILL_PY = 5    # vertical inner padding
LINE_H  = 22   # px per event text line

T_NORMAL  = "#0f172a"
T_EVENT   = "#3730a3"
T_WEEKEND = "#64748b"
T_HOLIDAY = "#b45309"
T_HLABEL  = "#d97706"
T_DAYNAME = (210, 205, 255)      # light lavender on gradient
T_WEEKEND_NAME = (255, 200, 200) # slight blush for Sat/Sun names
T_TITLE   = (255, 255, 255)
T_URL     = (200, 195, 240)
T_FOOTER  = "#64748b"

FONT_BOLD = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
FONT_REG  = "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"
FONT_MED  = "/usr/share/fonts/truetype/ubuntu/Ubuntu-M.ttf"


# ── Data ──────────────────────────────────────────────────────────────────────

def day_labels(year: int, month: int) -> dict[int, list[str]]:
    """
    {day: [label, ...]} — multi-day events appear on every day they span,
    each labelled with the span, e.g. "Agile Games Alpes 2026 🎲 (1-3)".
    """
    by_day: dict[int, list[str]] = {}
    for e in load_events(year, month):   # already sorted by day then time
        label = SHORT_LABELS.get(e.slug, e.title) + e.span_suffix
        for day in e.days_in_month(year, month):
            by_day.setdefault(day, []).append(label)
    return by_day


# ── Drawing helpers ───────────────────────────────────────────────────────────

def wrap_label(text: str, font, max_w: int, draw) -> list[str]:
    """
    Wrap to 2 lines. The last word (usually the trailing emoji) is kept on
    whichever line its predecessor is on — never orphaned alone.
    """
    words = text.split()
    lines: list[str] = []
    cur = ""
    for i, w in enumerate(words):
        cand = (cur + " " + w).strip()
        # Only a pure-emoji tail earns the right to overflow; a real word such as
        # the "(1-3)" multi-day span must wrap like any other.
        is_last = i == len(words) - 1 and not any(c.isalnum() for c in w)
        fits = draw.textbbox((0, 0), cand, font=font)[2] <= max_w

        if fits or not cur:
            cur = cand
        elif is_last:
            cur = cand  # keep trailing emoji with previous text, even if slightly wide
        else:
            lines.append(cur)
            if len(lines) == 1:
                # Building line 2 — gather rest, truncate with ellipsis if needed
                rest = " ".join(words[i:])
                while draw.textbbox((0, 0), rest + "…", font=font)[2] > max_w and len(rest) > 1:
                    rest = rest[:-1].rstrip()
                if rest != " ".join(words[i:]):
                    rest += "…"
                lines.append(rest)
                return lines
            cur = w

    if cur:
        lines.append(cur)
    return lines


def render(year: int, month: int, events: dict[int, list[str]], out_file: Path) -> None:
    label = month_label(year, month)
    holidays = {d: f"{name} 🇫🇷" for d, name in holidays_in(month).items()}

    cal_obj = cal_module.Calendar(firstweekday=0)
    weeks = cal_obj.monthdayscalendar(year, month)
    num_weeks = len(weeks)
    cell_h = (WIDTH - HEADER_H - FOOTER_H) // num_weeks
    cell_w = WIDTH // 7
    height = HEADER_H + num_weeks * cell_h + FOOTER_H
    grid_top = HEADER_H

    def cx(col: int) -> int:
        return col * cell_w

    def crx(col: int) -> int:
        """Right edge (inclusive) of column — last column absorbs remainder pixels."""
        return WIDTH - 1 if col == 6 else (col + 1) * cell_w - 1

    def ccw(col: int) -> int:
        return crx(col) - cx(col) + 1

    try:
        f_title   = ImageFont.truetype(FONT_BOLD, 54)
        f_url     = ImageFont.truetype(FONT_REG,  19)
        f_dayname = ImageFont.truetype(FONT_BOLD, 22)
        f_daynum  = ImageFont.truetype(FONT_BOLD, 28)
        f_event   = ImageFont.truetype(FONT_REG,  16)
        f_holiday = ImageFont.truetype(FONT_REG,  13)
        f_footer  = ImageFont.truetype(FONT_MED,  20)
    except Exception:
        f_title = f_url = f_dayname = f_daynum = f_event = f_holiday = f_footer = ImageFont.load_default()

    img  = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(img)

    # Gradient header
    for i in range(WIDTH):
        t = i / (WIDTH - 1)
        r = int(GRAD_L[0] + (GRAD_R[0] - GRAD_L[0]) * t)
        g = int(GRAD_L[1] + (GRAD_R[1] - GRAD_L[1]) * t)
        b = int(GRAD_L[2] + (GRAD_R[2] - GRAD_L[2]) * t)
        draw.line([(i, 0), (i, HEADER_H - 1)], fill=(r, g, b))

    # Dark ridge at header bottom
    draw.rectangle([0, HEADER_H - 4, WIDTH - 1, HEADER_H - 1], fill=(25, 20, 70))

    # Grid cells
    for wk, week in enumerate(weeks):
        for col, day in enumerate(week):
            x0, x1 = cx(col), crx(col)
            y0 = grid_top + wk * cell_h
            y1 = y0 + cell_h - 1

            if day == 0:
                bg = C_EMPTY
            elif day in events:
                bg = C_EVENT
            elif day in holidays:
                bg = C_HOLIDAY
            elif col >= 5:
                bg = C_WEEKEND
            else:
                bg = C_NORMAL

            draw.rectangle([x0, y0, x1, y1], fill=bg, outline=C_BORDER)

            if day > 0 and day in events:
                draw.rectangle([x0, y0, x0 + ACCENT_W - 1, y1], fill=C_ACCENT)

    # Event pill backgrounds (phase 1 — shapes before text layer)
    for wk, week in enumerate(weeks):
        for col, day in enumerate(week):
            if day == 0 or day not in events:
                continue
            x0 = cx(col)
            y0 = grid_top + wk * cell_h
            avail_w = ccw(col) - ACCENT_W - 2 * PILL_PX - 8

            ey = y0 + 42
            for evt in events[day]:
                lns = wrap_label(evt, f_event, avail_w, draw)
                ph = len(lns) * LINE_H + 2 * PILL_PY
                if ey + ph > y0 + cell_h - 8:
                    break
                draw.rounded_rectangle(
                    [x0 + ACCENT_W + 4, ey, crx(col) - 4, ey + ph],
                    radius=7, fill=PILL_BG,
                )
                ey += ph + 6

    # Footer background
    footer_y = grid_top + num_weeks * cell_h
    draw.rectangle([0, footer_y, WIDTH - 1, height - 1], fill="#ffffff")
    draw.line([(0, footer_y), (WIDTH, footer_y)], fill=C_BORDER, width=1)

    # ── Text layer ────────────────────────────────────────────────────────────
    with Pilmoji(img) as p:
        # Title
        title = f"Meetups Grenoble · {label}"
        tbx = draw.textbbox((0, 0), title, font=f_title)
        p.text(((WIDTH - (tbx[2] - tbx[0])) // 2, 14), title, fill=T_TITLE, font=f_title)

        # URL subtitle
        url = "grenoble-meetups.fr"
        ubx = draw.textbbox((0, 0), url, font=f_url)
        p.text(((WIDTH - (ubx[2] - ubx[0])) // 2, 78), url, fill=T_URL, font=f_url)

        # Day names row
        days_fr = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        for col, name in enumerate(days_fr):
            bx = draw.textbbox((0, 0), name, font=f_dayname)
            nx = cx(col) + (ccw(col) - (bx[2] - bx[0])) // 2
            clr = T_WEEKEND_NAME if col >= 5 else T_DAYNAME
            p.text((nx, 110), name, fill=clr, font=f_dayname)

        # Cell content
        for wk, week in enumerate(weeks):
            for col, day in enumerate(week):
                if day == 0:
                    continue
                x0 = cx(col)
                y0 = grid_top + wk * cell_h
                avail_w = ccw(col) - ACCENT_W - 2 * PILL_PX - 8

                # Day number
                if day in events:
                    nc = T_EVENT
                elif day in holidays:
                    nc = T_HOLIDAY
                elif col >= 5:
                    nc = T_WEEKEND
                else:
                    nc = T_NORMAL
                p.text((x0 + ACCENT_W + 10, y0 + 8), str(day), fill=nc, font=f_daynum)

                if day in holidays and day not in events:
                    p.text((x0 + ACCENT_W + 10, y0 + 40), holidays[day], fill=T_HLABEL, font=f_holiday)

                if day in events:
                    ey = y0 + 42
                    for evt in events[day]:
                        lns = wrap_label(evt, f_event, avail_w, draw)
                        ph = len(lns) * LINE_H + 2 * PILL_PY
                        if ey + ph > y0 + cell_h - 8:
                            break
                        ty = ey + PILL_PY
                        for line in lns:
                            p.text((x0 + ACCENT_W + 4 + PILL_PX, ty), line, fill=PILL_FG, font=f_event)
                            ty += LINE_H
                        ey += ph + 6

        # Footer — count events, not day-slots, so a 3-day event counts once
        n = len({lbl for v in events.values() for lbl in v})
        ftxt = f"{n} meetups en {label.lower()}  ·  #grenoble_meetups"
        fbx = draw.textbbox((0, 0), ftxt, font=f_footer)
        fx = (WIDTH - (fbx[2] - fbx[0])) // 2
        fy = footer_y + (FOOTER_H - (fbx[3] - fbx[1])) // 2
        p.text((fx, fy), ftxt, fill=T_FOOTER, font=f_footer)

    img.save(out_file, "PNG")
    print(f"Saved: {out_file} ({WIDTH}×{height}px)")


def main() -> None:
    ap = month_arg_parser(__doc__ or "")
    ap.add_argument("--out", type=Path, default=None,
                    help="output PNG (default: calendrier_<mois>_<année>.png next to this script)")
    args = ap.parse_args()
    year, month = parse_month(args.month)

    events = day_labels(year, month)
    if not events:
        raise SystemExit(f"No events found for {args.month}")

    out = args.out or Path(__file__).parent / f"calendrier_{FR_MONTHS[month - 1].lower()}_{year}.png"
    render(year, month, events, out)


if __name__ == "__main__":
    main()
