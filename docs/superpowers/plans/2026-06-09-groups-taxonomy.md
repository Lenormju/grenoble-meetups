# Groups Taxonomy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `groups` taxonomy to the Hugo site so each event belongs to a named group, enabling per-group event listing pages (`/groups/humantalks/`) and a client-side group filter above the monthly calendar.

**Architecture:** Hugo's native taxonomy system (`group = "groups"` in `hugo.toml`) auto-generates group pages from `groups:` front matter on events. Each group has a minimal `content/groups/<slug>/_index.md` providing a display name. Client-side JS in `month-calendar.html` filters visible events by reading `data-groups` attributes on event items.

**Tech Stack:** Hugo 0.162, HTML/CSS, vanilla JS (no dependencies)

---

## File Map

| File | Action |
|---|---|
| `hugo.toml` | Add `group = "groups"` to `[taxonomies]` |
| `content/groups/*/_ index.md` | Create ~20 group files |
| `layouts/groups/list.html` | Create — renders `/groups/<slug>/` |
| `layouts/groups/terms.html` | Create — renders `/groups/` |
| `layouts/partials/month-calendar.html` | Add `data-groups` on `<li>` + filter tag row + JS |
| `static/style.css` | Add filter tag and group page styles |
| `content/meetups/**/*.md` | Add `groups:` front matter to all events |
| `.claude/skills/add-meetup/SKILL.md` | Add groups step to the workflow |

---

## Task 1: Enable the groups taxonomy in Hugo

**Files:**
- Modify: `hugo.toml`

- [ ] **Step 1: Update hugo.toml**

Replace the empty `[taxonomies]` section with:

```toml
[taxonomies]
  group = "groups"
```

- [ ] **Step 2: Verify Hugo builds without errors**

```bash
hugo --gc --minify 2>&1 | tail -5
```

Expected: Build succeeds (exit 0), no taxonomy errors. Hugo will now generate `/groups/` and `/groups/<slug>/` pages (both empty until content is added).

- [ ] **Step 3: Commit**

```bash
git add hugo.toml
git commit -m "feat: enable groups taxonomy"
```

---

## Task 2: Create group content files

**Files:**
- Create: `content/groups/<slug>/_index.md` for each group below

Each file has this minimal front matter:
```yaml
---
title: "Display Name"
---
```

- [ ] **Step 1: Create all group directories and index files**

Run these commands:

```bash
mkdir -p content/groups/sicp
cat > content/groups/sicp/_index.md << 'EOF'
---
title: "SICP / Grenoble Coding Workshop"
---
EOF

mkdir -p content/groups/humantalks
cat > content/groups/humantalks/_index.md << 'EOF'
---
title: "Human Talks Grenoble"
---
EOF

mkdir -p content/groups/cara-beer
cat > content/groups/cara-beer/_index.md << 'EOF'
---
title: "CARA-Beer"
---
EOF

mkdir -p content/groups/hackerspace
cat > content/groups/hackerspace/_index.md << 'EOF'
---
title: "Hackerspace de Grenoble"
---
EOF

mkdir -p content/groups/securimag
cat > content/groups/securimag/_index.md << 'EOF'
---
title: "Securimag"
---
EOF

mkdir -p content/groups/game-dev
cat > content/groups/game-dev/_index.md << 'EOF'
---
title: "Grenoble Game Dev"
---
EOF

mkdir -p content/groups/python-grenoble
cat > content/groups/python-grenoble/_index.md << 'EOF'
---
title: "Python Grenoble"
---
EOF

mkdir -p content/groups/alpes-craft
cat > content/groups/alpes-craft/_index.md << 'EOF'
---
title: "Alpes Craft"
---
EOF

mkdir -p content/groups/alpesjug
cat > content/groups/alpesjug/_index.md << 'EOF'
---
title: "AlpesJUG"
---
EOF

mkdir -p content/groups/saas-connected-systems
cat > content/groups/saas-connected-systems/_index.md << 'EOF'
---
title: "SaaS & Connected Systems Leaders"
---
EOF

mkdir -p content/groups/powerbi-grenoble
cat > content/groups/powerbi-grenoble/_index.md << 'EOF'
---
title: "Power BI User Group Grenoble"
---
EOF

mkdir -p content/groups/aixperience
cat > content/groups/aixperience/_index.md << 'EOF'
---
title: "AiXperience"
---
EOF

mkdir -p content/groups/pmi-rhone-alpes
cat > content/groups/pmi-rhone-alpes/_index.md << 'EOF'
---
title: "PMI Rhône-Alpes"
---
EOF

mkdir -p content/groups/campus-agile
cat > content/groups/campus-agile/_index.md << 'EOF'
---
title: "Campus Agile"
---
EOF

mkdir -p content/groups/femmes-tech-isere
cat > content/groups/femmes-tech-isere/_index.md << 'EOF'
---
title: "Femmes dans la tech / Isère"
---
EOF

mkdir -p content/groups/wikimedia
cat > content/groups/wikimedia/_index.md << 'EOF'
---
title: "Wikimédia"
---
EOF

mkdir -p content/groups/grenoble-data-science
cat > content/groups/grenoble-data-science/_index.md << 'EOF'
---
title: "Grenoble Data Science"
---
EOF

mkdir -p content/groups/gresille
cat > content/groups/gresille/_index.md << 'EOF'
---
title: "Grésille"
---
EOF

mkdir -p content/groups/drupalcamp
cat > content/groups/drupalcamp/_index.md << 'EOF'
---
title: "DrupalCamp"
---
EOF

mkdir -p content/groups/snowcamp
cat > content/groups/snowcamp/_index.md << 'EOF'
---
title: "Snowcamp"
---
EOF
```

