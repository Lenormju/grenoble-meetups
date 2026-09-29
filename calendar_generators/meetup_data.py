"""
Shared data layer for the calendar and carousel generators.

Both read the same Hugo content, so the month parsing, the event loading and
the French labels live here rather than being duplicated (and drifting).
"""

import argparse
import calendar as cal_module
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

CONTENT_DIR = Path(__file__).parent.parent / "content" / "meetups"

FR_MONTHS = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]

DAYS_LONG  = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
DAYS_SHORT = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

# Fixed-date French public holidays. The movable ones (Pâques, Ascension,
# Pentecôte) are deliberately absent — no meetup month has needed them yet.
HOLIDAYS = {
    (1, 1):   "Jour de l'An",
    (5, 1):   "Fête du Travail",
    (5, 8):   "Victoire 1945",
    (7, 14):  "Fête Nationale",
    (8, 15):  "Assomption",
    (11, 1):  "Toussaint",
    (11, 11): "Armistice",
    (12, 25): "Noël",
}


@dataclass
class Event:
    slug: str
    title: str
    start: date
    end: date
    time: str | None = None
    location: dict = field(default_factory=dict)
    description: str = ""

    @property
    def is_multi_day(self) -> bool:
        return self.end > self.start

    @property
    def span_suffix(self) -> str:
        """" (1-3)" for a multi-day event, empty otherwise."""
        return f" ({self.start.day}-{self.end.day})" if self.is_multi_day else ""

    @property
    def sort_key(self) -> tuple[int, int]:
        """Start day, then time of day — for ordering within a month and a day."""
        return (self.start.day, minutes_of_day(self.time))

    def days_in_month(self, year: int, month: int) -> list[int]:
        """Every day number this event occupies within the given month."""
        last = cal_module.monthrange(year, month)[1]
        return list(range(self.start.day, min(self.end.day, last) + 1))


def minutes_of_day(time_val) -> int:
    """Minutes since midnight; unknown times sort last."""
    if not time_val:
        return 24 * 60
    s = str(time_val).strip()
    named = {"midi": 12 * 60, "après-midi": 14 * 60, "soir": 19 * 60}
    if s in named:
        return named[s]
    if ":" in s:
        h, m = s.split(":", 1)
        try:
            return int(h) * 60 + int(m)
        except ValueError:
            pass
    return 24 * 60


def format_time(val) -> str | None:
    """"19:00" → "19h", "18:30" → "18h30", "soir" → "En soirée"."""
    if not val:
        return None
    s = str(val).strip()
    labels = {"soir": "En soirée", "midi": "À midi", "après-midi": "L'après-midi"}
    if s in labels:
        return labels[s]
    if ":" in s:
        h, m = s.split(":", 1)
        return f"{int(h)}h{m}" if m != "00" else f"{int(h)}h"
    return s


def month_label(year: int, month: int) -> str:
    return f"{FR_MONTHS[month - 1]} {year}"


def holidays_in(month: int) -> dict[int, str]:
    return {d: label for (m, d), label in HOLIDAYS.items() if m == month}


def load_events(year: int, month: int) -> list[Event]:
    """
    Read content/meetups/YYYY-MM/ into Event objects, sorted chronologically.

    Cancelled events are skipped, as are files whose date falls outside the
    month (which shouldn't happen, but the site is the source of truth).
    """
    month_dir = CONTENT_DIR / f"{year:04d}-{month:02d}"
    if not month_dir.is_dir():
        raise SystemExit(f"No content directory: {month_dir}")

    events: list[Event] = []
    for f in sorted(month_dir.glob("*.md")):
        if f.name == "_index.md":
            continue
        parts = f.read_text(encoding="utf-8").split("---", 2)
        if len(parts) < 3:
            continue
        fm = yaml.safe_load(parts[1])
        if not fm or fm.get("cancelled"):
            continue

        start = _as_date(fm.get("date"))
        if not start or start.month != month or start.year != year:
            continue
        end = _as_date(fm.get("endDate")) or start

        loc = fm.get("location") or {}
        events.append(Event(
            slug=f.stem,
            title=fm.get("title") or f.stem,
            start=start,
            end=end,
            time=fm.get("time"),
            location=loc if isinstance(loc, dict) else {},
            description=fm.get("description") or "",
        ))

    return sorted(events, key=lambda e: e.sort_key)


def _as_date(val) -> date | None:
    if isinstance(val, str):
        return date.fromisoformat(val)
    if isinstance(val, date):
        return val
    return None


def month_arg_parser(description: str) -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("--month", required=True, metavar="YYYY-MM",
                    help="month to render, e.g. 2026-10")
    return ap


def parse_month(value: str) -> tuple[int, int]:
    try:
        year, month = (int(x) for x in value.split("-", 1))
        if not 1 <= month <= 12:
            raise ValueError
    except ValueError:
        raise SystemExit(f"Invalid --month {value!r}, expected YYYY-MM")
    return year, month
