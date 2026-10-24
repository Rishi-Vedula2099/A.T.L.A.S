output "appgw_id" {
  value = azurerm_application_gateway.appgw.id
}

output "public_ip" {
  value = azurerm_public_ip.pip.ip_address
}
