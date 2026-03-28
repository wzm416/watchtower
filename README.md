# Watchtower

Scheduled **merchandise price** monitoring—**natural-language** schedules, **email** alerts; **Google** sign-in. **WhatsApp** is a post-v1 channel. Product name: **Watchtower** (see [plans](./docs/plans/)).

## Status

**Phase 0:** Repo + CI. **Phase 1:** V1 plans in [`docs/plans/`](./docs/plans/). **App scaffold:** `api/` (FastAPI) and `web/` (Vite + React + TypeScript); CI runs pytest, Ruff, and `npm run build`.

## Development

```bash
# API — http://localhost:8000  (GET /health, /docs)
cd api && python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn watchtower_api.main:app --reload --host 0.0.0.0 --port 8000

# Web — http://localhost:5173
cd web && npm install && npm run dev
```

Copy `api/.env.example` → `api/.env` and `web/.env.example` → `web/.env`. For the API, run Postgres locally (or use Cloud SQL/Neon), set `DATABASE_URL`, `GOOGLE_CLIENT_IDS`, and `CRON_BEARER_TOKEN`, then `cd api && alembic upgrade head`. The SPA should send the Google **ID token** as `Authorization: Bearer` when calling `/api/v1/monitors`.

## Goals (roadmap)

| Area | Intent |
|------|--------|
| Stack | **Python** backend (API) + **React** frontend; **GCP Cloud Run** + Scheduler |
| Jobs | **HTTP + DOM price scrape** first; NL → schedule; user scripts later |
| UI | **Linear-like** dense dashboard (see product plan) |
| Identity | **Sign in with Google** (required for v1) |
| Notifications | **Email only** in v1 (immediate); WhatsApp later |
| Hosting | **GCP** — region closest to operator (documented in runbooks later) |

## Repository

**https://github.com/wzm416/watchtower**

## Quick links

- [Contributing](./CONTRIBUTING.md) — branches, PRs, reviews
- [Branch protection](./docs/BRANCH_PROTECTION.md) — enforce `main` via GitHub
- [CI workflow template](./docs/templates/github-actions-ci.yml) — copy into `.github/workflows/` after `gh auth refresh -s workflow`
- [Security](./SECURITY.md) — reporting vulnerabilities
- [Product plans](./docs/plans/) — decisions + V1 merchandise design (plan-design-review)

## License

MIT — see [LICENSE](./LICENSE).
