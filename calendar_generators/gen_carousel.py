#!/usr/bin/env python3
"""
Generate a LinkedIn carousel for one month of Grenoble meetups.

First-time setup (installs Chromium — once):
    uv run --with playwright python3 -m playwright install chromium

Usage:
    uv run --with playwright --with pyyaml --with img2pdf python3 gen_carousel.py --month 2026-10

Output (next to this script):
    carousel_octobre_2026_01.png  … overview
    carousel_octobre_2026_02.png  … one card per event day
    carousel_octobre_2026.pdf     → upload this to LinkedIn
"""

import base64
import calendar as cal_module
from html import escape
from pathlib import Path

from playwright.sync_api import sync_playwright

from meetup_data import (
    DAYS_LONG, DAYS_SHORT, Event, FR_MONTHS,
    format_time, holidays_in, load_events, month_arg_parser, month_label, parse_month,
)

SLIDE_W, SLIDE_H = 1080, 1080

# Shown on a day card when the event has no venue yet. Safe as a blanket rule:
# the carousel is only ever generated for a month that hasn't happened.
LOCATION_TBA = "Lieu annoncé prochainement"

# ── CSS (plain strings — not f-strings, so { } are literal CSS braces) ────────

OVERVIEW_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { width: 1080px; height: 1080px; overflow: hidden; background: #f8fafc;
       display: flex; flex-direction: column; }
.header { background: #2563eb; min-height: 96px; padding: 14px 24px 10px; display: flex; flex-direction: column;
          align-items: center; justify-content: center; flex-shrink: 0; }
.header h1 { color: #fff; font-size: 32px; font-weight: 800; letter-spacing: -.5px;
             text-align: center; white-space: normal; line-height: 1.2; }
.header .url { color: rgba(255,255,255,.7); font-size: 14px; margin-top: 5px; font-weight: 400; }
.dayrow { display: grid; grid-template-columns: repeat(5, 1fr); background: #1d4ed8;
          flex-shrink: 0; height: 40px; }
.dn { color: rgba(255,255,255,.85); font-size: 13px; font-weight: 700;
      display: flex; align-items: center; justify-content: center;
      letter-spacing: .5px; text-transform: uppercase; }
