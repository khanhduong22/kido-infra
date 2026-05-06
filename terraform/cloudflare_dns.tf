# --- Quản lý DNS Cloudflare ---

# Lưu ý: Cần nhập Zone ID của domain khanhdp.com trên Cloudflare
variable "cloudflare_zone_id" {
  description = "Zone ID của domain khanhdp.com trên Cloudflare"
  type        = string
  default     = "d87b502d9777331c553e20c9d57b470d"
}

locals {
  # Danh sách các subdomain cần bật Đám mây màu cam (Proxied)
  proxied_subdomains = [
    "dozzle",
    "grafana",
    "kuma",
    "npm",
    "otel",
    "portainer",
    "signoz",
    "tools",
    "gkg",
    "12wy-api",
    "p2p"
  ]
}

# Tạo tự động hàng loạt bản ghi DNS có bật Proxy
resource "cloudflare_record" "proxied_records" {
  for_each = toset(local.proxied_subdomains)

  zone_id = var.cloudflare_zone_id
  name    = each.key # Tên subdomain (ví dụ: dozzle.khanhdp.com)
  content = data.sops_file.secrets.data["shared_vps_host"]
  type    = "A"
  proxied = true # Bật tính năng Proxy ẩn IP (Đám mây màu cam)
}



# --- Bản ghi DNS trỏ về Vercel (Các ứng dụng Frontend) ---
# LƯU Ý: Khi trỏ về Vercel, nên để proxied = false (DNS Only) vì Vercel đã tự lo SSL và CDN.
# Bật Proxy Cloudflare đè lên Vercel dễ gây ra lỗi "Too many redirects".
resource "cloudflare_record" "vercel_md" {
  zone_id = var.cloudflare_zone_id
  name    = "md" # Subdomain md.khanhdp.com
  content = "cname.vercel-dns.com"
  type    = "CNAME"
  proxied = false 
}

resource "cloudflare_record" "vercel_12weeks" {
  zone_id = var.cloudflare_zone_id
  name    = "12weeks" # Subdomain 12weeks.khanhdp.com
  content = "cname.vercel-dns.com"
  type    = "CNAME"
  proxied = false 
}
