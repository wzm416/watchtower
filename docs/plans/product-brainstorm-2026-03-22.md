# Product brainstorm — Watchtower V1 (depth + Terraform + price history)

> **Brainstorming skill** capture: intent, tradeoffs, and decisions **before** implementation.  
> **Companion plans:** [00-decisions.md](./00-decisions.md), [v1-merchandise-price-monitoring.md](./v1-merchandise-price-monitoring.md), [v1-eng-implementation-plan.md](./v1-eng-implementation-plan.md).

---

## 1. Context explored

- **Who:** MVP = you + spouse; product direction = multi-user.  
- **What:** Merchandise URLs, **NL schedules**, **email** alerts, **Linear-like** UI.  
- **Stack:** Python API + React; GCP first; desire **Terraform** and **future cloud portability**.  
- **New:** Explicit **price history** (not only “last price”).

---

## 2. Product depth — job to be done

**Job:** “Stop missing a better price on something I already decided to buy—or avoid overpaying because I forgot to check.”

| Layer | Question | V1 stance (proposed) |
|-------|----------|----------------------|
| **Trigger** | When do we email? | **Any successful parse** that **changes** normalized price vs last snapshot **OR** crosses user **target** (if set). Optional: “notify on first successful watch” (onboarding delight). |
| **Trust** | User must believe the number | Show **last fetched time**, **confidence** (high/medium/low), **raw currency**; “wrong price?” → edit selector. |
| **Failure** | Site blocks bot | **Run** row with **http status** + short message; **no spam** email on repeated failure (digest or single “still failing” after N tries — **decide in Q1**). |
| **Stock** | “Out of stock” | V1: store **parse status** enum if we can detect OOS strings; else **unknown**. Don’t pretend. |
| **Multi-currency** | Global shops | Store **ISO 4217** + **minor units** (integer) per snapshot; normalize compare **within same monitor** only. |
| **Discovery** | How does the user **find** the product URL to watch? | **V1 baseline:** user **pastes a product URL** (current plan). **Stretch:** user types a **natural-language “what I want” prompt** → **Gemini** turns it into a **structured search plan** (keywords, store hints, optional filters) and/or **suggested next steps**—see **§2.1** below. |

### 2.1 Flexible product search — user prompt + Gemini (proposed)

**Intent:** Lower friction: *“cheapest OLED TV 55 inch under $800 from Best Buy or Amazon”* → system helps shape **criteria**, not replace the user’s judgment on **which exact page** to trust.

**Why not “fully autonomous shopping agent” in V1:** Legal/ToS risk, bot blocking, and **price truth** still require a **stable product URL** for our **HTTP + DOM** pipeline. The **monitor** remains **URL + selector**; Gemini is an **assistant layer** before that.

| Mode | What happens | Pros | Cons |
|------|----------------|------|------|
| **A) Assistant only (recommended first)** | User prompt → **Gemini** returns **JSON**: `{ summary, keywords[], site_hints[], price_max_minor?, currency }` + **short rationale**. UI shows it; user still **pastes or picks** the canonical **product URL** to create a **Monitor**. | No automatic scraping of search results pages; **safer**; tests are easy. | One extra step for the user. |
| **B) Suggested links (careful)** | Same as A, plus Gemini may output **candidate URLs** (only **https**, user allowlist domains TBD). User **must confirm** one link before monitoring. | Faster when links are good. | Hallucinated/broken links; **moderation** needed. |
| **C) Auto-pick URL** | Model chooses a URL and we start monitoring without confirmation | Fastest fantasy | **High** wrong-URL risk; **not recommended** for V1. |

**RECOMMENDATION:** Ship **V1** with **paste URL** only; add **Mode A** as **V1.1 / early V2** once core loop is stable. **Mode B** only with **explicit** user click on **“Use this URL”** per candidate.

**GCP fit:** Use **Vertex AI Gemini** (same org/billing as Cloud Run) or **Gemini API** with a **service account** / API key in **Secret Manager**. Log **prompt hashes** + latency; **avoid** storing raw prompts in DB unless user opts in (privacy).

**Eng notes (for [v1-eng-implementation-plan.md](./v1-eng-implementation-plan.md)):** New **`POST /api/discovery/plan`** (name TBD): body `{ prompt, locale }` → Gemini with a **fixed system instruction** (output **strict JSON schema**); **rate limit** per user; **timeout** ~10s; **no** server-side follow-up HTTP fetches triggered by the model without user action.

---

## 3. Price history — three approaches

