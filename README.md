# Watchtower

Scheduled monitoring jobs with notifications—watch prices, pages, or custom checks; get concise summaries by **email** or **SMS**.

## Status

**Phase 0:** Repository and contribution workflow are set up. Application code, GCP deployment, and auth flows will land behind feature branches and PRs.

## Goals (roadmap)

| Area | Intent |
|------|--------|
| Jobs | User-defined schedules (cron-style) for fetching, comparing, and summarizing |
| UI | Clear dashboard to create/edit jobs and view history |
| Identity | Sign-in with **Google** for email delivery; verified channel for SMS |
| Notifications | Email (transactional) and SMS (provider TBD) |
| Hosting | **Google Cloud Platform** (details in upcoming `docs/gcp/`) |

## Quick links

- [Contributing](./CONTRIBUTING.md) — branches, PRs, reviews
- [Branch protection](./docs/BRANCH_PROTECTION.md) — enforce `main` via GitHub
- [Security](./SECURITY.md) — reporting vulnerabilities

## License

MIT — see [LICENSE](./LICENSE).
