resource "azurerm_resource_group" "rg" {
  name     = "${var.name_prefix}-${var.environment}-rg"
  location = var.location
}

module "networking" {
  source              = "./modules/networking"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  name_prefix         = "${var.name_prefix}-${var.environment}"
  vnet_cidr           = var.vnet_cidr
}

module "aks" {
  source              = "./modules/aks"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  name_prefix         = "${var.name_prefix}-${var.environment}"
  subnet_id           = module.networking.aks_subnet_id
  node_count          = var.aks_node_count
  vm_size             = var.aks_vm_size
}

module "postgres" {
  source              = "./modules/postgres"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  name_prefix         = "${var.name_prefix}-${var.environment}"
  subnet_id           = module.networking.postgres_subnet_id
  sku_name            = var.postgres_sku_name
  storage_mb          = var.postgres_storage_mb
}

module "acr" {
  source              = "./modules/acr"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  name_prefix         = "${var.name_prefix}-${var.environment}"
}

module "app_gateway" {
  source              = "./modules/app-gateway"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  name_prefix         = "${var.name_prefix}-${var.environment}"
  subnet_id           = module.networking.appgw_subnet_id
}

module "dns" {
  source              = "./modules/dns"
  resource_group_name = azurerm_resource_group.rg.name
  domain_name         = var.domain_name
  target_ip           = module.app_gateway.public_ip
}

module "keyvault" {
  source              = "./modules/keyvault"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  name_prefix         = "${var.name_prefix}-${var.environment}"
}
