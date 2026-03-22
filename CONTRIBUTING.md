# Contributing

## Branch model

- **`main`** is the **protected** release branch. **Do not push directly to `main`.**
- All work happens on **feature branches** named `feat/<short-description>`, `fix/<short-description>`, or `chore/<short-description>`.
- Changes reach `main` only through **pull requests** that pass CI and receive **at least one approval** (once branch protection is enabled).

> Note: We use **`main`** as the default branch. Older docs sometimes refer to `master`; treat `main` as the protected default.

## Workflow

1. **Sync** from `main`:
   ```bash
   git fetch origin && git checkout main && git pull origin main
   ```
2. **Create a branch**:
   ```bash
   git checkout -b feat/your-change
   ```
3. **Commit** with clear messages (imperative mood, optional [Conventional Commits](https://www.conventionalcommits.org/) prefix).
4. **Push** and open a **Pull Request** into `main`.
5. **Address review** and ensure **CI is green** before merge.

## Pull requests

- Keep PRs focused and reasonably small.
- Describe *what* and *why*; link issues if applicable.
- Update docs when behavior or setup changes.

## Code review

- Be constructive and specific.
- Prefer approvals from someone who did not author the majority of the PR when possible.

## Local development

Instructions will be added with the first application stack (e.g. `docs/development.md`).
