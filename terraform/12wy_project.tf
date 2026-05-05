# --- 12 Week Year Backend ---

resource "github_repository" "wy_api" {
  name        = "12-week-year-api"
  description = "Backend API for 12 Week Year Dashboard"
  visibility  = "private"
  auto_init   = false
}

resource "github_actions_secret" "api_vps_ip" {
  repository      = github_repository.wy_api.name
  secret_name     = "VPS_IP"
  plaintext_value = data.sops_file.secrets.data["shared_vps_host"]
}

resource "github_actions_secret" "api_ssh_user" {
  repository      = github_repository.wy_api.name
  secret_name     = "SSH_USER"
  plaintext_value = "root"
}

resource "github_actions_secret" "api_ssh_private_key" {
  repository      = github_repository.wy_api.name
  secret_name     = "SSH_PRIVATE_KEY"
  plaintext_value = file("~/.ssh/id_rsa")
}