.grid { display: grid; grid-template-columns: repeat(5, 1fr); flex: 1; align-content: start; overflow: hidden; }
.cell { border: 1px solid #e2e8f0; padding: 8px 8px 6px; overflow: hidden; position: relative; min-height: 56px; }
.cell.out { background: #edf0f4; border-color: #e4e8ed; }
.cell.em { background: #f8fafc; }
.cell.em.hol { background: #fff7ed; }
.cell.ev { background: #fff; }
.dn-ev { font-size: 24px; font-weight: 800; color: #1d4ed8; margin-bottom: 8px; line-height: 1; }
.dn-em { font-size: 18px; font-weight: 500; color: #94a3b8; line-height: 1; }
.pill { background: #2563eb; color: #fff; border-radius: 6px; padding: 6px 10px;
        font-size: 16px; font-weight: 600; margin-bottom: 6px;
        white-space: normal; line-height: 1.4; }
.hname { font-size: 11px; color: #d97706; font-weight: 500; margin-top: 3px; }
.flag { position: absolute; top: 6px; right: 6px; font-size: 14px; }
.footer { height: 52px; background: #fff; border-top: 1px solid #e2e8f0;
          display: flex; align-items: center; justify-content: center;
          color: #64748b; font-size: 14px; font-weight: 500; flex-shrink: 0; }
"""

CARD_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { width: 1080px; height: 1080px; overflow: hidden; background: #fff;
       display: flex; flex-direction: column; }
.top { background: #2563eb; height: 58px; display: flex; align-items: center;
       padding: 0 40px; flex-shrink: 0; }
.brand { color: #fff; font-size: 15px; font-weight: 700; }
.slide-n { color: rgba(255,255,255,.6); font-size: 13px; margin-left: auto; font-weight: 500; }
.body { flex: 1; padding: 40px 64px 32px; display: flex; flex-direction: column; }
.day-header { display: flex; align-items: baseline; gap: 32px; margin-bottom: 8px; }
.big-day { font-size: 160px; font-weight: 900; color: #0f172a; line-height: 1;
           letter-spacing: -6px; white-space: nowrap; }
.day-name { font-size: 160px; font-weight: 900; color: #2563eb; line-height: 1;
            letter-spacing: -5px; white-space: nowrap; }
.month-lbl { font-size: 28px; color: #94a3b8; margin-bottom: 36px; }
hr { border: none; border-top: 2px solid #e2e8f0; margin-bottom: 36px; }
.events { flex: 1; display: flex; flex-direction: column; gap: 36px; overflow: hidden; }
.event-card { border-left: 4px solid #2563eb; padding-left: 32px; }
.evt-title { font-size: 44px; font-weight: 700; color: #0f172a; line-height: 1.2; margin-bottom: 12px; }
.evt-meta { font-size: 28px; font-weight: 600; color: #2563eb; margin-bottom: 12px; }
.evt-desc { font-size: 24px; color: #64748b; line-height: 1.5;
            display: -webkit-box; -webkit-line-clamp: 3;
            -webkit-box-orient: vertical; overflow: hidden; }
.bot { background: #f8fafc; border-top: 1px solid #e2e8f0; height: 56px;
       display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.bot span { color: #94a3b8; font-size: 18px; font-weight: 500; }
"""


# ── Font ──────────────────────────────────────────────────────────────────────

def load_font_css() -> str:
    """Embed Ubuntu Sans as base64 so Chromium renders it without network access."""
    font_path = Path("/usr/share/fonts/truetype/ubuntu/UbuntuSans[wdth,wght].ttf")
    if not font_path.exists():
        return "body { font-family: system-ui, sans-serif; }"
    b64 = base64.b64encode(font_path.read_bytes()).decode()
    return (
        "@font-face {"
        " font-family: 'UbuntuSans';"
        f" src: url('data:font/truetype;base64,{b64}') format('truetype');"
        " font-weight: 100 900; }"
        " body { font-family: 'UbuntuSans', system-ui, sans-serif; }"
    )


# ── HTML builders ─────────────────────────────────────────────────────────────

def overview_html(year: int, month: int, events: list[Event], font_css: str) -> str:
    """Slide 1 — the whole month as a Mon-Fri grid."""
    weeks = cal_module.Calendar(firstweekday=0).monthdayscalendar(year, month)
    holidays = holidays_in(month)

    # A multi-day event shows on every weekday it spans, like the calendar image.
    by_day: dict[int, list[str]] = {}
    for e in events:
        for day in e.days_in_month(year, month):
            by_day.setdefault(day, []).append(escape(e.title + e.span_suffix))

    day_names_html = "".join(f'<div class="dn">{d}</div>' for d in DAYS_SHORT[:5])

    cell_parts = []
    for week in weeks:
        for col in range(5):
            day = week[col]
            holiday = holidays.get(day)

            if day == 0:
                cell_parts.append('<div class="cell out"></div>')
            elif day in by_day:
                pills = "".join(f'<div class="pill">{t}</div>' for t in by_day[day])
                flag = '<div class="flag">🇫🇷</div>' if holiday else ""
                cell_parts.append(
                    f'<div class="cell ev"><div class="dn-ev">{day}</div>{flag}{pills}</div>'
                )
            else:
                hcls = " hol" if holiday else ""
                hname = f'<div class="hname">{escape(holiday)}</div>' if holiday else ""
                cell_parts.append(
                    f'<div class="cell em{hcls}"><div class="dn-em">{day}</div>{hname}</div>'
                )
    cells_html = "".join(cell_parts)

    return (
        f'<!DOCTYPE html><html><head><meta charset="utf-8">'
        f'<style>{font_css}{OVERVIEW_CSS}</style></head><body>'
        f'<div class="header"><h1>Meetups Grenoble · {month_label(year, month)}</h1>'
        f'<div class="url">grenoble-meetups.fr</div></div>'
        f'<div class="dayrow">{day_names_html}</div>'
        f'<div class="grid">{cells_html}</div>'
        f'<div class="footer">{len(events)} meetups · #grenoble_meetups</div>'
        f'</body></html>'
    )


def day_card_html(year: int, month: int, day: int, events: list[Event],
                  slide_num: int, total: int, font_css: str) -> str:
    day_name = DAYS_LONG[cal_module.weekday(year, month, day)]

    event_parts = []
    for e in events:
        bits = []
        if e.is_multi_day:
            bits.append(f"{e.start.day} → {e.end.day} {FR_MONTHS[month - 1].lower()}")
        bits.append(format_time(e.time))
        bits.append(e.location.get("name") or LOCATION_TBA)
        meta = " · ".join(b for b in bits if b)

        meta_html = f'<div class="evt-meta">{escape(meta)}</div>' if meta else ""
        desc_html = f'<div class="evt-desc">{escape(e.description)}</div>' if e.description else ""
        event_parts.append(
            f'<div class="event-card">'
            f'<div class="evt-title">{escape(e.title)}</div>'
            f'{meta_html}{desc_html}'
            f'</div>'
        )
    events_html = "".join(event_parts)

    return (
        f'<!DOCTYPE html><html><head><meta charset="utf-8">'
        f'<style>{font_css}{CARD_CSS}</style></head><body>'
        f'<div class="top">'
        f'<div class="brand">Meetups Grenoble · grenoble-meetups.fr</div>'
        f'<div class="slide-n">{slide_num}/{total}</div>'
        f'</div>'
        f'<div class="body">'
        f'<div class="day-header">'
        f'<span class="big-day">{day:02d}</span>'
        f'<span class="day-name">{day_name}</span>'
        f'</div>'
        f'<div class="month-lbl">{month_label(year, month)}</div>'
        f'<hr>'
        f'<div class="events">{events_html}</div>'
        f'</div>'
        f'<div class="bot"><span>#grenoble_meetups</span></div>'
        f'</body></html>'
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def screenshot(page, html: str, path: Path) -> None:
    page.set_content(html, wait_until="load")
    page.screenshot(path=str(path))


def main() -> None:
    args = month_arg_parser(__doc__ or "").parse_args()
    year, month = parse_month(args.month)

    print("Reading Hugo content…")
    events = load_events(year, month)
    if not events:
        raise SystemExit(f"No events found for {args.month}")

    # One card per day that *starts* an event — a multi-day event gets a single
    # card, with its span in the meta line, rather than N near-identical slides.
    by_start: dict[int, list[Event]] = {}
    for e in events:
        by_start.setdefault(e.start.day, []).append(e)
    event_days = sorted(by_start)
    total = 1 + len(event_days)
    print(f"  → {len(events)} events · {len(event_days)} event days · {total} slides")

    print("Loading font…")
    font_css = load_font_css()

    out = Path(__file__).parent
    prefix = f"carousel_{FR_MONTHS[month - 1].lower()}_{year}"
    png_paths: list[Path] = []

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={"width": SLIDE_W, "height": SLIDE_H})

            p = out / f"{prefix}_01.png"
            screenshot(page, overview_html(year, month, events, font_css), p)
            png_paths.append(p)
            print(f"  ✓ 1/{total}: overview")

            for idx, day in enumerate(event_days, 2):
                p = out / f"{prefix}_{idx:02d}.png"
                screenshot(page, day_card_html(year, month, day, by_start[day], idx, total, font_css), p)
                png_paths.append(p)
                print(f"  ✓ {idx}/{total}: {day} {month_label(year, month)}")

            browser.close()

    except Exception as e:
        if "executable" in str(e).lower() or "chromium" in str(e).lower():
            print("\nChromium not found. Run once:")
            print("  uv run --with playwright python3 -m playwright install chromium")
        raise

    import img2pdf
    pdf_path = out / f"{prefix}.pdf"
    pdf_path.write_bytes(img2pdf.convert([str(p) for p in png_paths]))

    print(f"\n✓ {pdf_path.name}  ({total} pages — upload this to LinkedIn)")
    for p in png_paths:
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
