# ==============================================================================
# A.T.L.A.S — AWS top-level orchestration
# ==============================================================================
# Wires the modules together. Each module is self-contained and exposes its
# outputs via outputs.tf.
# ==============================================================================

module "networking" {
  source = "./modules/networking"

  name_prefix        = var.name_prefix
  environment        = var.environment
  region             = var.region
  vpc_cidr           = var.vpc_cidr
  availability_zones = length(var.availability_zones) > 0 ? var.availability_zones : null
  enable_nat_gateway = true
  single_nat_gateway = var.environment == "dev" # save cost in dev
  tags               = var.tags
}

module "ecr" {
  source = "./modules/ecr"

  name_prefix      = var.name_prefix
  repository_names = ["atlas-backend", "atlas-frontend", "atlas-backup"]
  tags             = var.tags
}

module "iam" {
  source = "./modules/iam"

  name_prefix   = var.name_prefix
  account_id    = module.networking.account_id
  region        = var.region
  ecr_repo_arns = module.ecr.repository_arns
  tags          = var.tags
}

module "eks" {
  source = "./modules/eks"

  name_prefix              = var.name_prefix
  environment              = var.environment
  kubernetes_version       = var.eks_kubernetes_version
  vpc_id                   = module.networking.vpc_id
  subnet_ids               = module.networking.private_subnet_ids
  control_plane_subnet_ids = module.networking.intra_subnet_ids
  node_instance_type       = var.eks_node_instance_type
  node_gpu_instance_type   = var.eks_node_gpu_instance_type
  node_desired_size        = var.eks_node_desired_size
  enable_gpu               = var.enable_gpu
  tags                     = var.tags
}

module "rds" {
  source = "./modules/rds"

  name_prefix           = var.name_prefix
  environment           = var.environment
  vpc_id                = module.networking.vpc_id
  subnet_ids            = module.networking.database_subnet_ids
  allowed_ingress_cidrs = [module.networking.vpc_cidr]
  instance_class        = var.rds_instance_class
  allocated_storage     = var.rds_allocated_storage
  multi_az              = var.rds_multi_az
  tags                  = var.tags
}

module "alb" {
  source = "./modules/alb"

  name_prefix   = var.name_prefix
  environment   = var.environment
  vpc_id        = module.networking.vpc_id
  subnet_ids    = module.networking.public_subnet_ids
  backend_port  = 80
  frontend_port = 80
  tags          = var.tags
}

module "route53" {
  source = "./modules/route53"

  domain_name       = var.domain_name
  frontend_hostname = var.frontend_hostname
  backend_hostname  = var.backend_hostname
  alb_dns_name      = module.alb.alb_dns_name
  alb_zone_id       = module.alb.alb_zone_id
  tags              = var.tags
}
