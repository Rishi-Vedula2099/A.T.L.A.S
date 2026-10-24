variable "resource_group_name" {
  type        = string
  description = "Resource group name."
}

variable "location" {
  type        = string
  description = "Azure region."
}

variable "name_prefix" {
  type        = string
  description = "Prefix for resources."
}

variable "vnet_cidr" {
  type        = string
  description = "Virtual network address space."
}
