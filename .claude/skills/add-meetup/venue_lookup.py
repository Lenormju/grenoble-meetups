"""Look up a venue (by name or by address) in venues.yaml.

    uv run --with pyyaml .claude/skills/add-meetup/venue_lookup.py "5 esplanade Andry Farcy 38000 Grenoble"

Prints every plausible venue, best first, tagged with why it matched:
  exact-name    normalised query == normalised name/alias
  name          query is contained in a name/alias, or the reverse (e.g. "Casemate")
  address       query contains the venue's street (number and street words)
Exit status 0 if there is at least one candidate, 1 if none (a new venue).
Zero candidates -> new venue. One -> use it. Several -> let the user choose.
"""
import re
import sys
import unicodedata
from pathlib import Path

import yaml

VENUES = Path(__file__).with_name("venues.yaml")
# Words that carry no identity: articles, street types, the town, postcodes.
NOISE = {
    "le", "la", "les", "l", "de", "du", "des", "d", "a", "au", "aux", "et",
    "rue", "avenue", "av", "bd", "boulevard", "place", "cour", "quai", "esplanade",
    "chemin", "impasse", "allee", "cours", "route", "grenoble", "france",
}


def tokens(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    words = re.findall(r"[a-z0-9]+", text)
    return [w for w in words if w not in NOISE and not re.fullmatch(r"38\d{3}", w)]


def street(address):
    """The street part of a canonical address: before the trailing ', City'."""
    return address.rsplit(",", 1)[0] if "," in address else address


def classify(query, venue):
    q = tokens(query)
    if not q:
        return None
    qs = set(q)
    for label in [venue["name"], *venue.get("aliases", [])]:
        t = tokens(label)
        if t and set(t) == qs:
            return "exact-name"
    for label in [venue["name"], *venue.get("aliases", [])]:
        t = set(tokens(label))
        if t and (qs <= t or t <= qs) and not _is_street_only(qs, venue):
            return "name"
    addr = venue.get("address")
    if addr:
        a = set(tokens(street(addr)))
        # the query covers the whole street, or is a >=2-word part of it
        # ("Cour Marcel Reymond" for "Cour Marcel Reymond, Rue des Minimes")
        if a and (a <= qs or (qs <= a and len(qs) >= 2)):
            return "address"
    return None


def _is_street_only(qs, venue):
    # a query made only of street words must not be taken as a venue name
    addr = venue.get("address")
    return bool(addr) and qs <= set(tokens(street(addr))) and bool(qs & set(tokens(street(addr))))


def main(query):
    data = yaml.safe_load(VENUES.read_text(encoding="utf-8"))
    order = {"exact-name": 0, "name": 1, "address": 2}
    hits = []
    for v in data["venues"]:
        why = classify(query, v)
        if why:
            hits.append((order[why], why, v))
    hits.sort(key=lambda h: h[0])
    if not hits:
        print(f"NO MATCH for {query!r}: new venue, add it to venues.yaml")
        return 1
    for _, why, v in hits:
        print(f"[{why}]")
        print(f'  name: "{v["name"]}"')
        if v.get("address"):
            print(f'  address: "{v["address"]}"')
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
