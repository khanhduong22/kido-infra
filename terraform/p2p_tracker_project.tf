# --- P2P Tracker (Frontend + Worker on VPS) ---

resource "github_actions_secret" "p2p_vps_host" {
  repository      = "p2p-tracker"
  secret_name     = "VPS_HOST"
  plaintext_value = data.sops_file.secrets.data["shared_vps_host"]
}

resource "github_actions_secret" "p2p_ssh_user" {
  repository      = "p2p-tracker"
  secret_name     = "SSH_USER"
  plaintext_value = "root"
}

resource "github_actions_secret" "p2p_ssh_private_key" {
  repository      = "p2p-tracker"
  secret_name     = "SSH_PRIVATE_KEY"
  plaintext_value = file("~/.ssh/id_rsa")
}

resource "github_actions_secret" "p2p_vapid_public_key" {
  repository      = "p2p-tracker"
  secret_name     = "VAPID_PUBLIC_KEY"
  plaintext_value = data.sops_file.secrets.data["vapid_public_key"]
}

resource "github_actions_secret" "p2p_vapid_private_key" {
  repository      = "p2p-tracker"
  secret_name     = "VAPID_PRIVATE_KEY"
  plaintext_value = data.sops_file.secrets.data["vapid_private_key"]
}
