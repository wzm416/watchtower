# V1 — Engineering implementation plan (plan-eng-review)

> **Branch reviewed:** `feat/docs-product-plans` @ `73435b2`  
> **Inputs:** [00-decisions.md](./00-decisions.md), [v1-merchandise-price-monitoring.md](./v1-merchandise-price-monitoring.md)  
> **Codex plan pass:** skipped (`codex` CLI not installed).

### Architecture change (2026-03-22)

**Supersedes** the earlier draft that proposed a **Next.js monolith**. **V1 is now:**

- **Backend:** **Python** (**FastAPI** recommended) on **Cloud Run** — REST API, jobs, scraping, email.
- **Frontend:** **React** (**Vite** recommended) — SPA calling the API; **Google Sign-In** in the browser, **ID token** verified on the API.

---

## Step 0 — Scope challenge

| Question | Answer |
|----------|--------|
| **Existing code solving sub-problems?** | **None** — repo is docs + CI only. No parallel flows to reuse. |
| **Minimum change for V1?** | **Python API** + **React SPA** + **Postgres** + **Google OAuth (token verify)** + **Cloud Scheduler → HTTP** + **email**. Defer: WhatsApp, user scripts, site-specific connectors beyond generic fetch+selector. |
| **Complexity smell (8+ files / 2+ services)?** | **Two deployables** is acceptable: **`api`** (Python) + **`web`** (static React on Cloud Run or GCS+LB). Same **Postgres** + **one email provider**. Split only further if job CPU exceeds API **timeout** (then optional worker service). |
| **Search / built-ins [Layer 1]** | **FastAPI** + **SQLAlchemy 2** + **Alembic**; **Google `google-auth`** / **oauthlib** to verify **ID tokens**; **httpx** for HTTP fetch; **beautifulsoup4** + **lxml** for DOM; **dateparser** + **croniter** (and **zoneinfo**) for NL→schedule; **Cloud Scheduler → HTTP** on **same API** (`/internal/jobs/tick`) with **OIDC/HMAC**; **pytest** for tests. |
| **TODOS.md** | See [TODOS.md](../../TODOS.md). |
| **Completeness vs shortcut** | Prefer **complete error paths + tests** for **parse/schedule/compare** in Python; AI makes this cheap per Boil the Lake. |

**Scope accepted:** Single region; **two** user-facing deployables (API + web); innovation tokens on **scraping + NL schedule**, not microservice sprawl.

---

## Prerequisite offer (/office-hours)

**Skipped** — product problem statement and alternatives already captured in `docs/plans/`.

---

## 1. Architecture review

### 1.1 System context

```
  Users (browser)
       │
       ▼
┌──────────────┐     Google Sign-In     ┌─────────────────────┐
│ React (Vite) │ ──── (ID token) ────► │ Python FastAPI      │
│ Cloud Run or │     HTTPS / JSON       │ Cloud Run (`api`)   │
│ GCS + CDN    │ ◄── REST + CORS ─────  │                     │
└──────────────┘                        └──────────┬──────────┘
                                                   │
              ┌────────────────────────────────────┼────────────────┐
              ▼                    ▼                 ▼                ▼
        ┌──────────┐       ┌────────────┐   ┌─────────────┐  ┌──────────┐
        │ Postgres │       │ Secret Mgr │   │ Email API   │  │ httpx    │
        │ Cloud SQL│       │ (GCP)      │   │ (Resend/…)  │  │ → shops  │
        │ or Neon  │       └────────────┘   └─────────────┘  └──────────┘
        └──────────┘
              ▲
              │  Cloud Scheduler  (OIDC or HMAC)
              │
        ┌─────┴──────────────┐
        │ POST /internal/... │
        │ e.g. */5 * * * *   │
        └────────────────────┘
```

