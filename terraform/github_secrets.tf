# --- Quản lý Secrets cho các Repositories ---



# 2. Inject Secrets vào repo danang-badminton-hub
resource "github_actions_secret" "badminton_vps_host" {
  repository      = "danang-badminton-hub"
  secret_name     = "VPS_HOST"
  plaintext_value = data.sops_file.secrets.data["shared_vps_host"]
}


# 3. Inject Secrets tương tự vào repo vietnam-market-scraper
resource "github_actions_secret" "scraper_vps_host" {
  repository      = "vietnam-market-scraper"
  secret_name     = "VPS_HOST"
  plaintext_value = data.sops_file.secrets.data["shared_vps_host"]
}
