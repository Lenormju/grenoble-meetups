# Add Meetup

Given a text list of events, generate Hugo content files in `content/meetups/` matching the existing front-matter and naming conventions.

## File structure

Each month lives in its own directory: `content/meetups/YYYY-MM/`

Two file types:

**1. Month index — `content/meetups/YYYY-MM/_index.md`**
```yaml
---
title: "<Month name in French> YYYY"
date: "YYYY-MM-01"
linkedinPost: "https://..."   # optional — omit if not provided
---
```

**2. Event file — `content/meetups/YYYY-MM/YYYY-MM-DD-slug.md`**
```yaml
---
title: "<Event title with emoji at end>"
description: "..."  # required — one sentence; see "Descriptions" for how to obtain it
startDate: "YYYY-MM-DD"
startTime: "19:00"   # HH:MM strongly preferred (drives the iCal feed's event start); "midi" / "après-midi" / "soir" accepted as a fallback — omit only if truly unknown
endDate: "YYYY-MM-DD"  # optional — only for multi-day events (conferences, festivals)
endTime: "20:00"  # optional — time on endDate (else startDate); same grammar as startTime, HH:MM/midi/après-midi/soir
groups: ["slug"]  # required — organizer group slug(s), e.g. ["humantalks"] or ["securimag", "hackerspace"]
location:       # optional — omit if unknown
  name: "La Casemate"
  address: "1 Place Saint-Laurent, Grenoble"  # optional
  city: "Échirolles"  # optional — REQUIRED when the venue is outside Grenoble (Échirolles, Saint-Martin-d'Hères, Montbonnot-Saint-Martin…); omit for Grenoble
  url: "https://maps.app.goo.gl/..."          # optional — map or venue site
links:
  - url: "https://..."   # optional — omit if no URL provided
    label: "S'inscrire"  # always set one — see "Link labels" below
price: "payant"  # optional — omit if free (the default); "payant" for a ticketed event whose tarif we don't track, or a number for a known price in EUR
---
```

`price` is invisible on the page — it only feeds the `offers` of the `Event` JSON-LD. Omitting it
asserts the event is free, which is correct for nearly every meetup. Set `"payant"` for ticketed
conferences (DrupalCamp, GreHack, Alpes Craft, Agile Games Alpes…) rather than guessing an amount.

## Quoting

**Quote everything except booleans and numbers.** No exceptions for dates.

```yaml
startDate: "2026-11-05"    # quoted — yes, including dates
startTime: "soir"          # quoted
endDate: "2026-11-07"      # quoted
title: "Meetup CARA 🏢"    # quoted
linkedinPost: "https://…"  # quoted
price: "payant"            # quoted when a word…
price: 15                  # …bare when a number
cancelled: true            # bare — a boolean; quoting it breaks the site, see below
```

This is defensive, not load-bearing: Hugo 0.162 does not coerce these values —
a bare `19:00` stays the string `19:00` (no YAML 1.1 sexagesimal), a bare
`2026-11-07` in a custom param arrives as a string rather than a `time.Time`,
and a quoted date still parses into a real `time.Time` for `.Date`. Every form
builds byte-identical output. Quote anyway, because it costs nothing and removes
a thing to reason about.

Dates were bare in all 127 files until they were normalised in one pass; the
built site came back byte-identical, which is the check to repeat if this ever
needs doing again. There is **no semantic distinction** between `startDate` and
`endDate` here — if you find yourself explaining why one is quoted and the other
isn't, the answer is that they both should be.

Watch the two exceptions in that list, because `cancelled` is the one field
where quoting actively breaks the site — and it breaks it *inconsistently*,
which is why it's easy to miss. Probed on Hugo 0.162:

| Front matter | `{{ if .Params.cancelled }}`<br>(`single.html` banner + `eventStatus`) | `where … "Params.cancelled" "ne" true`<br>(calendar grid, RSS) |
|---|---|---|
| `cancelled: true` | cancelled ✓ | filtered out ✓ |
| `cancelled: "true"` | cancelled | **kept — `eq "true" true` is false** |
| `cancelled: "false"` | **cancelled** (any non-empty string is truthy) | kept |

So `cancelled: "true"` yields a half-cancelled event: the detail page says
*Cet événement a été annulé*, while the homepage calendar and the RSS feed go on
advertising it. Keep it bare. Likewise a numeric `price` must stay bare to
remain a number.

