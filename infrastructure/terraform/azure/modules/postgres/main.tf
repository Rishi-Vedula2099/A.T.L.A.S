resource "random_password" "pg_pass" {
  length  = 24
  special = false
}

resource "azurerm_postgresql_flexible_server" "postgres" {
  name                   = "${var.name_prefix}-pg-server"
  resource_group_name    = var.resource_group_name
  location               = var.location
  version                = "16"
  delegated_subnet_id    = var.subnet_id
  administrator_login    = "atlas_admin"
  administrator_password = random_password.pg_pass.result
  sku_name               = var.sku_name
  storage_mb             = var.storage_mb

  backup_retention_days = 14
}

resource "azurerm_postgresql_flexible_server_database" "db" {
  name      = "atlas_db"
  server_id = azurerm_postgresql_flexible_server.postgres.id
  collation = "en_US.utf8"
  charset   = "utf8"
}
