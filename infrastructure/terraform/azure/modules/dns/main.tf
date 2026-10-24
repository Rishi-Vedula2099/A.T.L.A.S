resource "azurerm_dns_zone" "zone" {
  name                = var.domain_name
  resource_group_name = var.resource_group_name
}

resource "azurerm_dns_a_record" "root" {
  name                = "@"
  zone_name           = azurerm_dns_zone.zone.name
  resource_group_name = var.resource_group_name
  ttl                 = 300
  records             = [var.target_ip]
}