**CORS:** API allows **only** the deployed **web** origin(s). **Secrets:** `DATABASE_URL`, email API key, `GOOGLE_CLIENT_ID`, cron verifier secret / rely on **OIDC** from Scheduler.

### 1.2 Core domain model (logical)

- **User** — id, google sub, email, timezone default.  
- **Monitor** — userId, label, productUrl, optional cssSelector, scheduleCron, timezone, status (active/paused), lastRunAt, lastPrice, parseConfidence.  
- **Run** — monitorId, startedAt, finishedAt, httpStatus, rawSnippet?, parsedPrice?, errorCode?  
- **Notification** — monitorId, sentAt, channel=email, templateId, status.

### 1.3 Job execution path

```
Scheduler ──► POST /internal/jobs/tick (or /api/v1/internal/cron)
              │
              ├─► list due monitors (query by next_run)
              │
              └─► for each (bounded concurrency):
                    fetch URL ──► parse HTML ──► extract price
                    compare to previous ──► persist Run
                    if rule fires ──► send email (idempotent key)
```

**Idempotency:** `notification` rows dedupe `(monitorId, priceBucket, day)` or event-id to avoid email storms on retries.

### 1.4 Security architecture

| Concern | Mitigation |
|---------|------------|
| **Google auth** | React obtains **ID token** (GIS); API validates with **`google-auth`** (`verify_oauth2_token`) and maps **sub** → `User`; session via **httpOnly cookie** (API-set) or **short-lived JWT** — pick one and document. |
| **Cron endpoint abuse** | **No public cron** — verify **OIDC token** from Scheduler (recommended) or **HMAC secret** in header; reject otherwise. |
| **User data isolation** | All queries **scoped by userId** from validated identity; RLS optional phase-2. |
| **Secrets** | GCP Secret Manager for `DATABASE_URL`, email API key, Google client secret (if server-side flow), cron secret. |
| **Fetch SSRF** | **Allowlist schemes** `https:` only; optional blocklist for private IPs; timeout **10s** default. |
| **CORS** | Strict **allowlist** — production web origin only. |

### 1.5 Production failure scenarios (sample)

| Failure | Mitigation in plan |
|---------|-------------------|
| Target site 403/bot block | Surface **actionable** UI state; store **httpStatus** on Run; optional **Playwright** later — **not V1** default. |
| DOM change | **parseConfidence** low → warning pill; user fixes selector. |
| Scheduler duplicate tick | **Idempotent** job keys + transaction around “claim” monitor run. |
| Email provider down | Retry with backoff; **dead letter** row or alert to admin. |

**Architecture issues count:** **0 blocking** — open **infra** choices: **Postgres on Cloud SQL** vs **Neon**; **web** on **Cloud Run** (nginx/static) vs **Cloud Storage + HTTPS LB** (cheaper static).  
**RECOMMENDATION [Layer 1]:** **Cloud SQL Postgres** + **two Cloud Run services** (`api`, `web`) for **simple mental model** and **private networking** options later.

---

## 2. Code quality review (planned structure — no code yet)

| Topic | Guidance |
|-------|----------|
| **Layout (Python)** | `app/` or `src/` with **routers**, `services/`, `models/`, `schemas/`; **parse** and **schedule** in **pure functions** + `tests/`. |
| **Layout (React)** | `src/` features or **route-based** folders; shared **UI primitives** for Linear-like density. |
| **DRY** | Single **fetch+parse** pipeline in Python; shared **error codes** for API + UI. |
| **Explicit > clever** | Store **cron + timezone** in DB; API returns **both** machine and **human** summary for schedules. |

**Issues flagged:** **0** (implementation not started).

---

## 3. Test review

### 3.1 Flow diagram (what must gain tests)

```
NL input ──► parseSchedule() ──► cron + timezone validation
productUrl + html ──► extractPrice() ──► Money + confidence
comparePrices(old, new, rule) ──► shouldNotify boolean
```

