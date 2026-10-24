# A.T.L.A.S — Enterprise Deployment Guide

Guide for deploying A.T.L.A.S across Kubernetes (via raw manifests or Helm), Cloud Infrastructure (Terraform), and Ansible bare-metal/VM fleets.

---

## Option 1: Kubernetes Deployment (Manifests)

### Apply Order
Kubernetes resources should be applied in sequential numerical order:

```bash
kubectl apply -f infrastructure/kubernetes/00-namespace.yaml
kubectl apply -f infrastructure/kubernetes/01-configmaps.yaml
kubectl apply -f infrastructure/kubernetes/02-secrets.yaml
kubectl apply -f infrastructure/kubernetes/03-persistentvolumes.yaml
kubectl apply -f infrastructure/kubernetes/10-postgres-statefulset.yaml
kubectl apply -f infrastructure/kubernetes/11-redis-statefulset.yaml
kubectl apply -f infrastructure/kubernetes/12-neo4j-statefulset.yaml
kubectl apply -f infrastructure/kubernetes/13-qdrant-statefulset.yaml
kubectl apply -f infrastructure/kubernetes/14-minio-statefulset.yaml
kubectl apply -f infrastructure/kubernetes/20-backend-deployment.yaml
kubectl apply -f infrastructure/kubernetes/21-frontend-deployment.yaml
kubectl apply -f infrastructure/kubernetes/30-services.yaml
kubectl apply -f infrastructure/kubernetes/40-ingress.yaml
kubectl apply -f infrastructure/kubernetes/50-hpa.yaml
kubectl apply -f infrastructure/kubernetes/51-pdb.yaml
kubectl apply -f infrastructure/kubernetes/60-networkpolicies.yaml
```

---

## Option 2: Helm Chart Deployment

### Install / Upgrade via Helm

```bash
# Lint the chart
helm lint infrastructure/helm/atlas

# Install using enterprise defaults overlay
helm install atlas infrastructure/helm/atlas -f infrastructure/helm/atlas/values-enterprise.yaml -n atlas --create-namespace

# Upgrade release
helm upgrade atlas infrastructure/helm/atlas -f infrastructure/helm/atlas/values-enterprise.yaml -n atlas
```

---

## Option 3: Cloud Provisioning with Terraform

### AWS (EKS + RDS)
```bash
cd infrastructure/terraform/aws
terraform init
terraform plan
terraform apply
```

### Azure (AKS + PostgreSQL Flexible)
```bash
cd infrastructure/terraform/azure
terraform init
terraform plan
terraform apply
```

---

## Option 4: Ansible Fleet Management

```bash
cd infrastructure/ansible

# Install host prerequisites
ansible-playbook -i inventory.example.ini playbooks/00-prereqs.yml

# Deploy application stack
ansible-playbook -i inventory.example.ini playbooks/10-deploy.yml

# Perform zero-downtime upgrade
ansible-playbook -i inventory.example.ini playbooks/20-upgrade.yml

# Trigger ad-hoc backup
ansible-playbook -i inventory.example.ini playbooks/30-backup.yml
```
