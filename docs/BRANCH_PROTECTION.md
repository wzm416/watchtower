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

If your token has `admin` scope on the repo, you can apply protection via API.

**Do not paste angle brackets** like `<owner>/<repo>` in zsh: `<` starts **input redirection**, so the shell tries to open a file named `owner` and fails with `no such file or directory: owner`. Use your real repo path instead, e.g. `repos/wzm416/watchtower`.

The **pull_request** rule must include the **full** `parameters` object (GitHub returns `422` if fields are missing). Example:

```bash
gh api repos/wzm416/watchtower/rulesets --method POST --input - <<'EOF'
{
  "name": "protect-main",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["refs/heads/main"],
      "exclude": []
    }
  },
  "rules": [
    {
      "type": "pull_request",
      "parameters": {
        "allowed_merge_methods": ["merge", "squash", "rebase"],
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_approving_review_count": 1,
        "required_review_thread_resolution": false
      }
    },
    { "type": "non_fast_forward" }
  ]
}
EOF
```

Replace `wzm416/watchtower` with `YOUR_GITHUB_USER/YOUR_REPO` (no `<` `>`).

If you see permission errors, use **Option A** or ask an org owner to enable rules.

## After enabling

- Default branch should remain **`main`**.
- All contributors create branches from `main` and open PRs.
