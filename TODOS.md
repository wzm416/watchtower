# Watchtower — engineering backlog

Format aligned with gstack review output from `/plan-eng-review` (2026-03-22).

## Open

### TODO-1 — Lock Postgres hosting

- **What:** Choose **Cloud SQL (Postgres)** vs **Neon** (or other) and document connection + migration strategy in `docs/plans/gcp-runtime.md`.
- **Why:** Unblocks production parity with local Docker/Postgres.
- **Depends on:** GCP project + **region** ([00-decisions.md](./docs/plans/00-decisions.md)).

### TODO-1b — Gemini discovery spike (optional; after core URL monitor works)

- **What:** Prototype **Vertex AI Gemini** (or Gemini API) call: user **prompt** → **strict JSON** search plan; document schema + rate limits in `docs/plans/gemini-discovery.md`.
- **Context:** See [product-brainstorm-2026-03-22.md](./docs/plans/product-brainstorm-2026-03-22.md) §2.1.
- **Depends on:** GCP project + **core monitor path** stable.

### TODO-4 — Cron authentication contract (hardening)

- **What:** Add **OIDC verification** for Cloud Scheduler → Cloud Run in addition to **Bearer `CRON_BEARER_TOKEN`**.
- **Context:** See [v1-eng-implementation-plan.md](./docs/plans/v1-eng-implementation-plan.md).
- **Depends on:** Cloud Run service deployed.

## Done (recent implementation)

- **TODO-0 — Terraform baseline:** `terraform/environments/staging` + `docs/plans/gcp-terraform.md` (API enablement scaffold; extend with Cloud SQL / Run / Scheduler).
- **TODO-2 — NL → schedule:** Best-effort English phrases + `POST /api/v1/schedule/translate`; cron validated with **croniter** + **zoneinfo**; `next_run_at` on monitors.
- **TODO-3 — Email provider:** **Resend** integration in API (`RESEND_API_KEY`, `RESEND_FROM_EMAIL`); skipped gracefully when unset.
- **Core monitor path:** Fetch + DOM price extract, `Run` / `PriceSnapshot`, internal tick, web GIS sign-in + monitors UI.

## Historical notes (superseded by Done above)

The following were originally listed as open; baseline code now exists — keep refining in PRs.

- ~~Terraform baseline~~ → see `terraform/`
- ~~NL schedule spike~~ → `schedule_nl.py` + translate endpoint
- ~~Email templates~~ → HTML body in `tick_runner._render_email` (iterate with design)
