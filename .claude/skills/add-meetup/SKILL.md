# Add Meetup

Given a text list of events, generate Hugo content files in `content/meetups/` matching the existing front-matter and naming conventions.

## File structure

Each month lives in its own directory: `content/meetups/YYYY-MM/`

Two file types:

**1. Month index — `content/meetups/YYYY-MM/_index.md`**
```yaml
---
title: "<Month name in French> YYYY"
date: YYYY-MM-01
linkedinPost: https://...   # optional — omit if not provided
---
```

**2. Event file — `content/meetups/YYYY-MM/YYYY-MM-DD-slug.md`**
```yaml
---
title: "<Event title with emoji at end>"
date: YYYY-MM-DD
time: "19:00"   # HH:MM preferred; or "midi" / "après-midi" / "soir" — optional, omit if unknown
location:       # optional — omit if unknown
  name: "La Casemate"
  address: "1 Place Saint-Laurent, Grenoble"  # optional
  url: "https://maps.app.goo.gl/..."          # optional — map or venue site
links:
  - url: "https://..."   # optional — omit if no URL provided
---
```

## Naming conventions

- Directory: `YYYY-MM` (zero-padded month)
- File: `YYYY-MM-DD-kebab-case-slug.md` — slug is 1–4 words from the title, lowercase, hyphens, no accents
- Emoji at end of title is encouraged but optional

## Steps

1. **Read two existing event files** from the most recent month to confirm current conventions before generating anything.
2. **Group events by month.** For each month:
   - Create `content/meetups/YYYY-MM/` directory if it does not exist.
   - Create `_index.md` if it does not exist (no `linkedinPost` until provided).
   - Create one `.md` file per event.
3. **Suggest missing optional fields.** After creating each event file, if any optional field was omitted, ask the user if they want to provide it. Example: *"Tu peux aussi me donner : l'heure (format HH:MM comme "19:00", ou midi/après-midi/soir), le lieu (nom, adresse, lien maps), un lien, et/ou une description."*
4. **Hugo hides future-dated content by default.** After generating, remind the user to build with `hugo --buildFuture` or set `buildFuture = true` in `hugo.toml` to see upcoming events locally.
5. List every file created so the user can verify before committing.

## What to infer

- If no URL is given for an event, omit the `links` block entirely.
- If no time is given, omit the `time` field.
- Derive the slug from the French or English event name; strip accents, lowercase, hyphenate.
- If a month `_index.md` already exists, do not overwrite it.
