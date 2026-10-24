output "cluster_name" {
  value = module.eks.cluster_name
}

output "cluster_endpoint" {
  value     = module.eks.cluster_endpoint
  sensitive = true
}

output "cluster_ca_data" {
  value     = module.eks.cluster_certificate_authority_data
  sensitive = true
}

output "cluster_iam_role_arn" {
  value = module.eks.cluster_iam_role_arn
}