- [ ] **Step 2: Verify Hugo builds and generates group pages**

```bash
hugo --gc --minify 2>&1 | tail -5
```

Expected: Build succeeds. `/public/groups/` directory now exists but pages are empty (no events assigned yet).

- [ ] **Step 3: Commit**

```bash
git add content/groups/
git commit -m "feat: add group content files for known organizers"
```

---

## Task 3: Create group page layouts

**Files:**
- Create: `layouts/groups/list.html`
- Create: `layouts/groups/terms.html`

- [ ] **Step 1: Create the group term page layout (`/groups/<slug>/`)**

Create `layouts/groups/list.html`:

```html
{{ define "main" }}
{{ $now := now }}
{{ $future := where .Pages "Date" ">=" $now }}
{{ $past := where .Pages "Date" "<" $now }}

<div class="page-actions page-actions--right">
  <button class="permalink-btn" onclick="navigator.clipboard.writeText(window.location.href).then(()=>{this.textContent='✓ Copié !';setTimeout(()=>{this.textContent='🔗 Copier le lien'},2000)})">🔗 Copier le lien</button>
</div>

<h1>{{ .Title }}</h1>

{{ if $future }}
<section class="group-events">
  <h2>À venir</h2>
  <ul class="group-event-list">
    {{ range $future.ByDate }}
    <li>
      <span class="event-day">{{ .Date.Format "02/01/2006" }}</span>
      <a href="{{ .RelPermalink }}">{{ .Title }}</a>
    </li>
    {{ end }}
  </ul>
</section>
{{ end }}

{{ if $past }}
<section class="group-events">
  <h2>Passés</h2>
  <ul class="group-event-list">
    {{ range $past.ByDate.Reverse }}
    <li>
      <span class="event-day">{{ .Date.Format "02/01/2006" }}</span>
      <a href="{{ .RelPermalink }}">{{ .Title }}</a>
    </li>
    {{ end }}
  </ul>
</section>
{{ end }}

{{ if and (not $future) (not $past) }}
<p style="color:#888">Aucun événement pour ce groupe.</p>
{{ end }}

{{ end }}
```

- [ ] **Step 2: Create the groups index layout (`/groups/`)**

Create `layouts/groups/terms.html`:

```html
{{ define "main" }}
<h1>Groupes</h1>
<ul class="groups-list">
  {{ range .Data.Terms.ByCount }}
  <li>
    <a href="{{ .Page.RelPermalink }}">{{ .Page.Title }}</a>
    <span class="event-count">{{ .Count }} événement{{ if gt .Count 1 }}s{{ end }}</span>
  </li>
  {{ end }}
</ul>
{{ end }}
```

- [ ] **Step 3: Verify layouts render without errors**

```bash
hugo server --buildFuture 2>&1 | grep -E "ERROR|WARN" | head -20
```

Expected: No ERROR lines. Visit `http://localhost:1313/groups/` and `http://localhost:1313/groups/sicp/` in a browser — pages render (empty event lists until Task 6).

- [ ] **Step 4: Commit**

```bash
git add layouts/groups/
git commit -m "feat: add group listing and terms layouts"
```

---

## Task 4: Add CSS for group filter and group pages

**Files:**
- Modify: `static/style.css`

- [ ] **Step 1: Append group styles to static/style.css**

Add at the end of `static/style.css`:

