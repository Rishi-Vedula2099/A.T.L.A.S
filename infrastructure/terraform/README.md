# A.T.L.A.S — Infrastructure as Code (Terraform)

This directory contains modularized Terraform IaC configurations for provisioning enterprise infrastructure across public clouds.

## Directory Structure

```
infrastructure/terraform/
├── README.md
├── aws/
│   ├── versions.tf            # Terraform & AWS provider requirements
│   ├── providers.tf           # AWS provider configuration
│   ├── variables.tf           # Input variables
│   ├── main.tf                # Module orchestration
│   ├── outputs.tf             # Outputs (VPC, EKS, RDS, ECR, etc.)
│   ├── backend.tf.example     # S3 + DynamoDB state locking template
│   └── modules/
│       ├── networking/        # VPC, subnets, IGW, NAT
│       ├── eks/               # EKS cluster, node groups, IRSA
│       ├── rds/               # RDS PostgreSQL instance
│       ├── ecr/               # ECR repositories
│       ├── alb/               # Application Load Balancer
│       ├── route53/           # DNS zone & certs
│       └── iam/               # IAM roles & policies
├── azure/
│   ├── versions.tf            # Terraform & AzureRM provider requirements
│   ├── providers.tf           # Azure provider configuration
│   ├── variables.tf           # Input variables
│   ├── main.tf                # Module orchestration
│   ├── outputs.tf             # Outputs (VNet, AKS, Postgres, ACR, AppGW, KV)
│   ├── backend.tf.example     # Azure Storage state backend template
│   └── modules/
│       ├── networking/        # Virtual Network, subnets, NSGs
│       ├── aks/               # Azure Kubernetes Service cluster
│       ├── postgres/          # Azure Database for PostgreSQL Flexible Server
│       ├── acr/               # Azure Container Registry
│       ├── app-gateway/       # Application Gateway WAF & TLS
│       ├── dns/               # Azure DNS zone
│       └── keyvault/          # Azure Key Vault secrets
└── gcp/
    └── README.md              # Stub for future GCP session
```

## Quick Start

### AWS Deployment
```bash
cd infrastructure/terraform/aws
terraform init
terraform plan
terraform apply
```

### Azure Deployment
```bash
cd infrastructure/terraform/azure
terraform init
terraform plan
terraform apply
```
