# ==============================================================================
# Top-level AWS variables
# ==============================================================================

variable "region" {
  description = "AWS region for all resources."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (dev | staging | prod | enterprise)."
  type        = string
  default     = "prod"
  validation {
    condition     = contains(["dev", "staging", "prod", "enterprise"], var.environment)
    error_message = "environment must be one of dev|staging|prod|enterprise."
  }
}

variable "name_prefix" {
  description = "Prefix for resource names (kept short — AWS has name length limits)."
  type        = string
  default     = "atlas"
}

variable "vpc_cidr" {
  description = "CIDR for the VPC."
  type        = string
  default     = "10.30.0.0/16"
}

variable "availability_zones" {
  description = "AZs to spread across. Defaults to 3 in the region."
  type        = list(string)
  default     = []
}

variable "eks_kubernetes_version" {
  description = "EKS Kubernetes version."
  type        = string
  default     = "1.30"
}

variable "eks_node_instance_type" {
  description = "Instance type for EKS general-purpose node group."
  type        = string
  default     = "m6i.large"
}

variable "eks_node_gpu_instance_type" {
  description = "Instance type for EKS GPU node group (only used when enable_gpu=true)."
  type        = string
  default     = "g5.xlarge"
}

variable "eks_node_desired_size" {
  description = "Desired number of general-purpose nodes."
  type        = number
  default     = 3
}

variable "enable_gpu" {
  description = "Provision a GPU node group."
  type        = bool
  default     = false
}

variable "rds_instance_class" {
  description = "RDS Postgres instance class."
  type        = string
  default     = "db.r6g.large"
}

variable "rds_allocated_storage" {
  description = "RDS allocated storage in GB."
  type        = number
  default     = 100
}

variable "rds_multi_az" {
  description = "Run RDS in Multi-AZ for HA."
  type        = bool
  default     = true
}

variable "domain_name" {
  description = "Root domain name (must already exist as a Route53 hosted zone, or be delegated)."
  type        = string
  default     = "atlas.example.com"
}

variable "frontend_hostname" {
  description = "Frontend hostname (under domain_name)."
  type        = string
  default     = "atlas"
}

variable "backend_hostname" {
  description = "Backend hostname (under domain_name)."
  type        = string
  default     = "api"
}

variable "tags" {
  description = "Additional tags merged into every resource."
  type        = map(string)
  default     = {}
}
