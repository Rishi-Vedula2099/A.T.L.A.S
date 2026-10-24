locals {
  tags = merge({ Layer = "iam" }, var.tags)
}

# ---------------------------------------------------------------------------
# CI/CD deploy role — assumed by GitHub Actions via OIDC.
# ---------------------------------------------------------------------------
data "aws_iam_openid_connect_provider" "github" {
  count = 0 # opt-in: create a github OIDC provider and bump count to 1.
  url   = "https://token.actions.githubusercontent.com"
}

resource "aws_iam_role" "atlas_deploy" {
  name = "${var.name_prefix}-deploy"

  description = "CI/CD role assumed by GitHub Actions to push images and deploy to EKS."

  # IMPORTANT: replace with a real OIDC trust policy in production.
  # The placeholder below denies all assume-role; it exists so `terraform apply`
  # succeeds without leaking a real trust anchor.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Deny"
      Principal = { Service = "codepipeline.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = local.tags
}

resource "aws_iam_role_policy" "deploy_ecr" {
  name = "${var.name_prefix}-deploy-ecr"
  role = aws_iam_role.atlas_deploy.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ecr:GetAuthorizationToken"]
        Resource = ["*"]
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetRepositoryPolicy",
          "ecr:DescribeRepositories",
          "ecr:DescribeImages",
          "ecr:BatchGetImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage"
        ]
        Resource = values(var.ecr_repo_arns)
      }
    ]
  })
}

# ---------------------------------------------------------------------------
# Backup role — used by the atlas-backup container via IRSA.
# ---------------------------------------------------------------------------
resource "aws_iam_role" "atlas_backup" {
  name        = "${var.name_prefix}-backup"
  description = "Assumed by atlas-backup pods to push encrypted dumps to S3 (or MinIO backup of last resort)."

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      # Real IRSA trust is created by the EKS module; placeholder here.
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = local.tags
}

resource "aws_iam_role_policy" "backup_s3" {
  name = "${var.name_prefix}-backup-s3"
  role = aws_iam_role.atlas_backup.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:ListBucket", "s3:GetObject", "s3:PutObject", "s3:DeleteObject"
      ]
      Resource = [
        "arn:aws:s3:::${var.name_prefix}-backups",
        "arn:aws:s3:::${var.name_prefix}-backups/*",
      ]
    }]
  })
}
