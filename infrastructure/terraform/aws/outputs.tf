output "vpc_id" {
  description = "ID of the created VPC."
  value       = module.networking.vpc_id
}

output "vpc_cidr" {
  value = module.networking.vpc_cidr
}

output "public_subnet_ids" {
  value = module.networking.public_subnet_ids
}

output "private_subnet_ids" {
  value = module.networking.private_subnet_ids
}

output "database_subnet_ids" {
  value = module.networking.database_subnet_ids
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "API endpoint of the EKS cluster."
  value       = module.eks.cluster_endpoint
  sensitive   = true
}

output "eks_cluster_ca_data" {
  description = "Base64-encoded CA data for the EKS cluster."
  value       = module.eks.cluster_ca_data
  sensitive   = true
}

output "rds_endpoint" {
  description = "RDS Postgres writer endpoint."
  value       = module.rds.endpoint
}

output "rds_connection_string" {
  description = "psql connection string (password masked — get from Secrets Manager)."
  value       = "postgresql://${module.rds.username}:<password>@${module.rds.endpoint}:${module.rds.port}/${module.rds.db_name}?sslmode=require"
  sensitive   = true
}

output "rds_secret_arn" {
  description = "Secrets Manager ARN holding the RDS master password."
  value       = module.rds.secret_arn
}

output "ecr_repository_urls" {
  description = "ECR push/pull URLs per image."
  value       = module.ecr.repository_urls
}

output "alb_dns_name" {
  value = module.alb.alb_dns_name
}

output "frontend_url" {
  value = "https://${module.route53.frontend_fqdn}"
}

output "backend_url" {
  value = "https://${module.route53.backend_fqdn}"
}
