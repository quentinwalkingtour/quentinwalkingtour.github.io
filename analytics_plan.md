# CTA Click Tracking Plan — Review & Booking Buttons

> **Status:** implemented on the site (see §4). GTM/GA4-side setup (§7) still to be done by you.

---

## 0. Accounts & IDs (reference)

- **GTM container to edit:** `GTM-5B56HBZC` — account "Quentin Walking Tour" (6271229721). This is the only container actually installed on the site (verified across every page).
- **GA4 property (destination):** "Website activity" — property ID `480383664`, under GA4 account "Quentin Walking Tour - Analytics" (347673370).
- **Existing tags inside `GTM-5B56HBZC`** (confirmed from the GTM UI, 2026-07-07):

  | Tag | Type | Trigger |
  |---|---|---|
  | Google Ads - Conversion Linker | Conversion Linker | Initialization - All Pages |
  | Google Ads Conversion - Open Croix-Rousse Page | Google Ads Conversion Tracking | Open Croix-Rousse Booking Page |
  | Google Ads Conversion - Open Vieux-Lyon Page | Google Ads Conversion Tracking | Open Vieux-Lyon Booking Page |
  | Google Ads Conversion - Purchase | Google Ads Conversion Tracking | Purchase on Website Bokun |
  | **Google Analytics - GA4 Linker** | **Google Tag** | Initialization - All Pages |
  | Google Tag AW-16699236593 | Google Tag | Initialization - All Pages |
  | Page Viewed - GA4 Event | Google Analytics: GA4 Event | All Pages |

  - `Google Analytics - GA4 Linker` (type **Google Tag**) is the base GA4 configuration in modern GTM — it replaces the old standalone "GA4 Configuration" tag type. **Reuse this as the Configuration Tag for the new `cta_click` event tag** (see §7 Step 0) rather than creating a new one — confirm by opening `Page Viewed - GA4 Event` and checking it references the same tag.
  - **Correction to an earlier claim in this doc:** `AW-16699236593` (Google Ads) IS live on every page — it's wired in as the `Google Tag AW-16699236593` tag above, firing on `Initialization - All Pages`. It just isn't visible from the site's HTML source (GTM-defined tags don't show up in a source grep), which is what my earlier check was based on.
  - The three `Google Ads Conversion Tracking` tags (`Croix-Rousse`, `Vieux-Lyon`, `Bokun Purchase`) are almost certainly leftover from the old Lyon tour business (matches the commented-out "After 3 years guiding in Lyon" banner in `index.html`). Likely dead weight, but left untouched — flagged for optional future cleanup, not part of this plan.

---

## 1. What we're trying to answer

- Which review platform (TripAdvisor / GuruWalk / FreeTour / Google / GetYourGuide) gets clicked the most on `recommendation.html`?
- Does that differ by **guide** (Quentin / Christina / Thomas)?
- What's the click-through rate of the **"Book tour"** CTA on the main page (`index.html`)?
- Same guide breakdown for booking clicks.

## 2. Current state (what already exists)

- GTM container `GTM-5B56HBZC` is installed on every page already — no new install needed.
- `/go/*.html` redirect pages already push a `dataLayer` event on load (`affiliate_redirect`, with `redirect_slug` + `platform`). This is the only tracking that currently reaches GTM.
- `recommendation.html` review buttons only `console.log` on click today — nothing is sent anywhere.
- `index.html`'s "Reserve Your Spot!" button just opens a modal (`toggleModal()`); the modal's actual booking link (GuruWalk) isn't tracked either.
- The `guide` URL parameter (`?guide=quentin|christina|thomas`) already exists on `recommendation.html` and drives the avatar photo. It is not currently present anywhere on `index.html`.
- `tour_source` (`?src=flyer|qrcode`) is captured in `sessionStorage` on `recommendation.html`.

## 3. Design principle: one generic event, not one event per button

Instead of a different GTM tag/trigger per platform or per page (which gets messy fast as you add guides/platforms/pages), every trackable click pushes the **same** event shape to `dataLayer`:

```js
dataLayer.push({
  event:        'cta_click',
  cta_category: 'review',           // 'review' | 'booking' | 'affiliate'
  cta_platform: 'guruwalk',         // 'tripadvisor' | 'guruwalk' | 'freetour' | 'google' | 'getyourguide' | 'whatsapp' | 'email'
  cta_label:    'Review on GuruWalk', // human-readable button text, for sanity-checking reports
  guide:        'quentin',          // 'quentin' | 'christina' | 'thomas' | 'unknown'
  tour_type:    'freetour',         // 'freetour' | 'prepaid' | 'hybrid' | 'n/a'  (recommendation.html only)
  source:       'qrcode',           // from sessionStorage tour_source, 'direct' if absent
});
```

