output "endpoint" {
  value = aws_db_instance.this.address
}

output "port" {
  value = aws_db_instance.this.port
}

output "username" {
  value = aws_db_instance.this.username
}

output "db_name" {
  value = aws_db_instance.this.db_name
}

output "secret_arn" {
  value = aws_secretsmanager_secret.postgres.arn
}
