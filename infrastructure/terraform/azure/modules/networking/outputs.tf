output "vnet_id" {
  value = azurerm_virtual_network.vnet.id
}

output "vnet_name" {
  value = azurerm_virtual_network.vnet.name
}

output "aks_subnet_id" {
  value = azurerm_subnet.aks_subnet.id
}

output "postgres_subnet_id" {
  value = azurerm_subnet.postgres_subnet.id
}

output "appgw_subnet_id" {
  value = azurerm_subnet.appgw_subnet.id
}
