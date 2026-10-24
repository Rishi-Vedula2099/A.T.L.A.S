variable "name_prefix" { type = string }
variable "environment" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }

variable "backend_port" {
  type    = number
  default = 80
}

variable "frontend_port" {
  type    = number
  default = 80
}

variable "health_check_path" {
  type    = string
  default = "/healthz"
}

variable "tags" {
  type    = map(string)
  default = {}
}
