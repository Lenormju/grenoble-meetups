# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A Hugo static site listing Grenoble tech meetups, deployed to GitHub Pages at https://grenoble-meetups.fr. The homepage at `/` is a real page showing the current month's meetups. Each month is a Hugo section (`content/meetups/YYYY-MM/`), and each event is a Markdown file within it.

## Commands

```bash
hugo server          # local dev server with hot-reload
hugo server --buildFuture   # include future-dated events (needed for upcoming meetups)
hugo --gc --minify   # production build (output to ./public)
```

Hugo version: **0.162.0** (see `.github/workflows/hugo.yml`). `buildFuture = true` is already set in `hugo.toml`, so `hugo server` shows upcoming events locally.

## Content structure

```
content/meetups/
  YYYY-MM/
    _index.md          # month section (title, date, optional linkedinPost)
    YYYY-MM-DD-slug.md # one file per event
```

### Event front matter

```yaml
---
cancelled: true      # optional — goes *above* title; see "Cancelled events" below
title: "Event name with emoji at end 🎤"
description: "One-sentence summary for SEO"  # required — see the add-meetup skill for how to obtain one
startDate: "YYYY-MM-DD"
startTime: "soir"      # midi | après-midi | soir | HH:MM (e.g. "19:00") — omit only if even the part of day is unknown
endDate: "YYYY-MM-DD"  # optional, for multi-day events
endTime: "20:00"       # optional — time on endDate if set, else on startDate; same grammar as startTime
location:            # optional
  name: "La Casemate"
  address: "1 Place Saint-Laurent, Grenoble"  # optional
  city: "Échirolles"   # optional — omit for Grenoble (the default); drives addressLocality in the JSON-LD
links:
  - url: "https://..."
    label: "Custom label"  # optional, defaults to "S'inscrire"
price: "payant"      # optional — omit if free (the default), a number for a known price in EUR
---
Optional longer description in Markdown.
```

`price` only feeds the `Event` JSON-LD `offers` (it is not displayed on the page). Omitted means free (`price: 0`, EUR), which is right for nearly every meetup; use `"payant"` for ticketed conferences whose price we don't track, or a number for a known price.

The offer's `url` is the first entry of `links`, falling back to the event's own page when the event has no link (Google requires the field).

The offer's `validFrom` needs no front matter: it comes from the **first** commit touching the file (`enableGitInfo`, via `.GitInfo.Ancestors.Reverse`), clamped so it is never later than the event date. Files not yet committed fall back to the event date.

It must be the *first* commit, not `.GitInfo`'s own (which is the **latest**). The first commit is the real publication date and it is immutable — no later edit can rewrite it. Using the latest meant the value drifted on every subsequent edit: 32 of 114 pages had already silently moved off their publication date that way, and a single repo-wide reformat reset 36 more at once. Deriving published data from git history is only safe if you reach for the end of it that doesn't move.

### Field naming and ordering

Event files use `startDate` / `startTime` / `endDate` / `endTime` — two symmetric pairs, in that order, which reads as the interval (`startDate` at `startTime` → `endDate` at `endTime`). The names deliberately match schema.org's `Event.startDate` / `endDate`, which is what these fields feed.

Both time fields share one grammar: `midi` | `après-midi` | `soir` | `H?H:MM` (`HH` 00–23, `MM` 00–59; a single-digit hour like `9:00` is normalised to `09:00`). The fuzzy words are a permanent, deliberate state — not a legacy shorthand waiting to be replaced once a real hour is known — for events announced before they're scheduled: `midi` → 12:00, `après-midi` → 14:00, `soir` → 19:00. When the exact hour is unknown, prefer a fuzzy value over omitting the field: an omitted `startTime` makes the event all-day, which reads as starting at midnight — worse than an approximate evening. `19h` / `19h30` is not supported; it was never documented and no file uses it. A malformed value fails the build via `errorf`, naming the file and the value — there is no silent fallback to all-day.

One rule computes the end, with no day arithmetic anywhere: end = (`endDate` if set, else `startDate`) at `endTime`. If the computed end is not after the computed start, the build fails — nothing is ever inferred about which day an event ends, so an event running past midnight must say so with an explicit `endDate`. `startTime: "soir"` + `endTime: "soir"` with no `endDate` fails for the same reason (end == start) rather than silently becoming a 24-hour event. On the all-day path the predicate is deliberately looser — both bounds are whole days, so `endDate` equal to `startDate` only restates a one-day event and is accepted — but an `endDate` *strictly before* its `startDate` fails the build, since it would emit a `DTEND` preceding its `DTSTART` and make `month-calendar.html`'s `seq` day-expansion count downward. `startDate` is itself required: a file without it, and without any of the `hugo.toml` fallback keys, fails the build rather than inheriting the zero date and publishing an event in year 0001.

