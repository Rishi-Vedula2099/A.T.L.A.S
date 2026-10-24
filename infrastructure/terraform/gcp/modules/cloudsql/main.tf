resource "random_password" "db_password" {
  length  = 24
  special = false
}

resource "google_sql_database_instance" "instance" {
  name             = "${var.name_prefix}-pg-instance"
  region           = var.region
  database_version = "POSTGRES_16"
  project          = var.project_id

  settings {
    tier = var.db_tier
    ip_configuration {
      ipv4_enabled = true
    }
  }
}

resource "google_sql_database" "database" {
  name     = "atlas_db"
  instance = google_sql_database_instance.instance.name
  project  = var.project_id
}

resource "google_sql_user" "users" {
  name     = "atlas_admin"
  instance = google_sql_database_instance.instance.name
  password = random_password.db_password.result
  project  = var.project_id
}
