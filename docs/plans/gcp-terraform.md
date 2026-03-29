# GCP + Terraform (baseline)

This repo includes a **starter Terraform layout** under `terraform/` for reproducible infrastructure. It is **not** a complete production module set: you still choose project, region, and wire secrets.

## What to declare (v1 target)

| Resource | Role |
|----------|------|
| **Cloud SQL (Postgres)** | Primary database; private IP optional later |
| **Cloud Run** (`api`, `web`) | Containers; min instances 0 OK for MVP |
| **Secret Manager** | `DATABASE_URL`, `GOOGLE_CLIENT_IDS`, `CRON_BEARER_TOKEN`, `RESEND_API_KEY`, … |
| **Cloud Scheduler** | `POST` to `/internal/jobs/tick?limit=20` with **Bearer** token (or OIDC later) |
| **IAM** | Scheduler SA → `run.invoker` on API service |
| **Artifact Registry** | Store API/web images |

## State backend

Use a **GCS** bucket (or Terraform Cloud) for remote state. Do **not** commit `terraform.tfstate`.

Example backend block (create bucket first):

```hcl
terraform {
  backend "gcs" {
    bucket = "YOUR_TF_STATE_BUCKET"
    prefix = "watchtower/staging"
  }
}
```

## Layout

- `terraform/environments/staging/` — example entrypoint wiring variables
- `terraform/modules/` — grow over time (Cloud SQL, Cloud Run service, Scheduler job)

## Apply (high level)

1. `gcloud auth application-default login` (or workload identity in CI).
2. Set `project_id`, `region`, image URIs, and secrets in `tfvars` (not committed).
3. `terraform init && terraform plan && terraform apply`.

## Runtime env (API)

Mirror `api/.env.example`: `DATABASE_URL`, `GOOGLE_CLIENT_IDS`, `CRON_BEARER_TOKEN`, optional `RESEND_API_KEY` / `RESEND_FROM_EMAIL`, `APP_PUBLIC_URL`, `CORS_ORIGINS` (production web origin).

## OIDC vs Bearer for Scheduler

v1 API uses **Bearer `CRON_BEARER_TOKEN`** on `POST /internal/jobs/tick`. For stricter GCP-native auth, add **OIDC token verification** in the API and grant Scheduler’s service account `roles/run.invoker` (see `TODOS.md` TODO-4).
