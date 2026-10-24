variable "location" {
  description = "Azure region for resource deployment."
  type        = string
  default     = "eastus"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)."
  type        = string
  default     = "prod"
}

variable "name_prefix" {
  description = "Prefix used for naming Azure resources."
  type        = string
  default     = "atlas"
}

variable "vnet_cidr" {
  description = "Address space for the Virtual Network."
  type        = string
  default     = "10.100.0.0/16"
}

variable "aks_node_count" {
  description = "Number of worker nodes in default node pool."
  type        = number
  default     = 3
}

variable "aks_vm_size" {
  description = "VM SKU for AKS node pool."
  type        = string
  default     = "Standard_D4s_v5"
}

variable "postgres_sku_name" {
  description = "SKU for Azure Database for PostgreSQL Flexible Server."
  type        = string
  default     = "GP_Standard_D2s_v3"
}

variable "postgres_storage_mb" {
  description = "Allocated storage size for PostgreSQL in MB."
  type        = number
  default     = 131072 # 128 GiB
}

variable "domain_name" {
  description = "Base domain name for Azure DNS zone."
  type        = string
  default     = "atlas.example.com"
}
