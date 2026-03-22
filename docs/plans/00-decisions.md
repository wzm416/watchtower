# Locked product decisions (from Q1–15)

> **Product name:** **Watchtower** — confirmed for **eng review and initial `DESIGN.md`** (option **B**); rename later if needed.

## Stack & process

| # | Decision |
|---|----------|
| 1 | **1A:** Full **7-pass** plan-design-review on written plans + **TypeScript + Next.js** on **GCP Cloud Run** (with **Cloud Scheduler**), per prior recommendation. |
| 14 | Plans live under **`docs/plans/`** with **sub-plan docs per step/milestone** (this folder). |
| 15 | Use gstack sequence: **plan-design-review → plan-eng-review** before heavy build. |

## V1 product scope

| # | Decision |
|---|----------|
| 2 | **V1:** **Merchandise price monitoring**; **notify by email only**. Product/store UX detailed in [v1-merchandise-price-monitoring.md](./v1-merchandise-price-monitoring.md). |
| 3 | **Architecture:** multi-user ready; **MVP operators:** **you + your wife** (2 accounts). |
| 4 | **Sign in with Google** is **required** (no password-only v1). |
| 5 | **WhatsApp** is the preferred **future** channel (not v1). **v1 = email only** (see #8). |
| 6 | **Ship first:** **HTTP check** + **price / DOM scrape**. Later: user-defined checks expressed as scripts → translated to scheduled job types. |
| 7 | **Natural language** for schedule intent (e.g. “every morning”, “weekdays 9am PT”) — product must translate to real cron/timezone rules. |
| 8 | **Notifications:** **email only** in v1; **send immediately** (no quiet hours / digest in v1). |
| 9 | Same as #8: **immediate** delivery. |

## Infra & scale

| # | Decision |
|---|----------|
| 10 | **GCP region:** **closest to operator** — pick at project setup (measure latency or choose nearest region to home; document in GCP runbook when created). |
| 11 | **Scale posture:** **solo + friends** (low volume; reliability > multi-tenant polish for v1). |

## Brand & UI direction

| # | Decision |
|---|----------|
| 12 | **Visual direction:** **Linear-like** — dense, calm, keyboard-friendly, professional (not generic “AI SaaS” cards). |
| 13 | **Name:** keep **Watchtower** for now (through eng review / first design system); optional rename post–v1. |

## Contradictions resolved

- **WhatsApp vs email:** v1 is **email only**; **WhatsApp** is explicitly **post-v1** so we don’t block shipping.

## Open (before first GCP deploy)

1. **Exact GCP region** once home location / quota is known.

**Resolved:** Product name — **Watchtower** (see Q13 option B).
