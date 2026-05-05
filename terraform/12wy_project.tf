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

# --- 12 Week Year Dashboard (Frontend on Vercel) ---
# NOTE: The Vercel API token in SOPS lacks permissions for the Team 'kidos-projects-f7b57ed5'.
# Until a Team-scoped token is generated and updated in SOPS, this project is managed manually via Vercel CLI.
#
# resource "vercel_project" "wy_dashboard" {
#   name      = "12-week-year-dashboard"
#   team_id   = "team_Sf4YHziZbXR2cc11baVuMzLX"
#   framework = "nextjs"
#
#   git_repository = {
#     type = "github"
#     repo = "khanhduong22/12-week-year-dashboard"
#   }
#
#   environment = [
#     {
#       key    = "NEXT_PUBLIC_API_URL"
#       value  = "https://12wy-api.khanhdp.com"
#       target = ["production", "preview", "development"]
#     },
#     {
#       key    = "NEXTAUTH_URL"
#       value  = "https://12weeks.khanhdp.com"
#       target = ["production"]
#     }
#   ]
# }
#
# resource "vercel_project_domain" "wy_dashboard_domain" {
#   project_id = vercel_project.wy_dashboard.id
#   team_id    = "team_Sf4YHziZbXR2cc11baVuMzLX"
#   domain     = "12weeks.khanhdp.com"
# }