**Why this scales:** adding a 4th guide or a 6th review platform later never requires touching GTM or GA4 — it's just a different string value in an existing field. One GA4 custom-event tag and 5 custom dimensions cover the entire site, forever.

`cta_category` values map to what you're asking about:
- `review` → the 3(+2) review buttons on `recommendation.html`
- `booking` → "Reserve Your Spot" on `index.html` + the GuruWalk link inside the modal + the `book-a-tour.html` link
- `affiliate` → the existing `/go/*` redirects (kept as-is, optionally folded into this same shape later — out of scope for now)

## 4. Buttons to instrument

| Page | Button | `cta_category` | `cta_platform` | `guide` source |
|---|---|---|---|---|
| `recommendation.html` | Review on GuruWalk | review | guruwalk | `?guide=` param |
| `recommendation.html` | Review on TripAdvisor (viator link) | review | tripadvisor | `?guide=` param |
| `recommendation.html` | Leave a Google Review | review | google | `?guide=` param |
| `recommendation.html` | Review on GetYourGuide (prepaid type only) | review | getyourguide | `?guide=` param |
| `recommendation.html` | Footer "Google review takes 2 minutes" link | review | google | `?guide=` param |
| `index.html` | "🎟️ Reserve Your Spot!" (opens modal) | booking | modal_open | n/a — no guide param on this page yet (see §5) |
| `index.html` | GuruWalk link inside the booking modal | booking | guruwalk | see §5 |
| `book/book-a-tour.html` | GuruWalk link | booking | guruwalk | see §5 |

Every `<a>`/button gets one extra inline attribute calling a single shared helper, e.g.:
```html
<a ... onclick="trackCta({category:'review', platform:'guruwalk', label:'Review on GuruWalk'})">
```
The helper (one small `<script>` block, same pattern already used for `copyChip()`) reads `guide`/`tour_type`/`source` from the page context automatically, so each button only declares what's unique to it.

## 5. Open question: propagating `guide` to the booking page

Right now `?guide=` only exists on `recommendation.html`. If you want "Book tour" CTR broken down by guide, the flyers/QR codes that point to `index.html` need `?guide=quentin` (etc.) added too, the same way they already do for `recommendation.html`. Two options:

- **A. Add `?guide=` to your `index.html` flyer/QR links** — same mechanism as today, minimal work, keeps everything URL-param driven.
- **B. Skip guide-level breakdown on the booking CTA for now** — only track it on the review page, where the parameter already exists.

