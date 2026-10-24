output "vpc_id" {
  value = module.vpc.vpc_id
}

output "vpc_cidr" {
  value = var.vpc_cidr
}

output "public_subnet_ids" {
  value = module.vpc.public_subnets
}

output "private_subnet_ids" {
  value = module.vpc.private_subnets
}

output "intra_subnet_ids" {
  value = module.vpc.intra_subnets
}

output "database_subnet_ids" {
  value = module.vpc.database_subnets
}

output "account_id" {
  value = module.vpc.vpc_owner_id
}
