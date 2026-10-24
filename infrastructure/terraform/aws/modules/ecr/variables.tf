variable "name_prefix" { type = string }

variable "repository_names" {
  description = "Repository names (will be prefixed with name_prefix)."
  type        = list(string)
}

variable "image_tag_mutability" {
  type    = string
  default = "IMMUTABLE"
}

variable "tags" {
  type    = map(string)
  default = {}
}
