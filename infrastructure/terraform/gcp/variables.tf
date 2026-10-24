variable "project_id" {
  description = "GCP Project ID."
  type        = string
  default     = "atlas-gcp-project"
}

variable "region" {
  description = "GCP region."
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)."
  type        = string
  default     = "prod"
}

variable "name_prefix" {
  description = "Prefix for GCP resources."
  type        = string
  default     = "atlas"
}

variable "vpc_cidr" {
  description = "Primary CIDR block for subnetwork."
  type        = string
  default     = "10.200.0.0/16"
}

variable "gke_node_count" {
  description = "Initial worker node count per zone."
  type        = number
  default     = 3
}

variable "db_tier" {
  description = "Cloud SQL tier specification."
  type        = string
  default     = "db-custom-2-7680"
}