| New behavior | Test type |
|--------------|-----------|
| Schedule parsing / timezone | **Unit** — edge cases for ambiguous NL (mocked) |
| Price extraction | **Unit** — fixture HTML snippets |
| Notification rule | **Unit** — thresholds, equality, first-run |
| API routes | **Integration** — **pytest** + **TestClient** + **Postgres** (docker **testcontainers** or CI service) |
| Cron route | **Integration** — OIDC/HMAC verification |

**Test plan artifact:** written to `~/.gstack/projects/wzm416-watchtower/` (see filesystem).

**Gaps:** **0** until code exists; **mandatory** before merge: **parse + schedule + compare** unit tests.

---

## 4. Performance review

| Risk | V1 mitigation |
|------|----------------|
| **N+1** | Batch load monitors for tick; **limit** monitors per tick wave. |
| **Fetch slow** | Per-URL **timeout**; max **N** concurrent fetches (config). |
| **DB** | Indexes on `(userId)`, `(nextRunAt)`; prune old **Run** rows (retention policy). |
| **Cold start** | Cloud Run **min instances = 0** OK for MVP; **api** concurrency **1–4** if parse is CPU-heavy; **web** is static — near-zero cold start if served from CDN. |

**Issues:** **0** blocking for MVP scale (solo + friends).

---

## NOT in scope (engineering)

- Separate worker fleet, **Kafka**, **multi-region** active-active.  
- **Playwright** in V1 path (adds ops weight).  
- User-supplied **arbitrary scripts** (sandbox ocean).  
- **WhatsApp** delivery pipeline.

---

## What already exists

- **CI:** GitHub Actions sanity check.  
- **No application runtime** — greenfield.

---

## Failure modes → tests / UX

| Codepath | Failure | Test? | User-visible? |
|----------|---------|-------|----------------|
| Fetch | timeout | yes | yes — “Couldn’t reach site” |
| Parse | no price node | yes | yes — “Wrong price?” |
| Notify | email API 5xx | retry | optional admin log |
| Cron | bad auth | yes | no — 401 only in logs |

**Critical gaps:** **none** identified at plan level; implementation must wire **silent failure** checks.

---

## Completion summary (plan-eng-review)

| Item | Result |
|------|--------|
| Step 0 | **Scope accepted** — Python API + React web V1 |
| Architecture | **8** observations, **0** unresolved blockers |
| Code quality | N/A (no code) |
| Tests | **Diagram + strategy**; **gaps: 0** pre-code |
| Performance | **4** notes |
| NOT in scope | **written** |
| What exists | **written** |
| TODOS | **TODOS.md** created |
| Failure modes | **critical gaps: 0** at plan stage |
| Lake score | Prefer **complete** parse/test coverage when implementing |

**MODE:** `FULL_REVIEW` (docs-only).

**STATUS:** `issues_open` — **1** unresolved deploy-time decision (**GCP region**).

---

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 0 | — | Optional |
| Codex Review | `/codex review` | 2nd opinion | 0 | — | CLI absent |
| Eng Review | `/plan-eng-review` | Architecture & tests | 2 | **CLEAR** (updated) | **Python + React**, Postgres, Scheduler, Google token verify, tests for parse/schedule |
| Design Review | `/plan-design-review` | UI/UX | 1 | prior | See product plan |

**UNRESOLVED:** Pick **GCP region** at project creation; choose **Cloud SQL vs Neon** for Postgres.  
**VERDICT:** **Eng plan ready to implement** — run **`/ship`** when code + CI tests land.

---

## Next steps

1. Merge docs branch when ready.  
2. Scaffold **`api/`** (FastAPI) + **`web/`** (Vite + React) + **Postgres** + **internal cron** route.  
3. Implement **parse + schedule** in Python **with pytest first** (TDD).  
4. Wire **Google Sign-In** on React + **token verification** on API.  
5. **`/plan-design-review`** on UI PRs if screens diverge from the product plan.
