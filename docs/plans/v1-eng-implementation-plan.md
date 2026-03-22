# V1 — Engineering implementation plan (plan-eng-review)

> **Branch reviewed:** `feat/docs-product-plans` @ `73435b2`  
> **Inputs:** [00-decisions.md](./00-decisions.md), [v1-merchandise-price-monitoring.md](./v1-merchandise-price-monitoring.md)  
> **Codex plan pass:** skipped (`codex` CLI not installed).

---

## Step 0 — Scope challenge

| Question | Answer |
|----------|--------|
| **Existing code solving sub-problems?** | **None** — repo is docs + CI only. No parallel flows to reuse. |
| **Minimum change for V1?** | One **Next.js** app on **Cloud Run** + **Postgres** + **Google OAuth** + **Scheduler-triggered jobs** + **email**. Defer: WhatsApp, user scripts, site-specific connectors beyond generic fetch+selector. |
| **Complexity smell (8+ files / 2+ services)?** | First slice should stay **one deployable** (monolith Next.js) + **managed DB** + **one email provider**. Split workers only if job runtime exceeds HTTP limits. |
| **Search / built-ins [Layer 1]** | Use **Auth.js (NextAuth v5)** for Google OAuth; **Cloud Scheduler → HTTP** on Cloud Run; **Cloud SQL (Postgres)** or **Neon** (if leaving pure-GCP optional); **chrono-node** or **@breejs/later** + explicit cron display for NL→schedule; **cheerio** for server-side DOM. |
| **TODOS.md** | Created — see [TODOS.md](../../TODOS.md). |
| **Completeness vs shortcut** | Prefer **complete error paths + tests for domain logic** (price parse, schedule parse, job orchestration); AI makes this cheap per Boil the Lake. |

**Scope accepted:** Single-region, single service V1; **innovation tokens** spent on **reliable scraping + NL schedule**, not microservices.

---

## Prerequisite offer (/office-hours)

**Skipped** — product problem statement and alternatives already captured in `docs/plans/`.

---

## 1. Architecture review

### 1.1 System context

```
                    ┌─────────────┐
  Users ──────────► │  Next.js    │◄─── Google OAuth (Auth.js)
  (browser)         │  Cloud Run  │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   ┌──────────┐     ┌────────────┐    ┌─────────────┐
   │ Postgres │     │ Secret     │    │ Email API   │
   │ (Cloud   │     │ Manager    │    │ (Resend /   │
   │  SQL or  │     │ (GCP)      │    │  SES / etc) │
   │  Neon)   │     └────────────┘    └─────────────┘
   └──────────┘
         ▲
         │  job enqueue / state
         │
   ┌─────┴──────────────┐
   │ Cloud Scheduler     │  (HTTP POST + auth)
   │ e.g. */5 * * * *    │
   └────────────────────┘
```

### 1.2 Core domain model (logical)

- **User** — id, google sub, email, timezone default.  
- **Monitor** — userId, label, productUrl, optional cssSelector, scheduleCron, timezone, status (active/paused), lastRunAt, lastPrice, parseConfidence.  
- **Run** — monitorId, startedAt, finishedAt, httpStatus, rawSnippet?, parsedPrice?, errorCode?  
- **Notification** — monitorId, sentAt, channel=email, templateId, status.

### 1.3 Job execution path

```
Scheduler ──► POST /api/jobs/tick (or /api/internal/cron)
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
| **Cron endpoint abuse** | **No public cron** — verify **OIDC token** from Scheduler (recommended) or **HMAC secret** in header; reject otherwise. |
| **User data isolation** | All queries **scoped by userId** from session; RLS optional phase-2. |
| **Secrets** | GCP Secret Manager for `DATABASE_URL`, email API key, cron secret. |
| **Fetch SSRF** | **Allowlist schemes** `https:` only; optional blocklist for private IPs; timeout **10s** default. |

### 1.5 Production failure scenarios (sample)

| Failure | Mitigation in plan |
|---------|-------------------|
| Target site 403/bot block | Surface **actionable** UI state; store **httpStatus** on Run; optional **Playwright** later — **not V1** default. |
| DOM change | **parseConfidence** low → warning pill; user fixes selector. |
| Scheduler duplicate tick | **Idempotent** job keys + transaction around “claim” monitor run. |
| Email provider down | Retry with backoff; **dead letter** row or alert to admin. |

**Architecture issues count:** **0 blocking** — one open **product** choice: **Postgres on Cloud SQL (GCP-native)** vs **Neon** (simpler ops, cross-cloud).  
**RECOMMENDATION [Layer 1]:** **Cloud SQL Postgres** in chosen region for **boring-by-default** GCP alignment; Neon acceptable if team prefers serverless Postgres and simpler billing.

---

## 2. Code quality review (planned structure — no code yet)

| Topic | Guidance |
|-------|----------|
| **Layout** | `app/` routes, `lib/db`, `lib/jobs`, `lib/parse`, `lib/email`, `lib/auth`; **no** god `utils.ts`. |
| **DRY** | Single **fetch+parse** pipeline; shared **error taxonomy** for monitors. |
| **Explicit > clever** | Store **cron string + IANA timezone**; show **human** schedule from same source of truth. |

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
| API routes | **Integration** — auth mock + DB test container or sqlite not suitable — use **test Postgres** (docker) or **pglite** |
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
| **Cold start** | Cloud Run **min instances = 0** OK for MVP; set **concurrency** 1–4 for CPU-bound parse. |

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
| Step 0 | **Scope accepted** — monolith V1 |
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
| Eng Review | `/plan-eng-review` | Architecture & tests | 1 | **CLEAR** (with notes) | Monolith V1, Postgres, Scheduler, Auth.js, tests for parse/schedule |
| Design Review | `/plan-design-review` | UI/UX | 1 | prior | See product plan |

**UNRESOLVED:** Pick **GCP region** at project creation; choose **Cloud SQL vs Neon** for Postgres.  
**VERDICT:** **Eng plan ready to implement** — run **`/ship`** when code + CI tests land.

---

## Next steps

1. Merge **`feat/docs-product-plans`** (or open PR from current branch).  
2. Scaffold **Next.js** + **Auth.js** + **DB** + **single cron** route.  
3. Implement **parse + schedule** modules **with tests first** (TDD).  
4. Add **`/plan-design-review`** on UI PRs if components diverge from product plan.
