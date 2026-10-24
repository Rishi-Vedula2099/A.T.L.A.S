variable "name_prefix" {
  type = string
}

variable "environment" {
  type = string
}

variable "region" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

variable "availability_zones" {
  description = "Optional list of AZs. If null, 3 AZs in the region are picked."
  type        = list(string)
  default     = null
}

variable "enable_nat_gateway" {
  type    = bool
  default = true
}

variable "single_nat_gateway" {
  description = "Save cost in dev by provisioning one NAT gateway."
  type        = bool
  default     = false
}

variable "tags" {
  type    = map(string)
  default = {}
}
