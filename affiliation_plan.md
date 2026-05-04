# Affiliation & Rebuild Plan — `recommendation.html`

> **Status:** awaiting approval — no code will be written until confirmed.

---

## Observations on the current state

- `recommendation.html` is the live production file. `recommendation-new.html` is an exploratory draft with a different review-card design. After this rebuild, `recommendation-new.html` can be deleted.
- All data (activities, recommendations) is currently hardcoded inside `<script>` tags in the HTML.
- There is no `data/` folder, no JSON files, no `blog/` folder, and no `img/guides/` folder yet.
- A blog pipeline exists (`template-blog.html`, `generate_blog.py`, `blog-posts.yaml`, `.github/workflows/generate-blog.yml`) but has no content and `blog-posts.yaml` is empty. The template uses `{{handlebars}}`-style placeholders and references `index.css`.
- The review section currently shows static buttons (GuruWalk + Google + TripAdvisor) regardless of URL parameters.
- The `assets/images/icons/` folder presumably holds `guruwalk.png`, `google.png`, `tripadvisor.png` — icon assets for the new platforms (GetYourGuide, Viator) will need to be added there too.

---

## Files to CREATE

### 1. `data/activities.json`
Replaces the hardcoded `ACTIVITIES` array in `recommendation.html`.

Schema per item:
```jsonc
{
  "emoji": "⚰️",             // display emoji (used instead of image for simplicity)
  "title": "Père Lachaise",
  "description": "Love, scandal, and legends among the graves",
  "affiliateUrl": "https://...",
  "badge": "Free tour",       // optional label shown on the card, e.g. "Partner", "Recommended"
  "active": true              // set to false to hide without deleting
}
```
Seeded with the 2 existing activities from `recommendation.html`.

---

### 2. `data/places.json`
Powers the new **Places** section (3 dropdowns: Restaurants, Bars, Cafés).

Top-level structure:
```jsonc
{
  "maps": {
    "restaurants": "PLACEHOLDER_RESTAURANTS_GOOGLE_MY_MAPS_URL",
    "bars":        "PLACEHOLDER_BARS_GOOGLE_MY_MAPS_URL",
    "cafes":       "PLACEHOLDER_CAFES_GOOGLE_MY_MAPS_URL"
  },
  "places": [
    {
      "category":     "restaurants",   // "restaurants" | "bars" | "cafes"
      "name":         "Bouillon Chartier",
      "neighborhood": "Grands Boulevards",
      "description":  "Iconic 1896 brasserie, very affordable, always packed.",
      "googleMapsUrl": "https://maps.google.com/?q=...",
      "active": true
    }
  ]
}
```
`maps` holds one Google My Maps iframe URL per category (the map shown when the dropdown is opened). These are left as named string placeholders to fill in later. The `places` array is filtered by `category` and `active: true` when rendering the list view.

---

### 3. `data/tips.json`
Powers the new **Tips** section (4 dropdowns: Museums, Tours, Day Trips, Transfers & Métro).

Schema per item:
```jsonc
{
  "category":    "museums",    // "museums" | "tours" | "day-trips" | "transfers"
  "icon":        "🏛️",
  "title":       "Book the Louvre in advance",
  "description": "Skip the 2-hour queue by reserving a timed entry online.",
  "ctaLabel":    "Book tickets",
  "ctaUrl":      "https://www.louvre.fr/en/visit",
  // ctaUrl can be:
  //   - a direct ticketing URL
  //   - a /go/ redirect slug  (e.g. "/go/louvre")
  //   - a future blog article (e.g. "/blog/best-paris-museums.html")
  "active": true
}
```

---

### 4. `blog/index.html`
A new, standalone blog index page. Its purposes are:
- SEO landing page for organic search traffic ("Paris tips", "Paris walking tour guide", etc.)
- Links to individual article pages
- Sells the tour to potential readers who find it via search

Structure:
- `<head>`: full SEO meta tags, Open Graph, canonical URL `https://quentinwalkingtour.com/blog/`
- Inlined CSS matching the site design (same CSS variables as `recommendation.html`)
- Header: site logo + nav link back to homepage
- Hero: short editorial intro from Quentin (2–3 sentences, first-person)
- Article grid: card for each article (cover image, title, excerpt, date, category tag, "Read →" link)
- Footer: link to homepage + link to GuruWalk booking
- The article list is **generated** by `generate_blog.py` reading the `blog/posts/` folder (see Blog pipeline section below).

