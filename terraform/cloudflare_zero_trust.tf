# --- Quản lý Cloudflare Zero Trust (Access) ---

locals {
  # Danh sách các subdomain cần bảo vệ bằng Cloudflare Zero Trust
  # Tạm thời chỉ bật cho gkg để test. Sau này bạn có thể thêm:
  # "npm" = "Nginx Proxy Manager", "dozzle" = "Dozzle Logs", v.v.
  zero_trust_apps = {
    "gkg" = "GitLab Knowledge Graph"
  }
}

# Tạo Access Application (Ứng dụng cần bảo vệ)
resource "cloudflare_access_application" "internal_apps" {
  for_each = local.zero_trust_apps

  zone_id          = var.cloudflare_zone_id
  name             = each.value
  domain           = "${each.key}.khanhdp.com"
  session_duration = "24h"
}

# Tạo Access Policy (Luật truy cập)
resource "cloudflare_access_policy" "internal_apps_policy" {
  for_each = local.zero_trust_apps

  application_id = cloudflare_access_application.internal_apps[each.key].id
  zone_id        = var.cloudflare_zone_id
  name           = "Allow Admin Email Only"
  precedence     = 1
  decision       = "allow"

  include {
    email = ["khanhdev4@gmail.com"]
  }
}
