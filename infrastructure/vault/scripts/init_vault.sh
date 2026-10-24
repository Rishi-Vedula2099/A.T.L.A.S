#!/usr/bin/env bash
set -euo pipefail

VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
export VAULT_ADDR

echo "[vault-init] Initializing Vault KV secrets engine and policies..."
vault secrets enable -path=secret kv-v2 || true

echo "[vault-init] Writing default ATLAS secrets..."
vault kv put secret/atlas/database password="${POSTGRES_PASSWORD:-atlas_secure_pass}"
vault kv put secret/atlas/jwt secret="${JWT_SECRET:-atlas_jwt_secret_key}"

echo "[vault-init] Enabling AppRole authentication..."
vault auth enable approle || true

echo "[vault-init] Creating ATLAS application policy..."
vault policy write atlas-policy - <<EOF
path "secret/data/atlas/*" {
  capabilities = ["read"]
}
EOF

vault write auth/approle/role/atlas-role policies="atlas-policy" token_ttl=1h token_max_ttl=4h
echo "[vault-init] Vault initialization complete."