| `startTime` | `endTime` | `endDate` | Result |
|---|---|---|---|
| yes | no | no | start + 2h default |
| yes | yes | no | timed, same day; end <= start fails the build |
| yes | yes | yes | timed start on `startDate`, timed end on `endDate` |
| no | no | yes | all-day span (GreHack, DrupalCamp) |
| no | yes | any | build error — an end with no start is meaningless |
| yes | no | yes | all-day span; `startTime` is not used in the feed |

That last row is deliberate, not an oversight: `startTime` with `endDate` but no `endTime` is a legitimately partial record — "starts 19:00 the first evening, runs through the 3rd, final hour unknown" — so it's accepted rather than rejected, every field staying independently optional. The cost is real and worth knowing: the event page shows the start time while the iCal feed shows an all-day span.

`startDate` is not Hugo's own key, so `hugo.toml` points Hugo at it:

```toml
[frontmatter]
  date = ["startDate", "date", "publishDate", "lastmod"]
```

`.Date` is populated from the first key found, so **every template keeps using `.Date`** — the rename touched no date-reading template. `date` stays in the list because the month `_index.md` files still use it: there, the date is a marker identifying the month, not the start of an interval, so `startDate` would imply a missing `endDate`.

**Quote every value except booleans and numbers**, dates included. This is defensive, not load-bearing — Hugo 0.162 coerces none of it, and a quoted `date` still parses into a real `time.Time` — but it costs nothing and removes a thing to reason about. `cancelled` is the exception that matters: quoting it breaks the site asymmetrically, since `{{ if .Params.cancelled }}` treats any non-empty string as true while `where … "ne" true` does not match the string `"true"`, so `cancelled: "true"` yields an event that says *annulé* on its page while the calendar and RSS keep advertising it.

### Cancelled events

`cancelled: true` marks an event as called off rather than deleting its file, so the page keeps working for anyone holding the link. Three things follow from it:

- `month-calendar.html` drops the event from the calendar grid (`where .events "Params.cancelled" "ne" true`), so it disappears from the homepage and month views.
- `meetups/single.html` renders `Cet événement a été annulé.` on the detail page and sets the `Event` JSON-LD `eventStatus` to `EventCancelled`.
- `_default/rss.xml` filters it out of `/index.xml`, using the same `"ne" true` idiom as the calendar. A cancelled event is not news, and the feed is capped at 50 items, so dropping it lets a real event take the slot.
- `_default/calendar.ics` **keeps** the `VEVENT` and marks it `STATUS:CANCELLED` (plus `SEQUENCE:1`). This is deliberately the opposite of the RSS treatment: subscribers already hold the event, and a `VEVENT` that simply vanishes from a published feed is not a cancellation signal — most clients keep showing the stale entry. `STATUS:CANCELLED` tells them to strike it, and the bumped `SEQUENCE` (everything else is implicitly 0) marks it as a revision so clients accept it over the copy they cached.

Convention: the three existing files all put `cancelled: true` on the line *above* `title:`. `description` stays directly after `title:` regardless, so it lands on line 4 in those files rather than line 3.

### Deadlines (CFP, inscriptions)

A submission deadline is not a meetup, but it is published as one: an event file in the month the deadline falls in. Three files do this — `2026-05-31-tremplin-snowcamp.md`, `2026-06-15-cfp-campus-agile.md`, `2026-10-18-cfp-snowcamp.md`.

The alternative is a link on the conference's own event, which is what GreHack and AlpOSS carry (`label: "Call for papers (avant le 2 novembre)"`). That only works when the conference itself is within the browsing horizon. Snowcamp's CFP closes in October for a conference in January, so a link there would sit in a month nobody is looking at yet — hence the standalone entry. Both forms can coexist for the same event, and do.

Three conventions follow:

- **The title starts lowercase** and reads as a phrase, because the calendar grid prints it right after the day number: `18 — limite pour soumettre au CFP de Snowcamp`. The forms in use are `limite pour soumettre au CFP de …` and `clôture des inscriptions au …`.
- **No `startTime` or `endTime` — the entry is all-day.** A deadline is an instant, not an interval, so any start time would be fabricated. `endTime` alone fails the build by design (`event-times.html`), and `startTime: "00:00"` + `endTime: "23:59"` is worse than it looks: it publishes a midnight start on the page and in the grid, and turns the `VEVENT` into a 24-hour *timed* block rather than an all-day banner, which most clients render as a solid column over the whole day.
- **The exact hour goes in the link label**, where it is actionable and costs the time model nothing: `label: "Proposer un talk (jusqu'à 23h59)"`. Don't repeat the day in it — the grid already files the entry under that day, and the detail page already shows the date.

Two things a deadline still needs: the organiser's `groups`, so the JSON-LD gets an `organizer`; and an explicit `label` on every link, since the `S'inscrire` default is wrong for a call for papers.

### Month `_index.md` front matter

```yaml
---
title: "Mois YYYY"
date: "YYYY-MM-01"
linkedinPost: "https://..."   # optional
---
```

### Naming conventions

- Directory: `YYYY-MM`
- File: `YYYY-MM-DD-kebab-case-slug.md` — slug is 1–4 words, no accents, lowercase, hyphens

## Layouts

- `layouts/index.html` — real homepage at `/`, shows the current month's meetups
- `layouts/meetups/list.html` — renders `/meetups/` (current month calendar + past months list) and `/meetups/YYYY-MM/` (single month calendar)
- `layouts/meetups/single.html` — event detail page
- `layouts/partials/month-calendar.html` — calendar grid partial; supports `endDate` for multi-day event spans. The one place that still reads `startTime` directly and prints it raw, rather than going through `event-times.html`
- `layouts/partials/fr-month-name.html` — French month name helper
- `layouts/partials/seo.html` — meta description, canonical, Open Graph and Twitter tags; called from `baseof.html` for every page
- `layouts/partials/og-image.html` — builds the social card, returns its absolute URL
- `layouts/partials/text-wrap.html` — line-breaking helper for `images.Text`
- `layouts/partials/event-times.html` — single owner of event timing. Parses `startTime`/`endTime` (including the fuzzy vocabulary), applies the 2-hour default and the end-computation rule, and returns `{ start, end, allDay, endIsDefault }` zoned to `Europe/Paris`. Consumed by `calendar.ics` and `meetups/single.html`
- `layouts/partials/banner-afup.html` — site-wide banner for the AFUP open letter (temporary campaign; remove the partial, its call in `baseof.html` and the `.support-banner` CSS when it ends)
- `layouts/_default/rss.xml` — RSS feed at `/index.xml`, lists individual meetup events sorted by date (newest first, max 50), excluding cancelled ones
- `layouts/_default/calendar.ics` — iCal feed at `/meetups.ics`; every event including cancelled ones, which carry `STATUS:CANCELLED` (see "Cancelled events"). Defines an `ics-escape` template for RFC 5545 escaping and emits an explicit `DTEND` in every timed case, computed by `event-times.html`

## Social cards (`og:image`)

Every page gets a 1200×630 card, generated by Hugo at build time and used for both `og:image`/`twitter:image` (`seo.html`) and the `Event` JSON-LD `image` (`meetups/single.html`). No image is committed and no CI step is involved — a full build produces ~126 cards in under 3 s.

`og-image.html` composes `assets/og/card-bg.png` (gradient, amber left rule, date-badge frame and domain — identical on every card) with variable text via `images.Text`, using `assets/fonts/Inter-{Regular,Bold}.ttf`.

The layout is an agenda-style badge on the left, title and a secondary line on the right. The badge carries three texts — an amber header, a large number, a footer — whose meaning varies by page type:

| Page | Badge | Title | Secondary line |
|---|---|---|---|
| Event | `JEU` / `8` / `OCTOBRE` | event title | time · organising group(s) |
| Multi-day event | `JEU` / `13` / amber `→ 14` / `NOVEMBRE` | event title | time · group(s) |
| Month `YYYY-MM` | `AGENDA` / `13` / `ÉVÉNEMENTS` | `Octobre 2026` | `Tous les meetups tech du mois` |
| Homepage, `/meetups/` | `CE MOIS` / `13` / `ÉVÉNEMENTS` | site title | `params.ogTagline` |

When a multi-day event spans two months the badge footer becomes `SEPT. → OCT.`.

Events with `cancelled: true` get a large red cross over the whole card, plus a
veil that mutes the content underneath. It stays legible at a 200 px thumbnail,
where a mere word would vanish.

Things to know before touching it:

- **Everything informative is large on purpose.** The card is usually seen as a thumbnail (chat preview, LinkedIn feed) where 30 px renders at ~8 px and becomes unreadable. Nothing informative goes below 38 px; only the domain is smaller, and it lives in the background, not in the template.
- **`images.Text` has no automatic line wrapping.** `text-wrap.html` breaks by *character count*, since font metrics aren't available in templates. Two factors convert pixels to characters in `og-image.html`: `$advance` (0.60) for the mixed-case title and secondary line, and `$advanceCaps` (0.72) for the badge's uppercase footer. These are the knobs to adjust if text overflows.
- **`$advance` is a high percentile, not an average.** Measured over the 663 words of the site's titles, Inter Bold's real advance has a median of 0.543 but a p90 of 0.646. A width budget set on the median leaves every other line wider than predicted, which is how capital-heavy titles like `Grenoble Game` ended up 29 px from the card edge. 0.60 sits between the two.
- **Font sizes are adaptive**, using the same "largest that fits" loop in three places: the title (104/92/80/70/60/52 px), the badge footer (40/36/32/28 px — `SEPTEMBRE` and `ÉVÉNEMENTS` need the smaller steps), and the badge number (132 px instead of 180 when it has 3+ digits). The title's line budget subtracts the space the secondary line needs — without that, a five-line title fills the zone alone and the whole block overflows upward.
- **The secondary line follows the title** rather than sitting at a fixed `y`, and the whole title block is vertically centred. Both matter: a fixed `y` leaves a visible hole under short titles like `CARA Beer`.
- **Emoji are stripped from titles.** Go's text rendering has no colour-font support, so they would render as tofu.
- **Margins are deliberately tight** (64 px left, 60 right, 72 top), because the channels this site posts to — LinkedIn and chat unfurls — render the full 1.91:1 without cropping. The "centred 80 %" safe area that image guides recommend only matters for Facebook mobile and Twitter `summary` cards, which crop to a square.
- **The badge frame is static, only its text varies.** Hugo can only vary text, so any new shape must be identical on every card and belongs in `gen_og_background.py`. The geometry constants in that script and the anchor coordinates in `og-image.html` must be kept in sync by hand.
- **`images.Overlay` is the escape hatch for a conditional shape.** The cancelled cross (`assets/og/card-cancelled.png`) is one static layer applied only when `cancelled: true`, appended last so it sits above the text. Use the same trick for any future shape that varies by *condition* rather than by *value* — Hugo still cannot draw one that varies per page.
- Hugo names each card after a hash of its content, so editing an event yields a *new* URL — LinkedIn and Google caches are bypassed by construction.
- `tools/gen_og_background.py` regenerates the background (`uv run --with pillow tools/gen_og_background.py`). Run it only when the background design changes; the PNG is committed.
- Fonts must be **static** TTFs. Go cannot parse variable fonts — the system's `Ubuntu-B.ttf` and friends are symlinks to a single variable file and are unusable here.

## Design

Palette used across the site and favicon:

| Role | Value |
|---|---|
| Favicon gradient start | `#93c5fd` (bleu ciel) |
| Favicon gradient end | `#1d4ed8` (bleu roi) |
| Favicon accent (`</>`) | `#f59e0b` (amber/or) |
| Link / UI blue | `#2563eb` |
| Body text | `#111` |
| Muted text | `#555` |
| Social card gradient | `#2563eb` → `#0c1e4a` |
| Social card secondary text | `#dbeafe` |

The social card deliberately runs darker than the favicon: it is viewed against LinkedIn's white feed, where a dark card stands out, and white text needs the contrast that the favicon's light `#93c5fd` corner does not give.

The favicon (`static/favicon.svg`) is a calendar icon with a `</>` code tag — gradient background ↘, white card, amber accent.

## Deployment

Push to `main` triggers GitHub Actions (`hugo.yml`) which builds and deploys to GitHub Pages. The workflow also runs on a monthly cron (`0 2 1 * *`) to refresh the homepage's "current month" view.

## Skills

Use `/add-meetup` when adding new meetup events from a text list — it handles file creation, naming, front matter, and conventions automatically.

Use `/newsletter-linkedin` when preparing the monthly LinkedIn post — it covers sanity check, post text, carousel generation, and the Slack relay text.