*(Flagged for your decision — doesn't block the rest of the plan.)*

## 6. What does NOT change

- No new tracking library, no new script tag — everything rides the existing GTM container.
- `/go/*` redirect tracking is untouched.
- No visual/UX changes to any button.

---

## 7. GA4/GTM setup — full step-by-step walkthrough

Everything below happens in the GTM/GA4 web UI, in container **`GTM-5B56HBZC`** (see §0). Uses the exact event/parameter names already implemented in the code.

### Step 0 — Confirm the GA4 base tag (already done — reuse it)

Already resolved: `Google Analytics - GA4 Linker` (type **Google Tag**) is the existing GA4 base configuration in this container — no need to create a new one. Quick sanity check before moving on:

1. Open **`Page Viewed - GA4 Event`** (the tag that already tracks page views successfully) → check whatever field it uses to reference the base tag → it should point to `Google Analytics - GA4 Linker`.
2. Open **`Google Analytics - GA4 Linker`** itself → confirm its Tag ID is a `G-XXXXXXX` value matching the "Website activity" property (480383664) in GA4 Admin → Data Streams.
3. Reuse the same reference for the new `cta_click` tag in Step 3 below.

### Step 1 — Create the trigger

1. Left sidebar → **Triggers** → **New**.
2. Name it: `CE - cta_click`
3. Trigger type: **Custom Event**
4. Event name: `cta_click` (exact match, case-sensitive)
5. "This trigger fires on": **All Custom Events**
6. Save.

### Step 2 — Create 6 Data Layer Variables

Left sidebar → **Variables** → **User-Defined Variables** → **New**, repeat 6 times:

| Variable name | Data Layer Variable Name |
|---|---|
| `DLV - cta_category` | `cta_category` |
| `DLV - cta_platform` | `cta_platform` |
| `DLV - cta_label` | `cta_label` |
| `DLV - guide` | `guide` |
| `DLV - tour_type` | `tour_type` |
| `DLV - source` | `source` |

For each: Variable type = **Data Layer Variable**, Data Layer Variable Name = the exact key from the table (must match the `dataLayer.push({...})` keys in the code exactly), Version = **Version 2**.

### Step 3 — Create the event tag (confirmed against actual GTM screen, 2026-07-07)

1. **Tags** → **New**.
2. Name: `GA4 Event - cta_click`
3. Tag Type: **Google Analytics: GA4 Event**
4. **Measurement ID**: `{{constant - G4A measurement ID G-2C0B678Y8N}}` — reuse the existing Constant variable that already holds `G-2C0B678Y8N` (same one other GA4 Event tags in this container use). GTM shows a banner *"Google tag found in this container — this tag will use the configuration of Google tag quentinwalkingtour"* — that's expected; it means this event automatically inherits the base tag's settings, no separate config/linker step needed.
5. **Event Name**: `cta_click`
6. **Event Parameters** — click "Add Row" 6 times:

| Parameter Name | Value |
|---|---|
| `cta_category` | `{{DLV - cta_category}}` |
| `cta_platform` | `{{DLV - cta_platform}}` |
| `cta_label` | `{{DLV - cta_label}}` |
| `guide` | `{{DLV - guide}}` |
| `tour_type` | `{{DLV - tour_type}}` |
| `source` | `{{DLV - source}}` |

7. Triggering: click **+**, select `CE - cta_click` (from Step 1).
8. Save.

### Step 4 — Preview & test

1. Top-right of GTM → **Preview**.
2. Enter your site URL, e.g. `https://quentinwalkingtour.com/recommendation.html?type=freetour&guide=christina`.
3. This opens Tag Assistant in a connected tab. Click one of the review buttons on the live page.
4. In Tag Assistant, find the `cta_click` event in the left timeline → click it → check the **Tags** tab confirms `GA4 Event - cta_click` fired, and the parameters show correct values (`cta_platform=guruwalk`, `guide=christina`, etc.).
5. Repeat for `index.html`'s "Reserve Your Spot" button and the GuruWalk modal link, and for `book/book-a-tour.html`.
6. If a value shows as `undefined`, double-check the Data Layer Variable Name in Step 2 matches the dataLayer key exactly (case-sensitive, no typos).

### Step 5 — Publish

1. Close Preview mode.
2. Top-right → **Submit**.
3. Version name: e.g. `Add cta_click event tracking`. Version description: brief note referencing this plan.
4. **Publish**.

### Step 6 — Register custom dimensions in GA4

GA4 won't show these parameters in reports until registered:

1. GA4 → **Admin** → **Custom definitions** → **Custom dimensions** → **Create custom dimension**.
2. Repeat 6 times, one per parameter:
   - Dimension name: e.g. `CTA Category`
   - Scope: **Event**
   - Event parameter: `cta_category` (must match exactly)
   - Repeat for `cta_platform`, `cta_label`, `guide`, `tour_type`, `source`.

New custom dimensions can take a few hours to start populating standard reports/Explorations after events start flowing — don't panic if it's empty right after registering.

### Step 7 (optional) — Mark as a key event

GA4 → **Admin** → **Events** → find `cta_click` in the list (appears after it's fired at least once) → toggle **Mark as key event**. Only do this if you want raw clicks counted as conversions — you may prefer separate key events split by `cta_category` instead, built via Explore.

### Step 8 — Build the Explore reports

1. **"Review CTA performance"** — Free form exploration. Rows: `cta_platform`. Breakdown/Columns: `guide`. Values: Event count + Total users. Filter: `event name = cta_click` AND `cta_category = review`.
2. **"Booking CTA performance"** — same shape, filter `cta_category = booking`.
3. **For true CTR (clicks ÷ views):** add `page_view` count for `recommendation.html` / `index.html` (segmented by `guide` if you go with option A in §5) as a second metric in the same exploration, so you get clicks-per-visit directly instead of raw counts.

---

## Status

- ✅ §4 (code instrumentation) — implemented and verified with an automated click-through test (Playwright) confirming `cta_click` fires with correct `cta_category`/`cta_platform`/`guide`/`tour_type`/`source` on every button in the table above.
- ⬜ §7 (GTM/GA4 configuration) — manual dashboard work, still to be done by you. Steps 0–5 are GTM; Step 6 is GA4; Steps 7–8 are optional/reporting.
- ⬜ §5 (propagating `guide` to `index.html`/booking flyers) — open decision, not yet made.