## Naming conventions

- Directory: `YYYY-MM` (zero-padded month)
- File: `YYYY-MM-DD-kebab-case-slug.md` — slug is 1–4 words from the title, lowercase, hyphens, no accents
- Emoji at end of title is encouraged but optional

## Steps

1. **Read two existing event files** from the most recent month to confirm current conventions before generating anything.
1b. **Identify the organizer group(s).** Check `content/groups/` for an existing slug matching the organizer. If no match exists, create `content/groups/<new-slug>/_index.md` with `title: "Organizer Name"` before creating the event file. Every event must have at least one group.
1c. **Reuse known venue locations.** If a venue name is given (or inferable), search past events for it first, e.g. `grep -ril "turbine" content/meetups/` then check the matching `location:` blocks. Match loosely — punctuation/case/typo variants like "La Turbine.coop" and "Turbine.Coop" are the same venue. If found, reuse that exact `name`/`address`/`city`/`url` rather than asking the user or inventing a new address. If multiple past events disagree on the address, prefer the most recent one and flag the mismatch to the user.
   - **Grenoble has two valid postcodes, 38000 and 38100, but each address has only one canonical form.** When the same street address appears with both, it's a mistake, not a variant — ask which is right instead of copying the most recent. Known: `31 Rue Gustave Eiffel` is 38000.
   - **One street address can host several venues.** `31 Rue Gustave Eiffel` is both SII and Wizbii. Match on the venue *name* first; a shared address is not evidence that two events were at the same place, and the name the user gives wins over the one already on file.
2. **Group events by month.** For each month:
   - Create `content/meetups/YYYY-MM/` directory if it does not exist.
   - Create `_index.md` if it does not exist (no `linkedinPost` until provided).
   - Create one `.md` file per event.
3. **Fill the description** by working down the "Descriptions" list — resolve the event's link before
   settling for a derived one. Report which ones you sourced and which you derived.
