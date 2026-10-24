variable "name_prefix" { type = string }
variable "account_id" { type = string }
variable "region" { type = string }

variable "ecr_repo_arns" {
  description = "ECR repository ARNs the deploy role can push/pull."
  type        = map(string)
}

variable "tags" {
  type    = map(string)
  default = {}
}
