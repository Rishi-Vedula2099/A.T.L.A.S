# HashiCorp Vault Agent Sidecar Config
exit_after_auth = false
pid_file = "/tmp/agent.pid"

auto_auth {
  method "approle" {
    mount_path = "auth/approle"
    config = {
      role_id_file_path = "/etc/vault/roleid"
      secret_id_file_path = "/etc/vault/secretid"
      remove_secret_id_file_after_reading = false
    }
  }
}

template {
  contents = "{{ with secret \"secret/data/atlas/database\" }}{{ .Data.data.password }}{{ end }}"
  destination = "/run/secrets/postgres_password"
}

template {
  contents = "{{ with secret \"secret/data/atlas/jwt\" }}{{ .Data.data.secret }}{{ end }}"
  destination = "/run/secrets/jwt_secret"
}
