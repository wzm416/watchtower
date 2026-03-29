terraform {
  required_version = ">= 1.6"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }

  # Uncomment after creating a GCS bucket for state:
  # backend "gcs" {
  #   bucket = "your-tf-state-bucket"
  #   prefix = "watchtower/staging"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ---------------------------------------------------------------------------
# Scaffold only: enable APIs and document next steps. Un-comment and extend
# with Cloud SQL, Cloud Run resources, IAM, and Scheduler when images exist.
# ---------------------------------------------------------------------------

resource "google_project_service" "run" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "sqladmin" {
  service            = "sqladmin.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "secretmanager" {
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloudscheduler" {
  service            = "cloudscheduler.googleapis.com"
  disable_on_destroy = false
}

output "enabled_apis_note" {
  value = "APIs enabled for Cloud Run, Cloud SQL Admin, Secret Manager, Scheduler. Add modules for actual resources."
}
