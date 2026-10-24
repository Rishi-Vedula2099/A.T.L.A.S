resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "${var.name_prefix}-repo"
  description   = "ATLAS container images repository"
  format        = "DOCKER"
  project       = var.project_id
}
