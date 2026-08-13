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
description: ""  # Une phrase décrivant le meetup
date: YYYY-MM-DD
time: "19:00"   # HH:MM strongly preferred (drives the iCal feed's event start); "midi" / "après-midi" / "soir" accepted as a fallback — omit only if truly unknown
groups: ["slug"]  # required — organizer group slug(s), e.g. ["humantalks"] or ["securimag", "hackerspace"]
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
1b. **Identify the organizer group(s).** Check `content/groups/` for an existing slug matching the organizer. If no match exists, create `content/groups/<new-slug>/_index.md` with `title: "Organizer Name"` before creating the event file. Every event must have at least one group.
1c. **Reuse known venue locations.** If a venue name is given (or inferable), search past events for it first, e.g. `grep -ril "turbine" content/meetups/` then check the matching `location:` blocks. Match loosely — punctuation/case/typo variants like "La Turbine.coop" and "Turbine.Coop" are the same venue. If found, reuse that exact `name`/`address`/`url` rather than asking the user or inventing a new address. If multiple past events disagree on the address, prefer the most recent one and flag the mismatch to the user.
2. **Group events by month.** For each month:
   - Create `content/meetups/YYYY-MM/` directory if it does not exist.
   - Create `_index.md` if it does not exist (no `linkedinPost` until provided).
   - Create one `.md` file per event.
3. **Suggest missing optional fields.** After creating each event file, if any optional field was omitted, ask the user if they want to provide it — lead with the start time, since it's the field most worth chasing down (see "What to infer" below). Example: *"Tu peux aussi me donner : l'heure de début (format HH:MM comme "19:00", ou midi/après-midi/soir — important, sinon l'évènement apparaît toute la journée dans le calendrier), une description (une phrase décrivant le meetup), le lieu (nom, adresse, lien maps), et/ou un lien."*
4. **Hugo hides future-dated content by default.** After generating, remind the user to build with `hugo --buildFuture` or set `buildFuture = true` in `hugo.toml` to see upcoming events locally.
5. List every file created so the user can verify before committing.

## What to infer

- If no URL is given for an event, omit the `links` block entirely.
- **The start time matters — ask for it before omitting it.** The iCal feed (`/meetups.ics`) uses `time` to set the event's real start; without it, the event falls back to an all-day entry that shows as starting at midnight. Only omit the `time` field if the user genuinely doesn't know it after being asked.
- The iCal feed has no way to know an event's actual end time or duration — it always assumes **2 hours** from the start time. No front-matter field controls this; it's not worth asking the user for an end time.
- Derive the slug from the French or English event name; strip accents, lowercase, hyphenate.
- If a month `_index.md` already exists, do not overwrite it.
- If a venue name is given but no address/url, check for a known location first (see step 1c) before asking the user or omitting `location`.

## Descriptions

Keep the event's `description` field and any longer body text as close to the source wording as possible — do not rephrase or restyle text that's already usable. Only edit when needed (e.g. trimming to one sentence, fixing a typo, adding punctuation, light grammar fixes), and prefer the smallest change that works. If you do change or write wording (including writing a `description` from scratch when none was given), tell the user what you added or changed so they can review it.

## Recurring meetup conventions

### Human Talks Grenoble (`groups: ["humantalks"]`)

Recurring on the 2nd Tuesday of each month (with exceptions). Always 4 talks of 10 minutes each (with exceptions). Use these fixed values:

```yaml
---
title: "Human Talks Grenoble 🎤"
description: "Quatre conférences de 10 minutes chacune sur des sujets variés — technos, méthodes, retours d'expérience, side projects — suivies d'un apéritif."
date: YYYY-MM-DD
time: "19:00"
groups: ["humantalks"]
location:
  name: "<venue name>"
  address: "<address>"
links:
  - url: "https://www.meetup.com/humantalks-grenoble/events/..."
    label: "S'inscrire"
  - url: "https://humantalks.com/cities/grenoble/"
    label: "Proposer un talk"
---

Au programme, 4 talks de 10 minutes :

- *Titre du talk* — Prénom NOM
```

- Slug: `YYYY-MM-DD-human-talks.md`
- List known talks in the body as `- *Titre* — Prénom NOM`. Omit unknown talks (don't add placeholders).
