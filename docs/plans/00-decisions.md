# Locked product decisions (from Q1–15)

> **Repo codename:** still **Watchtower** until a final name is chosen (required before locking `DESIGN.md`).

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
| 13 | **Rename** the product **before** locking **`DESIGN.md`** (working title: TBD). |

## Contradictions resolved

- **WhatsApp vs email:** v1 is **email only**; **WhatsApp** is explicitly **post-v1** so we don’t block shipping.

## Open (must fill before `DESIGN.md`)

1. **Final product name** (replace codename everywhere).
2. **Exact GCP region** once home location / quota is known.
