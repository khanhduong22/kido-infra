resource "grafana_dashboard" "kido_ops" {
  config_json = file("${path.module}/dashboards/kido_ops_v2.json")
  overwrite   = true
}
