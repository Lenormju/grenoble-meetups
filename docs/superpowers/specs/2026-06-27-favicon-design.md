# Favicon redesign — grenoble-meetups.fr

**Date:** 2026-06-27  
**Status:** Approved

## Context

The current favicon (`static/favicon.svg`) is a plain blue rounded square with a white "G". It conveys neither the meetup purpose nor the tech identity of the site.

## Design decisions

### Concept: Calendar + `</>`

A calendar icon with the code tag `</>` in the main area. The calendar communicates "events/meetups", the code tag anchors the tech identity. Universally recognisable, unambiguous at small sizes.

### Shape

Rounded square, `rx="18"` on a 100×100 viewBox. Standard app-icon shape, consistent across platforms.

### Colour palette

| Role | Value | Usage |
|---|---|---|
| Gradient start | `#93c5fd` | Top-left of background |
| Gradient end | `#1d4ed8` | Bottom-right of background |
| Calendar body | `#ffffff` | White card inside the square |
| Header bar | `rgba(0,0,0,0.15)` | Semi-transparent dark strip at top of calendar |
| `</>` accent | `#f59e0b` | Amber/gold — code tag in calendar body |

Background: **linear gradient, diagonal ↘ (top-left → bottom-right)**, `#93c5fd` to `#1d4ed8`. Soft, airy, reads well on all browser backgrounds.

### Structure (SVG anatomy)

```
rounded square (gradient bg)
└── calendar card (white rect, rx=7)
    ├── header bar (dark overlay, top of card)
    ├── left hook (white rect, rx=4, above card)
    ├── right hook (white rect, rx=4, above card)
    └── </> text (monospace, bold, amber, centred)
```

### Sizes

SVG scales cleanly — a single `favicon.svg` covers all sizes (16px to 512px). The `site.webmanifest` already references the SVG with `"sizes": "any"`. No PNG raster needed.

## File to modify

- `static/favicon.svg` — replace entirely with the new SVG

## SVG source

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#93c5fd"/>
      <stop offset="100%" style="stop-color:#1d4ed8"/>
    </linearGradient>
  </defs>
  <!-- Background -->
  <rect width="100" height="100" rx="18" fill="url(#bg)"/>
  <!-- Calendar card -->
  <rect x="15" y="22" width="70" height="62" rx="7" fill="white"/>
  <!-- Header bar -->
  <rect x="15" y="22" width="70" height="20" rx="7" fill="rgba(0,0,0,0.15)"/>
  <rect x="15" y="34" width="70" height="8" fill="rgba(0,0,0,0.15)"/>
  <!-- Hooks -->
  <rect x="30" y="14" width="8" height="16" rx="4" fill="white"/>
  <rect x="62" y="14" width="8" height="16" rx="4" fill="white"/>
  <!-- Code tag -->
  <text x="50" y="72" font-size="22" text-anchor="middle"
        fill="#f59e0b" font-family="monospace" font-weight="700">&lt;/&gt;</text>
</svg>
```

## Out of scope

- Changing the site colour scheme beyond the favicon
- Generating PNG fallbacks (SVG favicon has wide enough browser support)
- Changing `site.webmanifest` (already correct)
