# --- Quản lý SigNoz Dashboard & Alerts ---

# Ví dụ 1: Tạo một Alert Rule trong SigNoz khi CPU VPS cao
# resource "signoz_alert" "high_cpu_usage" {
#   alert_type = "METRIC_BASED"
#   alert      = "[IaC] Cảnh báo CPU vượt mức 80%"
#   severity   = "critical"
#   frequency  = "5m"
#   
#   # Provider mới yêu cầu condition là một chuỗi JSON phức tạp
#   # condition  = "{...}"
# 
#   labels = {
#     env  = "production"
#     team = "devops"
#   }
# }

# Ví dụ 2: Tạo một Dashboard mới (Sử dụng Dashboard JSON)
# resource "signoz_dashboard" "vps_metrics" {
#   name        = "[IaC] Tổng quan VPS"
#   description = "Dashboard này được quản lý tự động bằng Terraform"
#   data        = file("${path.module}/dashboards/vps_overview.json")
# }
