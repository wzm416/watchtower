variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region (e.g. us-central1)"
  type        = string
  default     = "us-central1"
}

variable "api_image" {
  description = "Container image URI for the API (Artifact Registry or GCR)"
  type        = string
  default     = "REPLACE_ME"
}

variable "web_image" {
  description = "Container image URI for the static/web service (if using SSR container)"
  type        = string
  default     = "REPLACE_ME"
}
