output "server_fqdn" {
  value = azurerm_postgresql_flexible_server.postgres.fqdn
}

output "admin_password" {
  value     = random_password.pg_pass.result
  sensitive = true
}

output "database_name" {
  value = azurerm_postgresql_flexible_server_database.db.name
}
