# Watchtower — engineering backlog

Format aligned with gstack review output from `/plan-eng-review` (2026-03-22).

## Open

### TODO-1 — Lock Postgres hosting

- **What:** Choose **Cloud SQL (Postgres)** vs **Neon** (or other) and document connection + migration strategy in `docs/plans/gcp-runtime.md`.
- **Why:** Unblocks schema migrations and local dev parity.
- **Pros:** One source of truth; fewer surprises in prod.
- **Cons:** Cloud SQL adds GCP console work; Neon adds vendor outside core GCP.
- **Context:** V1 is solo+friends; boring-by-default favors **Cloud SQL** in chosen region.
- **Depends on:** GCP project + **region** ([00-decisions.md](./docs/plans/00-decisions.md)).

### TODO-2 — NL → schedule library spike

- **What:** Spike **chrono-node** (or alternative) + timezone handling; document edge cases in `docs/plans/nl-schedule.md`.
- **Why:** Core UX promise; bugs here erode trust.
- **Pros:** Smaller than custom NLP; testable.
- **Cons:** Library maintenance; locale quirks.
- **Context:** Product plan requires **visible** cron translation.
- **Depends on:** None.

### TODO-3 — Email provider + templates

- **What:** Pick **Resend / SES / SendGrid**; define **transactional templates** (price drop, failure).
- **Why:** Required for v1 notifications.
- **Pros:** Resend DX high; SES boring on AWS-aligned teams — on GCP **Resend** or **SES via SMTP** both OK.
- **Cons:** Bounce handling, domain verification.
- **Context:** Immediate send only in v1.
- **Depends on:** Domain + DNS access.

### TODO-4 — Cron authentication contract

- **What:** Implement **OIDC verification** for Cloud Scheduler → Cloud Run **or** document **HMAC** fallback.
- **Why:** Prevents internet randos from triggering jobs.
- **Pros:** OIDC is GCP-native.
- **Cons:** Slightly more setup than shared secret.
- **Context:** See [v1-eng-implementation-plan.md](./docs/plans/v1-eng-implementation-plan.md).
- **Depends on:** Cloud Run service deployed.

## Done

- (none yet)
