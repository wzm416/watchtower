# V1 — Merchandise price monitoring (product design)

> **Plan-design-review** artifact: design decisions for what users **see** and **feel** before implementation.  
> **Stack:** TypeScript + Next.js on GCP (execution plan → `/plan-eng-review`).  
> **Codename:** Watchtower until renamed (see [00-decisions.md](./00-decisions.md)).

---

## Step 0 — Design completeness

| Metric | Before | After this doc |
|--------|--------|----------------|
| Overall (target) | ~3/10 (goals only) | **9/10** (ready for eng + design-consultation on tokens) |

**What 10/10 means here:** Every primary screen has hierarchy, states, and a11y notes; **empty** states are intentional; **Linear-like** is translated into concrete patterns, not “clean UI.”

**DESIGN.md:** **Not present** — after **final product name**, run **`/design-consultation`** (or author `DESIGN.md`) to lock typography, color tokens, and components. This plan constrains that session.

---

## Problem statement

**Users** (MVP: two people; product: multi-user) want to **track merchandise prices** on the web and get **email** when prices change or hit a **target** threshold. They describe **when** to check in **natural language**; the system turns that into reliable schedules.

**Out of scope for v1:** WhatsApp, SMS, custom user scripts, digest-only sends, quiet hours.

---

## Pass 1 — Information architecture (9/10)

### Primary hierarchy (every screen)

1. **What matters now** — alerts, failures, or “last run” health.  
2. **What you’re tracking** — list of monitors with **price + trend** at a glance.  
3. **Actions** — add monitor, edit, pause (one primary CTA per context).

### Navigation model (Linear-like)

- **App shell:** **left sidebar** (collapsible on tablet) + **main content** + **top bar** (account, global “Add monitor”).  
- **No marketing mega-nav inside app** — authenticated app is **tool-first**, not brochure.

### Site map (ASCII)

```
[Sign in with Google]  ← landing if signed out
        │
        ▼
┌───────────────────────────────────────────┐
│ Sidebar │ Dashboard (overview)            │
│         │   ├─ “Needs attention” strip      │
│         │   └─ Monitors table               │
│ Monitors├────────────────────────────────── │
│ Alerts  │ Monitor detail                   │
│ Account │   ├─ Price history (chart stub)  │
│         │   ├─ Schedule (NL + translated)   │
│         │   └─ Notification settings         │
└───────────────────────────────────────────┘
```

**Deep links:** `/`, `/monitors`, `/monitors/[id]`, `/settings` (profile + email sanity only in v1).

### “If only three things” on dashboard

1. **Status** — all green / N issues (failed fetch, parse error, auth).  
2. **Best deal movement** — biggest price drop or “new low” (optional strip if data exists).  
3. **Monitors** — compact table: **name, site, last price, last check, next check**.

---

## Pass 2 — Interaction states (9/10)

### Features × states

What the user **sees** (not backend jargon):

| Feature | LOADING | EMPTY | ERROR | SUCCESS | PARTIAL |
|---------|---------|-------|-------|---------|---------|
| Dashboard monitor list | Skeleton rows + sidebar shimmer | Warm illustration + **“Track your first item”** + URL field + **primary CTA** | Inline banner: “We couldn’t refresh prices” + **Retry** | Table populated | Some monitors OK, some show **warning pill** (parse uncertain) |
| Add monitor flow | Step progress frozen | N/A | Field-level: invalid URL; global: “Site blocked” / timeout | **“You’re watching …”** | Saved but **first fetch pending** → show **pending** row |
| Monitor detail / price | Chart + price skeleton | “No history yet — we’ll log after first check” | **Actionable:** “Selector missing” / “Couldn’t find price” + link to **fix selector** | Price + sparkline | **Stale** badge if check older than SLA |
| NL schedule input | Parse spinner | Placeholder examples | “We didn’t understand — try …” | Shows **translated schedule** + timezone | **Ambiguous** → disambiguation inline |
| Email notify | — | — | “We couldn’t send — verify email” (if ever needed) | Toast: “Alert sent” | — |

**Empty state rule:** Never ship **“No items found.”** Copy: **human, short, one clear action** (e.g. “Add something you want to stop overpaying for”).

---

## Pass 3 — User journey & emotional arc (8/10)

| Step | User does | User should feel | Plan supports via |
|------|-----------|------------------|-------------------|
| 1 | Lands signed out | **Trust** — serious tool, not spam | Minimal, Linear-like, no stock hero |
| 2 | Google sign-in | **Relief** — one click, no new password | **Google only** |
| 3 | First dashboard | **Clarity** — what to do next | Empty state **warm** + single CTA |
| 4 | Pastes product URL | **Confidence** | Preview **page title** + domain favicon |
| 5 | Sets NL schedule | **In control** | Always show **machine translation** of schedule |
| 6 | First alert email | **Delight** — it worked | Subject + **price delta** + link back |

---

## Pass 4 — Anti–AI-slop (Linear-like)

**Forbidden defaults:** generic three-column hero, random gradient blobs, “AI-powered” badges, stock isometric art.

**Linear-like** (specific):

