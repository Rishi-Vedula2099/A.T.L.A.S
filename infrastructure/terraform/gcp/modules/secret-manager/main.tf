resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "${var.name_prefix}-jwt-secret"
  project   = var.project_id

  replication {
    auto {}
  }
}