| Approach | Behavior | Pros | Cons |
|----------|----------|------|------|
| **A) Append-only snapshot (recommended)** | Every successful check writes **PriceSnapshot** (monitor, time, amount, currency, run_id, confidence). | Full chart, audit, “lowest in 30d”; aligns with “history log.” | More rows; need **retention** policy. |
| **B) Only on change** | Insert row **only** when parsed price ≠ previous. | Smaller DB. | Misses “same price” checks; worse for “last checked” analytics. |
| **C) Hybrid** | Always write **Run**; write **Snapshot** on change **or** daily heartbeat. | Balance. | More rules to explain. |

**RECOMMENDATION: A** — append **PriceSnapshot** for every **successful** parse (and optionally **failed** Run without snapshot for ops). **Completeness 9/10.**

**Retention (policy, not implementation here):** e.g. **90 days** detailed + optional **monthly rollup** later; MVP can keep **all** until disk matters.

---

## 4. Terraform / IaC — portability framing

**Goal:** **One place** defines **Cloud Run + Cloud SQL + Scheduler + (optional) LB + IAM**; **repeatable** envs (staging/prod).

| Approach | Description | Portability | Effort |
|----------|-------------|-------------|--------|
| **A) Terraform GCP-first (recommended)** | `terraform/` with **google** provider; modules: `network`, `sql`, `run`, `scheduler`, `secrets`. Remote state **GCS** backend. | Same TF **language**; moving clouds = **rewrite providers + resources** but **patterns** (DB + container + cron) stay. **Human ~2–3d / CC ~1–2h** for skeleton. | **9/10** completeness |
| **B) Terragrunt** | DRY for multi-env. | Same as A + less copy-paste. | +complexity for solo MVP. |
| **C) “Cloud-agnostic” abstraction** | e.g. only **Kubernetes + Helm** everywhere | Real portability **if** you run K8s on GCP/Azure/AWS | **Ocean** for V1 — defer. |

**RECOMMENDATION: A** — **Terraform**, **GCP provider**, **pin versions**, **modules** small enough to swap **Cloud Run → Cloud Run equivalent** on another cloud later (container image + env vars + managed SQL).

**NOT Terraform in V1 app repo for:** application **business logic** — only **infrastructure**.

---

## 5. Design sections (approval checkpoints)

### 5.1 Core entities (refined)

- **User** — unchanged.  
- **DiscoveryPlan** (optional, **post-V1 baseline**) — userId, **prompt** (or redacted ref), **geminiResponseJson**, **createdAt**; ephemeral OK if we don’t need history of prompts.  
- **Monitor** — product URL, label, selector, schedule, timezone, **optional target_price_minor**, **notify_on** enum (change | target | both).  
- **Run** — each HTTP attempt (success/fail).  
- **PriceSnapshot** — append-only; **FK** to Run; **amount_minor**, **currency**, **confidence**, **observed_at**.  
- **Notification** — email sends (dedupe keys).

### 5.2 Data flow (history)

```
Scheduler → tick → fetch → parse → write Run → write PriceSnapshot (if success)
                              → compare to last snapshot → maybe notify
```

### 5.3 UI (monitor detail)

- **Chart:** time vs price (from **PriceSnapshot**).  
- **Table:** recent runs (status, time, price if any).  
- **Export (post-v1):** CSV of history.

---

## 6. Open questions (answer over time — skill: one at a time in chat)

1. **Failed-run emails:** Single alert after **N** failures, or **every** failure (noisy)?  
2. **First successful fetch:** Email “you’re tracking X @ price Y” or silent until **change**?  
3. **Terraform scope in V1 PR:** **Prod only** or **staging + prod** from day one?  
4. **Gemini discovery:** Ship **URL-paste only** first, then **Mode A** in **V1.1**, or **bundle Mode A** into first public release?

---

## 7. NOT in scope (this brainstorm)

- WhatsApp, user scripts, marketplace connectors beyond generic scrape.  
- Multi-cloud **active** failover.  
- Legal/compliance beyond “don’t violate site ToS” (user responsibility + rate limits in eng plan).  
- **Fully autonomous** “search and buy” without user-confirmed **product URL** (see §2.1).

---

## 8. Next steps

- Approve **snapshot model + Terraform approach A** or request changes.  
- Merge updates into [v1-eng-implementation-plan.md](./v1-eng-implementation-plan.md) (done in same PR as this file).  
- Optional: **`/plan-design-review`** refresh for chart/table copy when UI is built.

---

*Brainstorm document — not a binding contract until you confirm in issue/PR.*