- **Density:** Comfortable for power users; **12–14px** body (final in `DESIGN.md`), **tight vertical rhythm** (8px grid).  
- **Color:** **neutral surfaces**, **one accent** for primary actions (hue TBD in design-consultation). **Dark-first** UI with optional light (Linear is dark-first).  
- **Typography:** **Inter** or **Geist** — no mixed novelty fonts.  
- **Components:** **Tables** for monitors (not card grids), **subtle** row hover, **status badges** as pills.  
- **Motion:** **Micro** only — e.g. row highlight, **no** parallax.

**Differentiator copy:** Monitoring **merchandise** specifically — language can reference **“deals” / “price drops”** / **fair price** instead of generic “workflows.”

---

## Pass 5 — Design system alignment (6/10 until `DESIGN.md`)

- **Gap:** No `DESIGN.md` yet — **blocking:** finalize **name**, then **design-consultation** for tokens.  
- **This plan locks:** layout paradigm (sidebar + table), state philosophy, Linear-like tone.  
- **Component inventory (v1):** App shell, Data table, Form row, Badge, Toast, Modal/drawer for “Add monitor”, Chart stub.

---

## Pass 6 — Responsive & accessibility (8/10)

| Viewport | Intent |
|----------|--------|
| **Mobile** | Sidebar → **icon rail** or **hamburger**; **table → stacked cards** with same columns as priority order |
| **Tablet** | Collapsible sidebar |
| **Desktop** | Full Linear-like density |

**A11y (v1):**

- **Keyboard:** All primary flows without mouse; **focus rings** visible.  
- **Targets:** ≥ **44px** hit targets for touch.  
- **Contrast:** **WCAG AA** for text + interactive (validate in design-consultation).  
- **Semantics:** **Landmarks** — `nav`, `main`, `header`; tables with **scoped headers** where possible.  
- **Motion:** **Respect `prefers-reduced-motion`.**

---

## Pass 7 — Merchandise & “webstore” (product specifics)

### What “monitor” means in v1

- User provides **product URL** (merchandise page).  
- System runs **HTTP fetch** + **DOM price extraction** (selector or heuristic).  
- Optional: **target price** or **“notify on any drop”** (simplest rule set for v1).

### Webstore / site types

| Tier | Behavior | User expectation |
|------|----------|------------------|
| **Generic** | User **optional CSS selector** for price node; else **best-effort heuristic** | May need one-time **selector fix** for messy sites |
| **Connector backlog (post-v1)** | Amazon, Shopify, WooCommerce, **etc.** — structured parsers | Higher accuracy, less maintenance for user |

**Design implication:** First-run flow must **surface confidence**: **“We found price ¥X”** with **“Wrong price?”** → edit selector.

### Natural language scheduling

- **Input:** User types natural schedule; **Output:** always show **interpreted** schedule + **timezone** (default: browser → stored in profile).  
- **Failure:** **Inline** examples + **one-tap** presets (“Daily 9:00”, “Weekly Mon 9:00”).

---

## NOT in scope (v1)

- WhatsApp / SMS; custom **script** jobs; **digest** mode; **quiet hours**; multi-org billing; public API.

---

## What already exists in repo

- Governance + CI only — **no UI** to reuse. **Linear-like** is a **greenfield** choice.

---

## Sub-plans to add next (suggested)

1. `v1-google-auth.md` — OAuth flows, session, **session expiry** UX.  
2. `v1-email-delivery.md` — provider (e.g. SendGrid/SES), templates, **from** address, bounce handling.  
3. `gcp-cloud-run.md` — region choice, Scheduler → HTTP, secrets.

---

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | — | Not run | Optional |
| Codex Review | `/codex review` | 2nd opinion | — | Not run | Optional |
| Eng Review | `/plan-eng-review` | Architecture & tests | — | **Pending** | **Required before build** |
| Design Review | `/plan-design-review` | UI/UX gaps | 1 | **In progress** (this doc) | v1 merchandise design drafted; **name** + **DESIGN.md** open |

**UNRESOLVED:** Final **product name**; **GCP region**; **design-consultation** for tokens.  
**VERDICT:** Design **not** fully CLEAR until **eng review** + **DESIGN.md** — **eng review required** before implementation.

---

## Next step (AskUserQuestion — gstack format)

**Re-ground:** **Watchtower** repo, branch **`main`** (docs will land on a feature branch), task: **close open design decisions** before implementation.

**Simplify:** We need a **name** and a **region** so engineers and designers don’t build the wrong thing.

**RECOMMENDATION:** Choose **name** first (blocks `DESIGN.md`), then **GCP region** when you create the GCP project. **Completeness:** A 10/10, B 8/10.

**Options:**

- **A)** Reply with **final product name** in the next message (one word or short phrase).  
- **B)** Use a **temporary codename** for another week and run **design-consultation** in parallel with eng review.  
- **C)** **Pause** implementation until both **name** and **home region** (e.g. `us-central1`, `asia-southeast1`) are fixed.

---

*End of plan-design-review pass for v1 merchandise scope (document-only; no code).*