```css
/* ─── Group filter tags ───────────────────────── */
.group-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 1rem;
}
.group-tag {
  background: none;
  border: 1px solid #ddd;
  border-radius: 999px;
  padding: 0.2rem 0.65rem;
  font-size: 0.78rem;
  cursor: pointer;
  color: #555;
  font-family: inherit;
  line-height: 1.5;
  transition: background 0.1s, color 0.1s, border-color 0.1s;
}
.group-tag:hover {
  border-color: #aaa;
  color: #111;
}
.group-tag.active {
  background: #111;
  color: #fff;
  border-color: #111;
}

/* ─── Group page event list ───────────────────── */
.group-events {
  margin-bottom: 2rem;
}
.group-events h2 {
  font-size: 1rem;
  margin: 0 0 0.5rem 0;
  color: #555;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.3rem;
}
.group-event-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.group-event-list li {
  padding: 0.3rem 0;
  font-size: 0.9rem;
  border-bottom: 1px solid #f5f5f5;
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
}

/* ─── Groups index page ───────────────────────── */
.groups-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.groups-list li {
  padding: 0.4rem 0;
  border-bottom: 1px solid #f5f5f5;
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  font-size: 0.95rem;
}
```

- [ ] **Step 2: Commit**

```bash
git add static/style.css
git commit -m "feat: add group filter tag and group page styles"
```

---

## Task 5: Update calendar partial — data-groups attribute and filter tags

**Files:**
- Modify: `layouts/partials/month-calendar.html`

- [ ] **Step 1: Add group slug collection and filter tags above the day headers**

In `layouts/partials/month-calendar.html`, after line 8 (`{{ $month := .month }}`), insert the group slug collection block:

```go-template
{{/* Collect unique group slugs present in this month's events */}}
{{ $groupSlugs := slice }}
{{ range $events }}
  {{ range .Params.groups }}
    {{ if not (in $groupSlugs .) }}
      {{ $groupSlugs = $groupSlugs | append . }}
    {{ end }}
  {{ end }}
{{ end }}
```

- [ ] **Step 2: Insert filter tags HTML before the day headers div**

Insert before `<div class="calendar-day-headers" aria-hidden="true">`:

```go-template
{{ if $groupSlugs }}
<div class="group-filters">
  <button class="group-tag active" data-filter="all">Tous</button>
  {{ range $groupSlugs }}
    {{ $slug := . }}
    {{ $title := $slug }}
    {{ with site.GetPage (printf "/groups/%s" $slug) }}
      {{ $title = .Title }}
    {{ end }}
    <button class="group-tag" data-filter="{{ $slug }}">{{ $title }}</button>
  {{ end }}
</div>
{{ end }}
```

- [ ] **Step 3: Add data-groups attribute to each event list item**

Find the line:
```go-template
<li class="event-item{{ if .Params.endDate }} event-multiday{{ end }}">
```

Replace with:
```go-template
<li class="event-item{{ if .Params.endDate }} event-multiday{{ end }}"{{ with .Params.groups }} data-groups="{{ delimit . " " }}"{{ end }}>
```

- [ ] **Step 4: Add filter JS at the end of the partial, after the closing `</div>` of `.calendar-grid`**

```html
{{ if $groupSlugs }}
<script>
(function () {
  var tags = document.querySelectorAll('.group-tag');
  tags.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var filter = this.dataset.filter;
      tags.forEach(function (b) { b.classList.remove('active'); });
      this.classList.add('active');
      document.querySelectorAll('.event-item').forEach(function (item) {
        if (filter === 'all') {
          item.style.opacity = '';
        } else {
          var groups = item.dataset.groups ? item.dataset.groups.split(' ') : [];
          item.style.opacity = groups.indexOf(filter) !== -1 ? '' : '0.2';
        }
      });
    });
  });
})();
</script>
{{ end }}
```

- [ ] **Step 5: Verify the partial renders correctly**

```bash
hugo server --buildFuture 2>&1 | grep -E "ERROR|WARN" | head -20
```

Expected: No errors. Visit `http://localhost:1313/` in a browser. The filter tags won't appear yet (no `groups:` in any event front matter). That's expected — they'll appear after Task 6.

- [ ] **Step 6: Commit**

```bash
git add layouts/partials/month-calendar.html
git commit -m "feat: add group filter tags and data-groups to calendar partial"
```

---

## Task 6: Add groups front matter to all existing events

**Files:**
- Modify: All `content/meetups/**/*.md` event files

