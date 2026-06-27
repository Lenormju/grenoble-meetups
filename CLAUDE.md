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
title: "Event name with emoji at end 🎤"
date: YYYY-MM-DD
time: "soir"       # midi | après-midi | soir | HH:MM (e.g. "19:00") — omit if unknown
endDate: YYYY-MM-DD  # optional, for multi-day events
location:            # optional
  name: "La Casemate"
  address: "1 Place Saint-Laurent, Grenoble"  # optional
links:
  - url: "https://..."
    label: "Custom label"  # optional, defaults to "S'inscrire"
description: "One-sentence summary for SEO"  # recommended
---
Optional longer description in Markdown.
```

### Month `_index.md` front matter

```yaml
---
title: "Mois YYYY"
date: YYYY-MM-01
linkedinPost: https://...   # optional
---
```

### Naming conventions

- Directory: `YYYY-MM`
- File: `YYYY-MM-DD-kebab-case-slug.md` — slug is 1–4 words, no accents, lowercase, hyphens

## Layouts

- `layouts/index.html` — real homepage at `/`, shows the current month's meetups
- `layouts/meetups/list.html` — renders `/meetups/` (current month calendar + past months list) and `/meetups/YYYY-MM/` (single month calendar)
- `layouts/meetups/single.html` — event detail page
- `layouts/partials/month-calendar.html` — calendar grid partial; supports `endDate` for multi-day event spans
- `layouts/partials/fr-month-name.html` — French month name helper
- `layouts/_default/rss.xml` — RSS feed at `/index.xml`, lists all individual meetup events sorted by date (newest first, max 50)

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

The favicon (`static/favicon.svg`) is a calendar icon with a `</>` code tag — gradient background ↘, white card, amber accent.

## Deployment

Push to `main` triggers GitHub Actions (`hugo.yml`) which builds and deploys to GitHub Pages. The workflow also runs on a monthly cron (`0 2 1 * *`) to refresh the homepage's "current month" view.

## Skills

Use `/add-meetup` when adding new meetup events from a text list — it handles file creation, naming, front matter, and conventions automatically.

Use `/newsletter-linkedin` when preparing the monthly LinkedIn post — it covers sanity check, post text, and calendar image generation.
