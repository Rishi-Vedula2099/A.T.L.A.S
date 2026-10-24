output "frontend_fqdn" {
  value = aws_route53_record.frontend.name
}

output "backend_fqdn" {
  value = aws_route53_record.backend.name
}

output "certificate_arn" {
  value = aws_acm_certificate.this.arn
}
