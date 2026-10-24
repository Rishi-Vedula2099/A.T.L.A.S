output "secret_id" {
  value = google_secret_manager_secret.jwt_secret.secret_id
}
