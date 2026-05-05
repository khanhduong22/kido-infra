# --- Quản lý Nginx Proxy Manager (NPM) ---

locals {
  # Bản đồ ánh xạ Subdomain -> Port nội bộ
  # Bạn có thể điều chỉnh port tương ứng với file docker-compose của bạn
  proxy_mappings = {
    # Các app nằm CÙNG mạng với NPM (172.23.0.x) -> Dùng tên Container & Port nội bộ
    "grafana"   = { host = "grafana", port = 3000 }
    "dozzle"    = { host = "dozzle", port = 8080 }
    "kuma"      = { host = "uptime-kuma", port = 3001 } # Chú ý port nội bộ là 3001, pub là 3002
    "portainer" = { host = "portainer", port = 9000 }
    "tools"     = { host = "it-tools", port = 80 }      # Chú ý port nội bộ là 80, pub là 8086

    "npm"       = { host = "nginx-proxy-manager", port = 81 }
    "signoz"    = { host = "172.17.0.1", port = 8088 }              # SigNoz nằm khác network nên dùng Docker host IP và port map ra ngoài
    "otel"      = { host = "signoz-otel-collector", port = 4318 } # Đưa về port HTTP OTLP chuẩn 4318
    "gkg"       = { host = "gkg", port = 27495 }
    "gitnexus"  = { host = "gitnexus", port = 80 }
    "12wy-api"  = { host = "12wy_api", port = 3001 }
    "12weeks"   = { host = "12wy_dashboard", port = 3000 }
  }
}

# Tạo tự động hàng loạt Proxy Host
resource "nginxproxymanager_proxy_host" "hosts" {
  for_each = local.proxy_mappings

  domain_names = ["${each.key}.khanhdp.com"]
  forward_scheme = "http"
  forward_host   = each.value.host
  forward_port   = each.value.port

  # Bật WebSocket Support (rất cần cho các app thời gian thực như Dozzle, Portainer)
  allow_websocket_upgrade = true
  
  # Chặn công cụ quét lỗi (Tùy chọn)
  block_exploits = true

  # Đã dò tìm thấy Custom SSL Certificate (Cloudflare Origin Cert) của bạn có ID = 1 trên NPM!
  # Tự động gắn chứng chỉ này vào tất cả các subdomain.
  certificate_id = 1
  ssl_forced     = true
}
