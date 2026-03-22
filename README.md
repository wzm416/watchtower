# Watchtower

Scheduled **merchandise price** monitoring—**natural-language** schedules, **email** alerts; **Google** sign-in. **WhatsApp** is a post-v1 channel. Product name: **Watchtower** (see [plans](./docs/plans/)).

## Status

**Phase 0:** Repo + CI. **Phase 1 (planned):** V1 product design and eng plan in [`docs/plans/`](./docs/plans/) — implementation follows **`/plan-eng-review`**.

## Goals (roadmap)

| Area | Intent |
|------|--------|
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