Note: `blog/index.html` will initially render an empty-state message ("First articles coming soon!") and fill in automatically as Markdown files are added to `blog/posts/`.

---

### 5. `img/guides/` directory placeholder
Three guide photos will live at:
- `/img/guides/quentin.jpg`
- `/img/guides/christina.jpg`
- `/img/guides/thomas.jpg`

These images do not exist yet. The JS logic will reference these paths and fall back silently to the default logo if the image fails to load (`onerror` handler). The directory itself should be created (with a `.gitkeep`) so the path is ready.

---

## Files to MODIFY

### 6. `recommendation.html` ← main work

All changes are confined to this one file (inline CSS + inline JS). No new external CSS or JS files are created. The section order in the page stays the same; the two new sections (Places, Tips) are inserted between the existing Recommendations accordion card and the footer.

#### 6-A — Data loading architecture
Replace all hardcoded JS arrays with a `Promise.all()` fetch at `DOMContentLoaded`. Pseudocode:

```
Promise.all([
  fetch('./data/activities.json').then(r => r.json()),
  fetch('./data/places.json').then(r => r.json()),
  fetch('./data/tips.json').then(r => r.json()),
])
.then(([activities, placesData, tips]) => {
  renderActivities(activities);
  renderPlaces(placesData);
  renderTips(tips);
  renderCategories();   // existing accordion, still hardcoded data for now
})
.catch(err => { /* hide affected section gracefully */ });
```

