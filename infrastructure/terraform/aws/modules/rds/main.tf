locals {
  tags = merge({ Layer = "rds" }, var.tags)
}

# Random master password, stored in Secrets Manager. The cluster module fetches
# it via the secret ARN in outputs.tf.
resource "random_password" "master" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_security_group" "postgres" {
  name        = "${var.name_prefix}-${var.environment}-postgres"
  description = "Postgres ingress for A.T.L.A.S"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = toset([5432])
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = var.allowed_ingress_cidrs
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

resource "aws_db_subnet_group" "this" {
  name       = "${var.name_prefix}-${var.environment}"
  subnet_ids = var.subnet_ids
  tags       = local.tags
}

resource "aws_db_parameter_group" "this" {
  name   = "${var.name_prefix}-${var.environment}-pg16"
  family = "postgres16"

  parameter {
    name         = "log_connections"
    value        = "1"
    apply_method = "immediate"
  }

  parameter {
    name         = "log_min_duration_statement"
    value        = "1000" # log queries slower than 1s
    apply_method = "immediate"
  }

  tags = local.tags
}

resource "aws_db_instance" "this" {
  identifier = "${var.name_prefix}-${var.environment}-postgres"

  engine            = "postgres"
  engine_version    = "16.3"
  instance_class    = var.instance_class
  allocated_storage = var.allocated_storage
  storage_type      = "gp3"
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn

  db_name  = var.db_name
  username = var.username
  password = random_password.master.result
  multi_az = var.multi_az

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.postgres.id]
  parameter_group_name   = aws_db_parameter_group.this.name

  backup_retention_period  = 14
  backup_window            = "03:00-04:00"
  maintenance_window       = "sun:04:30-sun:05:30"
  copy_tags_to_snapshot    = true
  deletion_protection      = var.environment == "prod" || var.environment == "enterprise"
  delete_automated_backups = var.environment != "prod" && var.environment != "enterprise"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = local.tags
}

resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS at-rest encryption"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  tags                    = local.tags
}

# Secrets Manager — store the master password for retrieval by the backend.
resource "aws_secretsmanager_secret" "postgres" {
  name                    = "/atlas/${var.environment}/postgres/master"
  description             = "Master credentials for the A.T.L.A.S RDS Postgres."
  kms_key_id              = aws_kms_key.rds.arn
  recovery_window_in_days = 30
  tags                    = local.tags
}

resource "aws_secretsmanager_secret_version" "postgres" {
  secret_id = aws_secretsmanager_secret.postgres.id
  secret_string = jsonencode({
    username = var.username
    password = random_password.master.result
    host     = aws_db_instance.this.address
    port     = aws_db_instance.this.port
    dbname   = var.db_name
    engine   = "postgres"
  })
}
