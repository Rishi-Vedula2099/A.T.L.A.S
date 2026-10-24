variable "name_prefix" { type = string }
variable "environment" { type = string }
variable "kubernetes_version" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }
variable "control_plane_subnet_ids" { type = list(string) }

variable "node_instance_type" {
  type    = string
  default = "m6i.large"
}

variable "node_gpu_instance_type" {
  type    = string
  default = "g5.xlarge"
}

variable "node_desired_size" {
  type    = number
  default = 3
}

variable "enable_gpu" {
  type    = bool
  default = false
}

variable "tags" {
  type    = map(string)
  default = {}
}
