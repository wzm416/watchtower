# Protecting `main` on GitHub

The goal is: **no direct pushes to `main`**; all changes merge via **pull request** with **CI passing** and **required review**.

## Option A — GitHub UI (recommended)

1. Open the repo on GitHub → **Settings** → **Rules** → **Rulesets** (or **Branches** → **Branch protection rules** on classic UI).
2. Add a rule for branch name pattern **`main`**:
   - Require a pull request before merging
   - Require approvals: **1** (adjust per team policy)
   - Require status checks to pass (when CI exists, add the workflow job name)
   - Do not allow bypassing the above settings (optional: allow admins only if needed)

## Option B — GitHub CLI

If your token has `admin` scope on the repo, you can apply protection via API. Example (adjust to your checks):

```bash
gh api repos/<owner>/<repo>/rulesets --method POST --input - <<'EOF'
{
  "name": "protect-main",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": { "include": ["refs/heads/main"], "exclude": [] }
  },
  "rules": [
    { "type": "pull_request", "parameters": { "required_approving_review_count": 1 } },
    { "type": "non_fast_forward" }
  ]
}
EOF
```

If you see permission errors, use **Option A** or ask an org owner to enable rules.

## After enabling

- Default branch should remain **`main`**.
- All contributors create branches from `main` and open PRs.