**⚠ 9 events have unknown organizers** (short redirect links that can't be resolved programmatically). These are listed in Step 2 with instructions for manual research.

- [ ] **Step 1: Add `groups:` to all events with confirmed organizers**

For each file, insert `groups: ["<slug>"]` after the `date:` line. Here is the complete assignment list:

```
# April 2026
content/meetups/2026-04/2026-04-02-hackerspace-containers-gitops.md  → groups: ["hackerspace"]
content/meetups/2026-04/2026-04-02-sicp.md                           → groups: ["sicp"]
content/meetups/2026-04/2026-04-04-robot-simulator-python.md         → groups: ["python-grenoble"]
content/meetups/2026-04/2026-04-09-drupalcamp.md                     → groups: ["drupalcamp"]
content/meetups/2026-04/2026-04-09-hackerspace-vie-privee.md         → groups: ["hackerspace"]
content/meetups/2026-04/2026-04-11-robot-simulator-python.md         → groups: ["python-grenoble"]
content/meetups/2026-04/2026-04-14-human-talks.md                    → groups: ["humantalks"]
content/meetups/2026-04/2026-04-15-game-dev.md                       → groups: ["game-dev"]
content/meetups/2026-04/2026-04-15-securimag-phown.md                → groups: ["securimag"]
content/meetups/2026-04/2026-04-16-hackerspace-surete-electrique.md  → groups: ["hackerspace"]
content/meetups/2026-04/2026-04-18-robot-simulator-python.md         → groups: ["python-grenoble"]
content/meetups/2026-04/2026-04-22-securimag-cheat-jeux-video.md     → groups: ["securimag"]
content/meetups/2026-04/2026-04-23-hackerspace-assembleur-arm-x86.md → groups: ["hackerspace"]
content/meetups/2026-04/2026-04-25-robot-simulator-python.md         → groups: ["python-grenoble"]
content/meetups/2026-04/2026-04-27-securimag-secu-android.md         → groups: ["securimag"]
content/meetups/2026-04/2026-04-28-apero-python.md                   → groups: ["python-grenoble"]
content/meetups/2026-04/2026-04-30-hackerspace-stm32.md              → groups: ["hackerspace"]

# May 2026
content/meetups/2026-05/2026-05-05-cara-beer.md                      → groups: ["cara-beer"]
content/meetups/2026-05/2026-05-07-sicp.md                           → groups: ["sicp"]
content/meetups/2026-05/2026-05-12-human-talks.md                    → groups: ["humantalks"]
content/meetups/2026-05/2026-05-14-sicp.md                           → groups: ["sicp"]
content/meetups/2026-05/2026-05-21-sicp.md                           → groups: ["sicp"]
content/meetups/2026-05/2026-05-28-lightning-talks-python.md         → groups: ["python-grenoble"]
content/meetups/2026-05/2026-05-28-sicp.md                           → groups: ["sicp"]
content/meetups/2026-05/2026-05-31-tremplin-snowcamp.md              → groups: ["snowcamp"]

# June 2026
content/meetups/2026-06/2026-06-04-alpes-craft.md                    → groups: ["alpes-craft"]
content/meetups/2026-06/2026-06-04-sicp.md                           → groups: ["sicp"]
content/meetups/2026-06/2026-06-05-alpes-craft.md                    → groups: ["alpes-craft"]
content/meetups/2026-06/2026-06-08-rex-ia-agentique.md               → groups: ["saas-connected-systems"]
content/meetups/2026-06/2026-06-09-cara-beer.md                      → groups: ["cara-beer"]
content/meetups/2026-06/2026-06-09-human-talks.md                    → groups: ["humantalks"]
content/meetups/2026-06/2026-06-09-opendst.md                        → groups: ["alpesjug"]
content/meetups/2026-06/2026-06-09-powerbi-ia.md                     → groups: ["powerbi-grenoble"]
content/meetups/2026-06/2026-06-10-appli-sans-coder.md               → groups: ["aixperience"]
content/meetups/2026-06/2026-06-11-ia-levier-projets.md              → groups: ["pmi-rhone-alpes"]
content/meetups/2026-06/2026-06-11-sicp.md                           → groups: ["sicp"]
content/meetups/2026-06/2026-06-13-apres-midi-creatif.md             → groups: ["gresille"]
content/meetups/2026-06/2026-06-15-cfp-campus-agile.md               → groups: ["campus-agile"]
content/meetups/2026-06/2026-06-16-femmes-tech-criteo.md             → groups: ["femmes-tech-isere"]
content/meetups/2026-06/2026-06-17-game-dev.md                       → groups: ["game-dev"]
content/meetups/2026-06/2026-06-18-sicp.md                           → groups: ["sicp"]
content/meetups/2026-06/2026-06-23-wikipedia-mixite.md               → groups: ["wikimedia"]
content/meetups/2026-06/2026-06-25-body-mesh-models.md               → groups: ["grenoble-data-science"]
content/meetups/2026-06/2026-06-25-python-ia.md                      → groups: ["python-grenoble"]
content/meetups/2026-06/2026-06-25-sicp.md                           → groups: ["sicp"]

# July 2026
content/meetups/2026-07/2026-07-03-papote-numerique-gresille.md      → groups: ["gresille"]
```

- [ ] **Step 2: Identify and assign groups for the 9 events with unknown organizers**

These events have only a shortened redirect URL (lnkd.in) or ambiguous context. Visit each event's link to identify the organizing group, then:
1. If the group already exists in `content/groups/`, add `groups: ["<existing-slug>"]`.
2. If it's a new group, create `content/groups/<new-slug>/_index.md` with the display name, then add `groups: ["<new-slug>"]` to the event.

Unknown events:
```
content/meetups/2026-04/2026-04-02-frugal-ai.md           → lnkd.in/dPbPNKJD (visit to identify)
content/meetups/2026-04/2026-04-07-hommage-carl-sagan.md  → lnkd.in/dsBGCJxv (visit to identify)
content/meetups/2026-04/2026-04-07-ia-generation-code.md  → lnkd.in (visit to identify)
content/meetups/2026-05/2026-05-19-paris-test-conf.md     → lnkd.in (who organized this local debrief?)
content/meetups/2026-05/2026-05-21-claude-code-leak.md    → lnkd.in (visit to identify)
content/meetups/2026-05/2026-05-21-dejeuner-product.md    → lnkd.in (visit to identify)
content/meetups/2026-05/2026-05-21-post-training-llm.md   → lnkd.in (visit to identify)
content/meetups/2026-06/2026-06-23-comprendre-ia.md       → mobilizon.fr (visit to identify)
content/meetups/2026-06/2026-06-30-jeux-qa.md             → linkedin.com/events (visit to identify)
```

- [ ] **Step 3: Verify filter tags appear on the June month page**

```bash
hugo server --buildFuture
```

Visit `http://localhost:1313/meetups/2026-06/`. Group filter tags should appear above the calendar. Click each tag to verify filtering works correctly.

- [ ] **Step 4: Verify group pages have events**

Visit `http://localhost:1313/groups/sicp/` — should list all SICP events.
Visit `http://localhost:1313/groups/` — should list all groups with event counts.

- [ ] **Step 5: Commit**

```bash
git add content/meetups/ content/groups/
git commit -m "feat: assign groups to all existing events"
```

---

## Task 7: Update add-meetup skill to require groups

**Files:**
- Modify: `.claude/skills/add-meetup/SKILL.md`

- [ ] **Step 1: Add groups field to the event file structure section**

In the **File structure** section, replace the event front matter template with:

```yaml
---
title: "<Event title with emoji at end>"
description: ""  # Une phrase décrivant le meetup
date: YYYY-MM-DD
time: "19:00"   # HH:MM preferred; or "midi" / "après-midi" / "soir" — optional, omit if unknown
groups: ["slug"]  # required — organizer group slug(s), e.g. ["humantalks"] or ["securimag", "hackerspace"]
location:       # optional — omit if unknown
  name: "La Casemate"
  address: "1 Place Saint-Laurent, Grenoble"  # optional
  url: "https://maps.app.goo.gl/..."          # optional — map or venue site
links:
  - url: "https://..."   # optional — omit if no URL provided
---
```

- [ ] **Step 2: Add a groups step to the Steps section**

After Step 1 ("Read two existing event files"), insert a new step:

```
1b. **Identify the organizer group(s).** Check `content/groups/` for an existing slug matching the organizer. If no match exists, create `content/groups/<new-slug>/_index.md` with `title: "Organizer Name"` before creating the event file. Every event must have at least one group.
```

- [ ] **Step 3: Verify the skill reads correctly**

```bash
cat .claude/skills/add-meetup/SKILL.md
```

Expected: The file shows `groups:` in the front matter template and the new step 1b.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/add-meetup/SKILL.md
git commit -m "feat: require groups in add-meetup skill"
```

---

## Self-review notes

- All 20 groups created in Task 2 are referenced by at least one event in Task 6's confirmed list.
- 9 events with unknown organizers are explicitly flagged with visit-the-link instructions — not left as silent TBDs.
- The `site.GetPage` lookup in the partial falls back to displaying the raw slug if the group page doesn't exist, preventing build errors.
- The JS guard `item.dataset.groups ? ... : []` prevents errors on event items without a `data-groups` attribute (events missing `groups:` in front matter — possible during Task 6 in-progress state).
- The `where .Pages "Date" ">=" $now` on the group list page uses Hugo's built-in comparison, no custom code needed.