Each section has:
- A skeleton/loading state (simple animated placeholder) shown while fetching
- Graceful hide (not crash) if its specific fetch fails
- The existing `CATEGORIES` accordion data stays hardcoded in JS for now (it is not part of this plan's scope)

#### 6-B — Header: guide photo logic
Read the `guide` URL parameter on page load. Swap `src` of `.rec-avatar` accordingly:

| `?guide=` value | Photo source |
|---|---|
| `quentin` | `/img/guides/quentin.jpg` |
| `christina` | `/img/guides/christina.jpg` |
| `thomas` | `/img/guides/thomas.jpg` |
| *(anything else / absent)* | `./assets/images/Logo_Noir_wb.png` (current default) |

The `alt` text is also updated to match the guide name. An `onerror` fallback on the `<img>` element resets to the logo if the guide photo file is not yet uploaded.

No CSS changes to the header.

#### 6-C — Review section: type-driven button logic
Read the `type` URL parameter and render the review buttons dynamically (JS, not hardcoded HTML):

**`?type=free_tour`** (or parameter absent — safe default):
1. Primary button → **GuruWalk** (existing style: white bg, red border)
   - URL placeholder: `GURUWALK_REVIEW_URL`
2. Secondary link → **Google** (existing style: blue)
   - URL: `https://g.page/r/CbXKLOzFaHEXEAE/review` (already in use)

**`?type=prepaid`**:
1. Primary button → **GetYourGuide** (yellow/black brand style)
   - URL placeholder: `GETYOURGUIDE_REVIEW_URL`
2. Secondary button → **Viator** (green brand style)
   - URL placeholder: `VIATOR_REVIEW_URL`
3. Small tertiary text link → **Google**
   - URL: `https://g.page/r/CbXKLOzFaHEXEAE/review`

All platform icons live in `./assets/images/icons/`. Icons for GetYourGuide and Viator need to be added to that folder (noted as a prerequisite but not part of this coding plan).

No CSS changes to the review card; the existing `.review-btn--google`, `.review-btn--secondary` and `.review-btn--guruwalk` classes are reused. One new class `.review-btn--getyourguide` and `.review-btn--viator` will be added inline.

#### 6-D — Activities section: JSON-driven rendering
Remove the hardcoded `ACTIVITIES` array. The `renderActivities()` function now accepts the parsed JSON array. The rendered HTML stays **pixel-identical** to what it produces today. The `badge` field, if present, renders as a small pill overlaid on the card (reusing the commented-out `.activity-partner` CSS that already exists in the file). The `active: false` items are filtered out silently.

Each activity card can optionally link to a blog article via a `blogUrl` field (optional, future use):
- If `blogUrl` is present, a small "Read more" text link appears below the description.

#### 6-E — Places section (new, fully built)
New section inserted after the existing Recommendations card.

HTML skeleton (rendered once, statically):
```html
<div class="card" id="section-places">
  <!-- loading state shown here until data arrives -->
  <p class="card-title">🍽️ Places I Recommend</p>
  <p class="card-subtitle">Restaurants, bars & cafés I've been to</p>
  <div class="accordion" id="places-accordion">
    <!-- 3 dropdowns injected by JS: Restaurants, Bars, Cafés -->
  </div>
</div>
```

Each dropdown (one per category) contains:
- **Closed state**: accordion trigger button (same `.acc-trigger` style as existing Recommendations)
- **Open state**: a toggle bar ("Map view / List view") + either:
  - **Map view** (default): Google My Maps `<iframe>` (URL from `places.json → maps[category]`)
  - **List view**: list of `<div class="place-item">` cards, each showing:
    - Name (bold) + neighborhood badge
    - Short description
    - "Open in Maps →" link (`googleMapsUrl`)
    - Optional: `blogUrl` field → small "Read our guide →" link pointing to a blog article

CSS additions (inline in `<style>` block):
- `.place-item` — card with name, neighborhood chip, description, link
- `.place-neighborhood` — small pill badge
- `.view-toggle` — two-button toggle bar (Map / List), switches `hidden` attribute on the two views

#### 6-F — Tips section (new, fully built)
New section inserted after the Places section.

HTML skeleton:
```html
<div class="card" id="section-tips">
  <p class="card-title">💡 My Paris Tips</p>
  <p class="card-subtitle">Shortcuts, bookings & insider tricks</p>
  <div class="accordion" id="tips-accordion">
    <!-- 4 dropdowns injected by JS -->
  </div>
</div>
```

Each dropdown (Museums / Tours / Day Trips / Transfers & Métro):
- Trigger button with emoji + category name
- Body: list of `.tip-card` components, each showing:
  - Icon (emoji)
  - Title (bold)
  - Description (short, 1–2 sentences)
  - CTA button → `ctaUrl` (opens in new tab if external; same tab if internal blog link)
  - Optional: if `ctaUrl` starts with `/blog/`, a small "article" chip is shown next to the CTA to signal it's an internal read rather than a booking link

CSS additions (inline):
- `.tip-card` — flex row: icon | text block | CTA button
- `.tip-cta` — small pill button, inherits the existing `.activity-cta` style
- `.tip-blog-chip` — tiny "📖 article" label for internal links

---

## Blog structure — design decisions

### Goal
The blog serves three functions simultaneously:
1. **SEO / organic traffic** — articles targeting Paris travel keywords bring new visitors who may book the tour
2. **Tour sales** — each article ends with a "Join the tour" CTA block (already in `template-blog.html`)
3. **Affiliate context** — articles are the natural home for affiliate links (e.g., "Best Paris museum passes", "How to get from CDG to Paris"), giving `/go/` redirects editorial cover

### Why the current pipeline needs to change before 50 articles

The existing setup stores full article content inside `blog-posts.yaml`. At scale this causes three problems:

1. **One giant YAML file** — with 50 articles it will be 3,000–5,000+ lines. YAML multiline strings are strict about indentation and escaping. One syntax error anywhere breaks generation of every article. Standard Markdown editors (VSCode preview, Typora, Obsidian, AI-generated content) can't help because the content isn't in `.md` files.
2. **Fragile index injection** — `update_index_with_posts()` uses a regex to rewrite `const blogPosts = [...]` inside `index.html`. Every publish triggers a GitHub Actions commit to `index.html`. Over 50 articles this pollutes git history, and the regex silently fails if the JS block is reformatted.
3. **No draft state** — there is no `draft: true` flag. Pushing a half-written article publishes it immediately.

### New architecture: one Markdown file per article

```
blog/
  posts/
    best-paris-museums.md       ← you write here, plain Markdown + frontmatter
    paris-metro-guide.md
    versailles-day-trip.md
    ...                         ← 50 files, one per article
  best-paris-museums.html       ← generated, never touch manually
  paris-metro-guide.html
  index.html                    ← generated blog index (replaces YAML-based injection)
template-blog.html              ← article HTML template (stays)
generate_blog.py                ← updated to read posts/*.md instead of blog-posts.yaml
blog-posts.yaml                 ← kept for reference, no longer used by the generator
```

Each article file is a standard `.md` file with YAML frontmatter at the top:

```markdown
---
title: "Best Paris Museums: A Local Guide"
slug: best-paris-museums
date: 2026-05-15
description: "Which museums are worth it — from a guide who's been to all of them."
keywords: "Paris museums, Louvre tips, Orsay museum guide"
category: Museums
image: assets/images/blog/museums-cover.jpg
draft: false
---

Your article in plain Markdown here.

No YAML escaping, no indentation rules, no risk of breaking other articles.
Paste AI-generated content directly, edit in VSCode preview, Typora, or Obsidian.
```

Setting `draft: true` hides an article from generation without deleting the file.

### Changes required to support this

**`generate_blog.py`** — rewrite the data-loading section only (~20 lines):
- Replace `yaml.safe_load(config_file)` with a glob over `blog/posts/*.md`
- Use the `python-frontmatter` library to parse each file's frontmatter + body
- Skip files where `draft: true`
- Generate `blog/index.html` directly (write a proper index template) instead of patching `index.html` with a regex
- Remove `update_index_with_posts()` entirely; `index.html` no longer holds the post list

**`.github/workflows/generate-blog.yml`** — two changes:
- Add `blog/posts/**` to the `paths` trigger
- Remove `index.html` from `git add` (the bot no longer touches it)

**`template-blog.html`** — make it self-contained:
- Add its own `<style>` block (article typography, affiliate CTA boxes, breadcrumb)
- Currently it references `index.css` which couples blog layout to the main site stylesheet

### What stays the same
- GitHub Actions deploys on push — no change in workflow
- HTML template approach — no change in concept
- `blog/{slug}.html` output paths — no change in URL structure

### Linking back from `recommendation.html`
- **Activity cards** (`data/activities.json`): optional `blogUrl` field → if present, a "Read our review →" micro-link appears on the card
- **Tip cards** (`data/tips.json`): `ctaUrl` can point directly to `/blog/{slug}.html`
- **Place items** (`data/places.json`): optional `blogUrl` field per place

### `/go/` redirect system

All affiliate and booking links are wrapped in `/go/{slug}` redirects. This means:
- You change a destination URL in one place (`go/redirects.json`) without touching any JSON data file or HTML page
- You can track clicks per slug in GTM/GA4 by watching hits to `/go/*`
- Links in blog articles, tip cards, and activity cards all use clean internal URLs

**Architecture:**

```
go/
  redirects.json          ← single editable source of truth
  versailles.html         ← generated, never edit manually
  louvre.html
  louvre-official.html
  ...
generate_redirects.py     ← reads redirects.json → writes go/{slug}.html
```

**`go/redirects.json` schema:**
```jsonc
[
  {
    "slug":        "versailles",
    "title":       "Palace of Versailles — Tickets with Guide",
    "platform":    "getyourguide",
    "description": "Official Versailles tickets with a guide, sold on GetYourGuide",
    "url":         "https://www.getyourguide.fr/paris-l16/billet-passeport-...",
    "active":      true
  }
]
```

Each generated `go/{slug}.html` is a minimal page with:
1. `<meta http-equiv="refresh" content="0;url={url}">` — instant redirect
2. JS fallback: `window.location.replace(url)` in case meta-refresh is blocked
3. A `<noscript>` "Click here" link for robustness
4. GTM dataLayer push so redirect clicks are tracked as events

**Initial slugs from your existing links:**

| Slug | Platform | Destination |
|---|---|---|
| `/go/versailles` | GetYourGuide | Versailles tickets with guide |
| `/go/louvre` | GetYourGuide | Louvre skip-the-line with audioguide |
| `/go/louvre-official` | Official | ticket.louvre.fr |
| `/go/seine` | GetYourGuide | Bateaux Mouches cruise |
| `/go/seine-amphibie` | GetYourGuide | Amphibious bus + river cruise |
| `/go/orsay` | GetYourGuide | Orsay with digital audioguide |
| `/go/orsay-official` | Official | billetterie.musee-orsay.fr |
| `/go/bus` | GetYourGuide | Hop-on hop-off bus + optional cruise |
| `/go/eiffel` | Official | ticket.toureiffel.paris |
| `/go/eiffel-dinner` | GetYourGuide | Lunch at Brasserie Madame, Eiffel Tower |

> ⚠️ **Important — affiliate tracking issue in your current links:**
> Several of your GetYourGuide links use a `visitor-id=...` query parameter instead of `partner_id=QBAL53E`. The `visitor-id` is a session tracking cookie, not your affiliate ID. Those clicks will not be attributed to you and you will not earn commission on them.
>
> Affected links: Seine (both), Orsay GYG, Bus, Eiffel GYG. Check your GYG affiliate dashboard for the correct deep-link format — it should always include `partner_id=QBAL53E`. The Versailles link is correct (`partner_id=QBAL53E&utm_medium=local_partners`).
>
> Before going live, replace the `visitor-id` links with properly constructed affiliate URLs from the GYG Partner Program dashboard (Partners > Tools > Deep Links).

---

## Execution order

### Phase 1 — Data files (independent, can be done together)
| # | Action | File(s) touched |
|---|---|---|
| 1 | Create `data/activities.json` with existing 2 activities + expanded schema | **CREATE** `data/activities.json` |
| 2 | Create `data/places.json` with placeholder map URLs and a few sample places per category | **CREATE** `data/places.json` |
| 3 | Create `data/tips.json` with placeholder entries across all 4 categories | **CREATE** `data/tips.json` |

### Phase 2 — Blog pipeline rebuild
| # | Action | File(s) touched |
|---|---|---|
| 4 | Create `blog/posts/` directory with a `.gitkeep` | **CREATE** `blog/posts/.gitkeep` |
| 5 | Add `python-frontmatter` to requirements; rewrite `generate_blog.py` to read `blog/posts/*.md`, skip drafts, generate `blog/index.html` directly, remove `update_index_with_posts()` | **MODIFY** `generate_blog.py` |
| 6 | Update workflow: add `blog/posts/**` to `paths` trigger, remove `index.html` from `git add` | **MODIFY** `.github/workflows/generate-blog.yml` |
| 7 | Rewrite `template-blog.html` to be self-contained (own `<style>` block, article typography, affiliate CTA box, breadcrumb, "Join the tour" footer CTA) — no `index.css` dependency | **MODIFY** `template-blog.html` |
| 8 | Create `blog/index.html` as the generated blog index template (SEO meta, article grid, empty-state, "Join the tour" link) | **CREATE** `blog/index.html` |

### Phase 3 — `recommendation.html` rebuild
| # | Action | File(s) touched |
|---|---|---|
| 9 | Add CSS for Places section (`.place-item`, `.view-toggle`, `.place-neighborhood`) | **MODIFY** `recommendation.html` — `<style>` block |
| 10 | Add CSS for Tips section (`.tip-card`, `.tip-cta`, `.tip-blog-chip`) | **MODIFY** `recommendation.html` — `<style>` block |
| 11 | Add HTML shells for Places and Tips sections (static markup, no JS yet) | **MODIFY** `recommendation.html` — `<body>` |
| 12 | Wire `Promise.all()` fetch + loading states + error handling | **MODIFY** `recommendation.html` — `<script>` |
| 13 | Implement header guide photo logic (`guide` param) | **MODIFY** `recommendation.html` — `<script>` |
| 14 | Implement review section type-driven logic (`type` param) | **MODIFY** `recommendation.html` — `<script>` |
| 15 | Implement `renderActivities()` from JSON (replace hardcoded array) | **MODIFY** `recommendation.html` — `<script>` |
| 16 | Implement `renderPlaces()` from JSON (map/list toggle, accordion) | **MODIFY** `recommendation.html` — `<script>` |
| 17 | Implement `renderTips()` from JSON (tip cards, CTA routing) | **MODIFY** `recommendation.html` — `<script>` |

### Phase 4 — Redirect system
| # | Action | File(s) touched |
|---|---|---|
| 18 | Create `go/redirects.json` with the 10 initial slugs (using correct affiliate URLs — fix `visitor-id` links first) | **CREATE** `go/redirects.json` |
| 19 | Write `generate_redirects.py` — reads `go/redirects.json`, writes `go/{slug}.html` per active entry | **CREATE** `generate_redirects.py` |
| 20 | Add redirect generation to GitHub Actions workflow (`paths` trigger on `go/redirects.json`, run `generate_redirects.py`, `git add go/`) | **MODIFY** `.github/workflows/generate-blog.yml` |
| 21 | Run the generator locally once to produce the initial `go/*.html` files and commit them | **CREATE** `go/*.html` (10 files) |

### Phase 5 — Cleanup
| # | Action | File(s) touched |
|---|---|---|
| 22 | Create `img/guides/.gitkeep` so the directory exists for future photo uploads | **CREATE** `img/guides/.gitkeep` |
| 23 | Delete `recommendation-new.html` (superseded) | **DELETE** `recommendation-new.html` |

Phases 1 and 2 are fully independent of each other and of Phase 3. Phase 4 (redirects) is independent of all other phases and can be done at any point. Within Phase 3, steps 9–11 (CSS + HTML shells) must precede steps 12–17 (JS logic).

---

## Starter blog articles

Three articles to write as part of this plan — enough to validate the pipeline end-to-end and start capturing SEO traffic. No placeholder content: these are real, publishable posts.

---

### Article 1 — `blog/posts/paris-museums-sold-out.md`

**Target keywords:** "paris museum tickets sold out", "louvre no availability", "orsay tickets unavailable"

**Angle:** Quentin explains in first person why this keeps happening (demand surge, time-slot system, resellers absorbing inventory) and what to actually do about it.

**Outline:**
1. Why it happens — the timed-entry system, high demand, and the reseller market
2. Option A — keep checking the official site (works, but requires patience; include `/go/louvre-official` and `/go/orsay-official`)
3. Option B — book through a tour operator who holds allocations (honest framing: slightly more expensive, includes audioguide or guide; include `/go/louvre` and `/go/orsay`)
4. Quentin's recommendation — try official first, use option B as a backup, never pay scalpers
5. "Join my free walking tour" CTA block (already in template)

**Affiliate links used:** `/go/louvre`, `/go/louvre-official`, `/go/orsay`, `/go/orsay-official`

---

### Article 2 — `blog/posts/versailles-day-trip-from-paris.md`

**Target keywords:** "versailles day trip from paris", "how to visit versailles", "versailles tickets guide"

**Angle:** Practical guide — how to get there, how long to spend, what to see, and why booking a guided ticket makes the visit make sense (the palace is enormous and confusing without context).

**Outline:**
1. Getting there (RER C, ~40 min from central Paris)
2. How much time you need (half day minimum, full day ideal)
3. What to prioritise inside (Hall of Mirrors, King's Apartments, gardens)
4. Tickets — official site vs. guided option with `/go/versailles`
5. Tips from Quentin (best time to go, what to bring)
6. "Join my free Paris walking tour" CTA block

**Affiliate links used:** `/go/versailles`

---

### Article 3 — `blog/posts/paris-seine-river-cruise.md`

**Target keywords:** "paris seine river cruise", "bateaux mouches paris", "best seine cruise paris"

**Angle:** Is a Seine cruise worth it? Quentin's honest take — yes for first-timers and families, not essential for repeat visitors — plus which option to book.

**Outline:**
1. What you actually see from the river (the case for doing it)
2. Classic cruise: Bateaux Mouches (`/go/seine`) — duration, price, what to expect
3. Quirky alternative: the amphibious bus (`/go/seine-amphibie`) — for kids, something different
4. When to go (golden hour is best, night cruises are touristy but fun)
5. "Join my free walking tour first, then take the cruise" CTA

**Affiliate links used:** `/go/seine`, `/go/seine-amphibie`

---

These three articles cover 7 of the 10 redirect slugs already planned, give the blog pipeline a real end-to-end test, and target keywords with clear commercial intent that align with the affiliate links you already have.

### Phase 6 — Write starter blog posts
| # | Action | File(s) touched |
|---|---|---|
| 24 | Write Article 1: `paris-museums-sold-out.md` with frontmatter + full Markdown content | **CREATE** `blog/posts/paris-museums-sold-out.md` |
| 25 | Write Article 2: `versailles-day-trip-from-paris.md` | **CREATE** `blog/posts/versailles-day-trip-from-paris.md` |
| 26 | Write Article 3: `paris-seine-river-cruise.md` | **CREATE** `blog/posts/paris-seine-river-cruise.md` |

These steps depend on Phase 2 (blog pipeline) being complete first so the generator can process them.

---

## Out of scope for this plan
- Uploading guide photos (`/img/guides/*.jpg`)
- ~~Adding GetYourGuide and Viator icon assets to `assets/images/icons/`~~ — already present (`getyourguide.png`, `viator.png`)
- Any changes to `index.html` or `index.css`
- Fixing the `visitor-id` → `partner_id` issue in your GYG links (must be done in the GYG dashboard before going live)

---

*Waiting for your approval before any code is written.*
