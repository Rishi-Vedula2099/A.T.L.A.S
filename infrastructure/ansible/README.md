# A.T.L.A.S — Ansible Operations Playbooks

Idempotent Ansible playbooks and roles for orchestrating prerequisites, deployment, upgrades, backups, and rollbacks across target server fleets.

## Directory Structure

```
infrastructure/ansible/
├── README.md
├── inventory.example.ini
├── ansible.cfg
├── group_vars/
│   ├── all.yml
│   ├── production.yml
│   └── staging.yml
├── playbooks/
│   ├── 00-prereqs.yml          # Install Docker & system dependencies
│   ├── 10-deploy.yml           # Render secrets & run docker compose up
│   ├── 20-upgrade.yml          # Pull new images, reload stack & verify health
│   ├── 30-backup.yml           # Trigger ad-hoc backup execution
│   └── 99-rollback.yml         # Revert stack to target image tag
├── roles/
│   ├── common/                 # Base package installation & OS tuning
│   ├── docker/                 # Docker Engine & Docker Compose plugin setup
│   └── atlas_deploy/           # Stack deployment, env rendering, healthcheck
└── templates/
    ├── docker-daemon.json.j2   # Docker daemon configuration template
    └── atlas.env.j2            # Environment variables template
```

## Quick Start

```bash
# Check syntax
ansible-playbook --syntax-check playbooks/00-prereqs.yml
ansible-playbook --syntax-check playbooks/10-deploy.yml

# Deploy prerequisites and stack
ansible-playbook -i inventory.example.ini playbooks/00-prereqs.yml
ansible-playbook -i inventory.example.ini playbooks/10-deploy.yml
```
