import json, urllib.request, urllib.error, base64

GRAFANA_URL = "http://localhost:3000"
PROM_UID = "bfic8xgcwqv40c"
AUTH = base64.b64encode(b"admin:KidoOps2026!").decode()

dashboard = {
  "overwrite": True,
  "dashboard": {
    "id": None,
    "uid": "predictive-perf",
    "title": "🔮 Performance & Predictive",
    "tags": ["performance", "predictive"],
    "timezone": "browser",
    "schemaVersion": 38,
    "refresh": "1m",
    "time": {"from": "now-6h", "to": "now"},
    "panels": [
      # ─── Row 1: CPU & Load Averages ──────────────────────────────────────
      {
        "id": 1, "type": "timeseries",
        "title": "🚥 Load Average (Hàng chờ CPU)",
        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"legend": {"displayMode": "table", "placement": "bottom"}},
        "fieldConfig": {
          "defaults": {
            "custom": {"lineWidth": 2, "fillOpacity": 5},
            "thresholds": {"mode": "absolute", "steps": [
              {"color": "green", "value": None},
              {"color": "yellow", "value": 3},
              {"color": "red", "value": 6}
            ]}
          }
        },
        "targets": [
          {"expr": "node_load1", "refId": "A", "legendFormat": "Load 1m"},
          {"expr": "node_load5", "refId": "B", "legendFormat": "Load 5m"},
          {"expr": "node_load15", "refId": "C", "legendFormat": "Load 15m"}
        ]
      },
      {
        "id": 2, "type": "timeseries",
        "title": "🧬 CPU Breakdown (Nguyên nhân chậm CPU)",
        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "fieldConfig": {
          "defaults": {"unit": "percent", "custom": {"lineWidth": 1, "fillOpacity": 60, "stacking": {"mode": "normal", "group": "A"}}}
        },
        "targets": [
          {"expr": "sum by(mode) (rate(node_cpu_seconds_total{mode!=\"idle\"}[5m])) * 100", "refId": "A", "legendFormat": "{{mode}}"}
        ]
      },
      # ─── Row 2: Node.js Vitals ──────────────────────────────────────────
      {
        "id": 3, "type": "timeseries",
        "title": "🛡️ Node.js Scraper RAM (Dò rỉ RAM Leak)",
        "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "fieldConfig": {"defaults": {"unit": "bytes", "custom": {"lineWidth": 2, "fillOpacity": 10}}},
        "targets": [
          {"expr": "scraper_node_process_resident_memory_bytes", "refId": "A", "legendFormat": "RSS (RAM thật)"},
          {"expr": "scraper_node_nodejs_heap_size_used_bytes", "refId": "B", "legendFormat": "V8 Heap Used"}
        ]
      },
      {
        "id": 4, "type": "timeseries",
        "title": "🐌 Event Loop Lag (P99) - Độ trễ Node.js",
        "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "fieldConfig": {
          "defaults": {
            "unit": "s",
            "custom": {"lineWidth": 2, "fillOpacity": 15},
            "thresholds": {"mode": "absolute", "steps": [
              {"color": "green", "value": None},
              {"color": "yellow", "value": 0.05},
              {"color": "red", "value": 0.1}
            ]}
          }
        },
        "targets": [
          {"expr": "scraper_node_nodejs_eventloop_lag_p99_seconds", "refId": "A", "legendFormat": "Lag P99"}
        ]
      },
      # ─── Row 3: Predictive (Ổ cứng & Disk IO) ──────────────────────────
      {
        "id": 5, "type": "gauge",
        "title": "⏳ Disk Full Prediction (Còn trống trong 24h tới không?)",
        "gridPos": {"x": 0, "y": 16, "w": 12, "h": 8},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["last"]}, "orientation": "auto", "showThresholdLabels": True},
        "fieldConfig": {
          "defaults": {
            "unit": "bytes",
            "thresholds": {"mode": "absolute", "steps": [
              {"color": "red", "value": None},
              {"color": "yellow", "value": 0},
              {"color": "green", "value": 5000000000}
            ]}
          }
        },
        "targets": [
          {"expr": "predict_linear(node_filesystem_free_bytes{mountpoint=\"/\",fstype!=\"tmpfs\"}[6h], 24*3600)", "refId": "A", "legendFormat": "Free bytes after 24h"}
        ]
      },
      {
        "id": 6, "type": "timeseries",
        "title": "💽 Disk I/O Throttling (Ổ cứng bị bão hoà)",
        "gridPos": {"x": 12, "y": 16, "w": 12, "h": 8},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "fieldConfig": {"defaults": {"custom": {"lineWidth": 2}}},
        "targets": [
          {"expr": "rate(node_disk_read_time_seconds_total[5m])", "refId": "A", "legendFormat": "Read Time (/sec)"},
          {"expr": "rate(node_disk_write_time_seconds_total[5m])", "refId": "B", "legendFormat": "Write Time (/sec)"}
        ]
      }
    ]
  }
}

data = json.dumps(dashboard).encode()
req = urllib.request.Request(
  f"{GRAFANA_URL}/api/dashboards/db",
  data=data,
  headers={"Content-Type": "application/json", "Authorization": f"Basic {AUTH}"},
  method="POST"
)
try:
  with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
    print("✅ Dashboard:", result.get("status"), result.get("url"))
except urllib.error.URLError as e:
  print(f"❌ Deploy failed: {e}")
  if hasattr(e, 'read'): print(e.read().decode())