4. **Suggest missing optional fields.** After creating each event file, if any optional field was omitted, ask the user if they want to provide it — lead with the start time, since it's the field most worth chasing down (see "What to infer" below). If the event has an `endDate`, chase the end time just as hard — without it the span shows all-day and `startTime` drops out of the feed. Example: *"Tu peux aussi me donner : l'heure de début (format HH:MM comme "19:00", ou midi/après-midi/soir — important, sinon l'évènement apparaît toute la journée dans le calendrier), l'heure de fin si tu la connais (surtout si l'événement dure plusieurs jours), le lieu (nom, adresse, lien maps), et/ou un lien."*
5. **Hugo hides future-dated content by default.** After generating, remind the user to build with `hugo --buildFuture` or set `buildFuture = true` in `hugo.toml` to see upcoming events locally.
6. List every file created so the user can verify before committing.

## Link labels

**Always set a `label` on every link.** It is technically optional — `meetups/single.html` falls back
to `"S'inscrire"` — but leaning on that default silently ships the wrong wording whenever the link
isn't a registration page.

- `"S'inscrire"` — registration or event pages: Meetup, Gancio, Framaforms, a billetterie.
- Anything else gets a specific label. Those already in use: `"Voir sur Meetup"`,
  `"Voir ou proposer un talk"`, `"Rejoindre le Discord"`, `"Voir l'événement"`,
  `"Channel Discord meetups"`, `"Post LinkedIn"`, `"Billetterie (événement payant)"`,
  `"Prochaines conférences"`. Reuse one of these before inventing a new wording.
- When an event has several links, only the one that actually registers people gets `"S'inscrire"`.

## What to infer

- If no URL is given for an event, omit the `links` block entirely.
- **The start time matters — ask for it before omitting it.** The iCal feed (`/meetups.ics`) uses `startTime` to set the event's real start; without it, the event falls back to an all-day entry that shows as starting at midnight. Only omit the `startTime` field if the user genuinely doesn't know it after being asked.
- **Record `endTime` whenever the source gives one.** It exists and feeds the iCal feed's real end. Both `startTime` and `endTime` share one grammar — `HH:MM` (preferred) or the fuzzy `midi` / `après-midi` / `soir`; `19h`-style values are not accepted. Without an explicit `endTime`, the feed falls back to a 2-hour default from the start.
- **Always ask for `endTime` when `endDate` is set.** An `endDate` with no `endTime` is accepted, not an error, but the cost is real: the iCal feed renders the whole span as an all-day event and drops `startTime` from the feed entirely (the event page still shows it). Chase the end time down for multi-day events rather than letting that happen by default.
- When the exact hour is unknown, prefer a fuzzy value (`midi` / `après-midi` / `soir`) over omitting `startTime` or `endTime` altogether — an omitted time reads as all-day/midnight, which is worse than an approximate one.
- Derive the slug from the French or English event name; strip accents, lowercase, hyphenate.
- If a month `_index.md` already exists, do not overwrite it.
- If a venue name is given but no address/url, check for a known location first (see step 1c) before asking the user or omitting `location`.

## Titles

**Never invent a title.** The title is the one field that can't be guessed from context — it's the event's real name on Meetup/LinkedIn, and a plausible-sounding invention is worse than no file at all.

- Use the title exactly as the user gave it, or exactly as it appears on the event page.
- If the source text pasted by the user is only a *description* with no title line, **stop and ask** for the title before writing the file. Don't derive one from the body text, however obvious it seems.
- If the event URL fails to load (Meetup returns 503 to `WebFetch` fairly often), that's not a licence to infer — ask.
- Appending an emoji at the end of a title the user gave is fine (it's the site convention), but nothing else about the wording changes.

## Descriptions

**A description must always be present**, and unlike a title it may be *derived* rather than only
sourced or asked for. The difference is what each field asserts: an invented title claims the event's
identity, so a missing one blocks the file entirely (see "Titles"); a description derived from the
title and group asserts nothing the title doesn't already say, so it's safe to write.

It feeds the meta description, the Open Graph card and the `Event` JSON-LD; without it `seo.html`
falls back to `"<Title> — meetup tech à Grenoble"`, the same generic shape on every page. Treating
it as optional is how 20 events once shipped with no description at all.

Work down this list, and only move to the next step when the one above genuinely fails:

1. **Use the description the user gave**, as close to the source wording as possible.
2. **Summarise the event's own body.** If the file has Markdown below the front matter, the content is
   already there and needs no fetch — condense it to one sentence. Human Talks files list their four
   talks in the body, which is all a good description needs: *"Quatre talks de 10 minutes :
   programmation réactive, IA agentique et relecture de code, sécurité électrique et compilation vers
   WebAssembly."* Take the wording from the body verbatim; a talk titled *Sécurité électrique* must
   not become *sûreté*.
3. **Recover it from the event's own link.** Resolve the URL (see "Resolving event links" below) and
   take the description from the event page. This is not inventing — it's the organiser's own words.
4. **Ask the user whenever the link can't be fetched.** Auth-walled sources — Discord, LinkedIn — are
   not a dead end for *them*: they are usually a member of that Discord or can open that post, so
   they can paste the text. Say which URL you couldn't reach and why, and ask. Don't skip silently to
   step 5; a pasted blurb beats a derived sentence every time.
5. **Derive one from the title and the organising group**, once asking has come up empty.
   `Découverte du STM32` at the Hackerspace genuinely is *"Atelier de découverte du microcontrôleur
   STM32, proposé par le Hackerspace de Grenoble."* Stay strictly inside what the title and the group
   already assert — no speakers, no topics, no venue detail that isn't on file. Derived ones come out
   shorter (65–95 chars) than sourced ones (125–155); that's honest, not a defect.

Steps 1–4 are the organiser's words and can be trusted as fact. Step 5 is your own sentence, so it
gets the tightest leash. When a batch has several unfetchable links, ask about them **together** in
one message rather than one question per event.

**Never write a shared placeholder.** Several pages carrying one identical generic sentence is worse
than the generated fallback — that at least varies with the title — and it destroys
`grep -rL '^description:' content/meetups --include='*.md'` as the way to find what's still missing.

Keep given wording close to the source: don't rephrase or restyle text that's already usable. Edit
only as needed (trimming to one sentence, fixing a typo, adding punctuation), preferring the
smallest change that works. Whenever you write or change wording — including deriving one at step 4
— tell the user what you added so they can review it.

Place `description` **directly after `title:`** — all 113 event files do. That's line 3 normally, and
line 4 in the three cancelled events, which carry `cancelled: true` on line 2. Anchor on the `title:`
line, not on a line number. (The front-matter example in `CLAUDE.md` once showed `description` after
`links:`; the files are the authority.)

## Resolving event links

Source lists are usually pasted from LinkedIn, so the URLs are rarely the event page itself.

- **`lnkd.in/xxxx` (LinkedIn shortener).** Does *not* send an HTTP redirect — it returns 200 with a
  JS interstitial, so `curl -I` and `%{redirect_url}` both come back empty. The real target is in
  the page body:
  ```bash
  curl -sS "https://lnkd.in/dXXXXXXX" | grep -oE 'https?://[^"'"'"'<> ]+' \
    | grep -viE 'lnkd\.in|licdn|w3\.org|schema\.org' | head -3
  ```
  These mostly resolve to Meetup event pages, which `WebFetch` reads fine.
- **`discord.com/channels/...` needs auth and is never fetchable.** Don't spend a fetch on it — **ask
  the user instead** (step 4 of "Descriptions"); they're usually in that Discord. Note too that
  several different events often share *one* Discord channel link, so the URL isn't event-specific
  even in principle, and the user may have to look up the right message.
- **`linkedin.com/feed/update/...`** is not fetchable either — same move: ask the user to paste the
  post text. They may confirm it holds no event detail, which is the answer that unlocks step 5.
- **Hackerspace has a machine-readable calendar.** `content/groups/hackerspace/_index.md` points at
  a [Gancio](https://gancio.ghspace.fr/) instance with a JSON API:
  ```bash
  curl -sS "https://gancio.ghspace.fr/api/events?start=$(date +%s)&end=$(($(date +%s)+5184000))"
  ```
  Each entry carries `title`, `start_datetime`, `description` and place — ideal for adding
  Hackerspace events. **It only serves upcoming events**: a window in the past returns `[]`, so
  descriptions must be captured while the event is still ahead. Once it's gone, it's gone.

## Recurring meetup conventions

**Give each occurrence its own description.** A series has one fixed *format*, but the description
should describe *this* month's edition — the talk titles, the topic, the episode. Copying one
canonical sentence onto every occurrence is what left ~32 pages sharing 10 strings, and it wastes
the one field that could distinguish them in search results. The fixed descriptions below are
fallbacks for when the lineup genuinely isn't known yet, not the default.

Keep occurrences distinct even when the source blurb is identical for all of them (Meetup serves one
recurring blurb for the whole `robot-simulator-python` series, for instance) — vary the phrasing
across the same facts rather than pasting one string N times.

### Human Talks Grenoble (`groups: ["humantalks"]`)

Recurring on the 2nd Tuesday of each month (with exceptions). Always 4 talks of 10 minutes each (with exceptions). Use these fixed values:

```yaml
---
title: "Human Talks Grenoble 🎤"
description: "<voir ci-dessous — nommer les talks du mois quand ils sont connus>"
startDate: "YYYY-MM-DD"
startTime: "19:00"
groups: ["humantalks"]
location:
  name: "<venue name>"
  address: "<address>"
links:
  - url: "https://www.meetup.com/humantalks-grenoble/events/..."
    label: "S'inscrire"
  - url: "https://humantalks.com/cities/grenoble/events/..."
    label: "Voir ou proposer un talk"
---

Au programme, 4 talks de 10 minutes :

- *Titre du talk* — Prénom NOM
```

- Slug: `YYYY-MM-DD-human-talks.md`
- List known talks in the body as `- *Titre* — Prénom NOM`. Omit unknown talks (don't add placeholders).
- **The description names the month's talks** — that's step 2 of "Descriptions", since the body
  already lists them. Only when the lineup is still unknown, fall back to the generic
  *"Quatre conférences de 10 minutes chacune sur des sujets variés — technos, méthodes, retours
  d'expérience, side projects — suivies d'un apéritif."*, and replace it once the talks are announced.
- The `humantalks.com/cities/grenoble/events/<id>` link is the specific event page (e.g. `https://humantalks.com/cities/grenoble/events/1228`). It serves both purposes on its own — it's where the talk lineup and slides get published, *and* it carries the "Proposer un talk" button — hence the single "Voir ou proposer un talk" link. Don't also add the generic `/cities/grenoble/` city page; it's redundant. Ask for the event URL if not given; omit that link line if the user doesn't have it.
- Some older event files still carry the previous two-link form (`"Voir les talks"` + a separate `"Proposer un talk"`). That's intentional — leave them as they are.
