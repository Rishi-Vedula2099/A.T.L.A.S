output "deploy_role_arn" {
  value = aws_iam_role.atlas_deploy.arn
}

output "backup_role_arn" {
  value = aws_iam_role.atlas_backup.arn
}
