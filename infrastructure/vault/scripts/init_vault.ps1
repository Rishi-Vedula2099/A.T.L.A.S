# HashiCorp Vault Windows PowerShell setup helper
$ErrorActionPreference = "Stop"
$env:VAULT_ADDR = if ($env:VAULT_ADDR) { $env:VAULT_ADDR } else { "http://localhost:8200" }

Write-Host "[vault-init] Initializing Vault KV secrets engine..."
vault secrets enable -path=secret kv-v2

Write-Host "[vault-init] Writing default ATLAS secrets..."
vault kv put secret/atlas/database password=atlas_secure_pass
vault kv put secret/atlas/jwt secret=atlas_jwt_secret_key

Write-Host "[vault-init] Enabling AppRole auth..."
vault auth enable approle
Write-Host "[vault-init] Vault initialization complete."
