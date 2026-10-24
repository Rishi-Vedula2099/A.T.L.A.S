output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "aks_cluster_name" {
  value = "${var.name_prefix}-${var.environment}-aks"
}

output "postgres_fqdn" {
  value = module.postgres.server_fqdn
}

output "acr_login_server" {
  value = module.acr.login_server
}

output "app_gateway_public_ip" {
  value = module.app_gateway.public_ip
}

output "key_vault_uri" {
  value = module.keyvault.vault_uri
}
