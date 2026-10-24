data "aws_availability_zones" "available" {
  count = var.availability_zones == null ? 1 : 0
  state = "available"
}

locals {
  azs = coalesce(var.availability_zones, data.aws_availability_zones.available[0].names)

  tags = merge({
    Environment = var.environment
    Layer       = "networking"
  }, var.tags)
}

# VPC -----------------------------------------------------------------------
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.8.0"

  name = "${var.name_prefix}-${var.environment}"
  cidr = var.vpc_cidr

  azs = local.azs

  # Subnets — three tiers.
  # - public:   ALB + NAT gateways
  # - private:  EKS worker nodes (no direct internet egress path)
  # - intra:    EKS control plane ENIs + resources with no internet route
  # - database: RDS (private, dedicated route table)
  public_subnets   = [for k, v in local.azs : cidrsubnet(var.vpc_cidr, 4, k)]
  private_subnets  = [for k, v in local.azs : cidrsubnet(var.vpc_cidr, 4, k + 10)]
  intra_subnets    = [for k, v in local.azs : cidrsubnet(var.vpc_cidr, 4, k + 20)]
  database_subnets = [for k, v in local.azs : cidrsubnet(var.vpc_cidr, 4, k + 30)]

  create_database_subnet_group = true

  enable_nat_gateway   = var.enable_nat_gateway
  single_nat_gateway   = var.single_nat_gateway
  enable_dns_hostnames = true
  enable_dns_support   = true

  public_subnet_tags   = { Tier = "public" }
  private_subnet_tags  = { Tier = "private", "kubernetes.io/role/elb" = "1" }
  intra_subnet_tags    = { Tier = "intra" }
  database_subnet_tags = { Tier = "database" }

  tags = local.tags
}

# VPC flow logs (S3 destination) — keep at least 30d for incident review.
resource "aws_flow_log" "atlas" {
  log_destination      = aws_s3_bucket.flow_log.arn
  log_destination_type = "s3"
  traffic_type         = "ALL"
  vpc_id               = module.vpc.vpc_id
  tags                 = local.tags
}

resource "aws_s3_bucket" "flow_log" {
  bucket_prefix = "${var.name_prefix}-${var.environment}-flowlogs-"
  tags          = local.tags
}

resource "aws_s3_bucket_lifecycle_configuration" "flow_log" {
  bucket = aws_s3_bucket.flow_log.id

  rule {
    id     = "expire-30d"
    status = "Enabled"
    expiration { days = 30 }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "flow_log" {
  bucket = aws_s3_bucket.flow_log.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

# Default security group — lock everything down by default.
resource "aws_default_security_group" "default" {
  vpc_id = module.vpc.vpc_id
}
