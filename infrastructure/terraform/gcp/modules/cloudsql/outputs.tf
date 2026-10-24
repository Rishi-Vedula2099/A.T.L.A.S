output "connection_name" {
  value = google_sql_database_instance.instance.connection_name
}

output "public_ip" {
  value = google_sql_database_instance.instance.public_ip_address
}

output "password" {
  value     = random_password.db_password.result
  sensitive = true
}
