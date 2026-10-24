# A.T.L.A.S — GCP Terraform IaC

Full Google Cloud Platform (GCP) IaC deployment modules for A.T.L.A.S.

## Architecture

- **VPC & Subnets:** Custom VPC with private subnets, Router, and Cloud NAT gateway.
- **GKE Cluster:** Google Kubernetes Engine regional cluster with node pools.
- **Cloud SQL:** Managed PostgreSQL 16 database instance.
- **Artifact Registry:** Docker container registry for ATLAS images.
- **Secret Manager:** GCP Secret Manager for credentials.

## Deployment

```bash
cd infrastructure/terraform/gcp
terraform init
terraform plan
terraform apply
```
