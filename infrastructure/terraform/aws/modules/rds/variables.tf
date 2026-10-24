variable "name_prefix" { type = string }
variable "environment" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }

variable "allowed_ingress_cidrs" {
  description = "CIDRs allowed to reach Postgres on 5432. Default to VPC CIDR."
  type        = list(string)
}

variable "instance_class" {
  type    = string
  default = "db.r6g.large"
}

variable "allocated_storage" {
  type    = number
  default = 100
}

variable "multi_az" {
  type    = bool
  default = true
}

variable "db_name" {
  type    = string
  default = "atlas_db"
}

variable "username" {
  type    = string
  default = "atlas_admin"
}

variable "tags" {
  type    = map(string)
  default = {}
}
