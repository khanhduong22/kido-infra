import json, urllib.request, urllib.error, base64

GRAFANA_URL = "http://localhost:3000"
PROM_UID = "bfic8xgcwqv40c"
LOKI_UID = "afik649p9kzy8d"
AUTH = base64.b64encode(b"admin:KidoOps2026!").decode()

legend_options = {
    "calcs": ["mean", "min", "max", "lastNotNull"],
    "displayMode": "table",
    "placement": "bottom"
}

dashboard = {
  "overwrite": True,
  "dashboard": {
    "id": None,
    "uid": "super-overview",
    "title": "🚀 KidoOps — Command Center",
    "tags": ["overview", "master", "performance"],
    "timezone": "browser",
    "schemaVersion": 38,
    "refresh": "30s",
    "time": {"from": "now-6h", "to": "now"},
    "panels": [
      {
        "id": 99, "type": "row", "title": "🔴 REAL-TIME HEALTH STATUS (Tình trạng hiện tại)", "gridPos": {"x": 0, "y": 0, "w": 24, "h": 1}
      },
      # ─── Row 1: 3 Gauges + 2 Stats ────────────────────────────────────────
      {
        "id": 1, "type": "gauge",
        "title": "💻 CPU Usage (Max: 4 vCores)",
        "gridPos": {"x": 0, "y": 1, "w": 5, "h": 5},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "showThresholdMarkers": True},
        "fieldConfig": {
          "defaults": {
            "min": 0, "max": 4, "unit": "none",
            "thresholds": {"mode": "absolute", "steps": [
              {"color": "green", "value": None},
              {"color": "yellow", "value": 2.5},
              {"color": "red", "value": 3.5}
            ]}
          }
        },
        "targets": [{"expr": "sum(rate(node_cpu_seconds_total{mode!=\"idle\"}[2m]))", "refId": "A", "legendFormat": "Cores"}]
      },
      {
        "id": 2, "type": "gauge",
        "title": "🧠 RAM Used (Max: 8 GiB)",
        "gridPos": {"x": 5, "y": 1, "w": 5, "h": 5},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "showThresholdMarkers": True},
        "fieldConfig": {
          "defaults": {
            "min": 0, "max": 8326963200, "unit": "bytes",
            "thresholds": {"mode": "absolute", "steps": [
              {"color": "green", "value": None},
              {"color": "yellow", "value": 6000000000},
              {"color": "red", "value": 7500000000}
            ]}
          }
        },
        "targets": [{"expr": "node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes", "refId": "A", "legendFormat": "Used RAM"}]
      },
      {
        "id": 3, "type": "gauge",
        "title": "💾 Disk Used (Max: 145 GiB)",
        "gridPos": {"x": 10, "y": 1, "w": 6, "h": 5},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "showThresholdMarkers": True},
        "fieldConfig": {
          "defaults": {
            "min": 0, "max": 155692564480, "unit": "bytes",
            "thresholds": {"mode": "percentage", "steps": [
              {"color": "green", "value": None},
              {"color": "yellow", "value": 70},
              {"color": "red", "value": 90}
            ]}
          }
        },
        "targets": [{"expr": "node_filesystem_size_bytes{mountpoint=\"/\",fstype!=\"tmpfs\"} - node_filesystem_avail_bytes{mountpoint=\"/\",fstype!=\"tmpfs\"}", "refId": "A"}]
      },
      {
        "id": 4, "type": "stat",
        "title": "💀 Job Failures (24h)",
        "gridPos": {"x": 16, "y": 1, "w": 4, "h": 5},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "colorMode": "background", "textMode": "auto"},
        "fieldConfig": {
          "defaults": {
            "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "red", "value": 1}]}
          }
        },
        "targets": [{"expr": "sum(increase(bullmq_job_failed_total[24h])) or vector(0)", "refId": "A", "legendFormat": "Failures"}]
      },
      {
        "id": 5, "type": "stat",
        "title": "✅ Job Completed (24h)",
        "gridPos": {"x": 20, "y": 1, "w": 4, "h": 5},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "colorMode": "background", "textMode": "auto"},
        "fieldConfig": {
          "defaults": {
            "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "green", "value": 1}]}
          }
        },
        "targets": [{"expr": "sum(increase(bullmq_job_completed_total[24h])) or vector(0)", "refId": "A", "legendFormat": "Completed"}]
      },
      # ─── Row 2: Timeline + Docker RAM ─────────────────────────────────────
      {
        "id": 6, "type": "timeseries",
        "title": "📈 CPU & RAM Timeline",
        "gridPos": {"x": 0, "y": 6, "w": 12, "h": 7},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"legend": legend_options},
        "fieldConfig": {"defaults": {"unit": "percent", "custom": {"lineWidth": 2, "fillOpacity": 8}}},
        "targets": [
          {"expr": "100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[2m])) * 100)", "refId": "A", "legendFormat": "CPU %"},
          {"expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100", "refId": "B", "legendFormat": "RAM %"}
        ]
      },
      {
        "id": 999, "type": "stat",
        "title": "🔥 TỔNG DOCKER RAM",
        "gridPos": {"x": 12, "y": 6, "w": 4, "h": 7},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "colorMode": "background", "textMode": "auto"},
        "fieldConfig": {"defaults": {"unit": "bytes", "thresholds": {"mode": "absolute", "steps": [{"color": "blue", "value": None}]}}},
        "targets": [{"expr": "sum(max by(container_name) (docker_container_mem_usage{container_status=\"running\"}))", "refId": "A", "legendFormat": "Total RAM"}]
      },
      {
        "id": 7, "type": "bargauge",
        "title": "🐳 Top RAM Hogs",
        "gridPos": {"x": 16, "y": 6, "w": 8, "h": 7},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "orientation": "horizontal", "displayMode": "gradient"},
        "fieldConfig": {
          "defaults": {
            "unit": "bytes",
            "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 268435456}, {"color": "red", "value": 536870912}]}
          }
        },
        "targets": [
          {"expr": "sort_desc(max by(container_name) (docker_container_mem_usage{container_status=\"running\"}))", "refId": "A", "legendFormat": "{{container_name}}", "instant": True}
        ]
      },
      # ─── Row 3: Fatal logs + DB/Redis stats ───────────────────────────────
      {
        "id": 8, "type": "logs",
        "title": "🚨 Log FATAL — Scrapers",
        "gridPos": {"x": 0, "y": 13, "w": 10, "h": 9},
        "datasource": {"type": "loki", "uid": LOKI_UID},
        "options": {"dedupStrategy": "none", "enableLogDetails": True, "showLabels": False, "showTime": True, "sortOrder": "Descending", "wrapLogMessage": True},
        "targets": [{"expr": "{job=\"vietnam-market-scraper\", log_type=\"stderr\"} |= \"FATAL\"", "refId": "A"}]
      },
      {
        "id": 9, "type": "stat",
        "title": "🐘 Postgres Connections",
        "gridPos": {"x": 10, "y": 13, "w": 14, "h": 5},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "colorMode": "background"},
        "fieldConfig": {
          "defaults": {
            "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 50}, {"color": "red", "value": 80}]}
          }
        },
        "targets": [{"expr": "sum by(state) (pg_stat_activity_count)", "refId": "A", "legendFormat": "{{state}}"}]
      },
      {
        "id": 10, "type": "stat",
        "title": "🟥 Redis Memory",
        "gridPos": {"x": 10, "y": 18, "w": 7, "h": 4},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "colorMode": "value"},
        "fieldConfig": {"defaults": {"unit": "decmbytes", "thresholds": {"mode": "absolute", "steps": [{"color": "blue", "value": None}]}}},
        "targets": [{"expr": "redis_memory_used_bytes / 1024 / 1024", "refId": "A", "legendFormat": "MB"}]
      },
      {
        "id": 11, "type": "stat",
        "title": "🟥 Redis Keys",
        "gridPos": {"x": 17, "y": 18, "w": 7, "h": 4},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "colorMode": "value"},
        "fieldConfig": {"defaults": {"thresholds": {"mode": "absolute", "steps": [{"color": "blue", "value": None}]}}},
        "targets": [{"expr": "sum(redis_db_keys)", "refId": "A", "legendFormat": "Keys"}]
      },

      # ─── SECTION: PREDICTIVE & PERFORMANCE ────────────────────────────────
      {
        "id": 100, "type": "row", "title": "🔮 PERFORMANCE & PREDICTIVE (Phân tích & Cảnh báo sớm)", "gridPos": {"x": 0, "y": 22, "w": 24, "h": 1}
      },
      {
        "id": 12, "type": "timeseries",
        "title": "🚥 Load Average (Hàng chờ CPU)",
        "gridPos": {"x": 0, "y": 23, "w": 12, "h": 9},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"legend": legend_options},
        "fieldConfig": {
          "defaults": {
            "custom": {"lineWidth": 2, "fillOpacity": 5},
            "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 3}, {"color": "red", "value": 6}]}
          }
        },
        "targets": [
          {"expr": "node_load1", "refId": "A", "legendFormat": "Load 1m"},
          {"expr": "node_load5", "refId": "B", "legendFormat": "Load 5m"},
          {"expr": "node_load15", "refId": "C", "legendFormat": "Load 15m"}
        ]
      },
      {
        "id": 13, "type": "timeseries",
        "title": "🧬 CPU Breakdown (Nguyên nhân chậm)",
        "gridPos": {"x": 12, "y": 23, "w": 12, "h": 9},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"legend": legend_options},
        "fieldConfig": {
          "defaults": {"unit": "percent", "custom": {"lineWidth": 1, "fillOpacity": 60, "stacking": {"mode": "normal", "group": "A"}}}
        },
        "targets": [
          {"expr": "sum by(mode) (rate(node_cpu_seconds_total{mode!=\"idle\"}[5m])) * 100", "refId": "A", "legendFormat": "{{mode}}"}
        ]
      },
      {
        "id": 14, "type": "timeseries",
        "title": "🛡️ Node.js Scraper RAM Tracker (Dò Leak)",
        "gridPos": {"x": 0, "y": 32, "w": 12, "h": 9},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"legend": legend_options},
        "fieldConfig": {"defaults": {"unit": "bytes", "custom": {"lineWidth": 2, "fillOpacity": 10}}},
        "targets": [
          {"expr": "sum(scraper_node_process_resident_memory_bytes)", "refId": "A", "legendFormat": "App RSS (RAM thật)"},
          {"expr": "sum(scraper_node_nodejs_heap_size_used_bytes)", "refId": "B", "legendFormat": "V8 Heap Used"}
        ]
      },
      {
        "id": 15, "type": "timeseries",
        "title": "🐌 App Event Loop Lag (P99 Độ trễ)",
        "gridPos": {"x": 12, "y": 32, "w": 12, "h": 9},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"legend": legend_options},
        "fieldConfig": {
          "defaults": {
            "unit": "s",
            "custom": {"lineWidth": 2, "fillOpacity": 15},
            "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 0.05}, {"color": "red", "value": 0.1}]}
          }
        },
        "targets": [
          {"expr": "max(scraper_node_nodejs_eventloop_lag_p99_seconds)", "refId": "A", "legendFormat": "Lag P99"}
        ]
      },
      {
        "id": 16, "type": "gauge",
        "title": "⏳ Tiên tri trống Ổ cứng (Dự đoán sau 24h)",
        "gridPos": {"x": 0, "y": 41, "w": 12, "h": 12},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["last"]}, "orientation": "auto", "showThresholdLabels": True},
        "fieldConfig": {
          "defaults": {
            "unit": "bytes",
            "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "yellow", "value": 0}, {"color": "green", "value": 5000000000}]}
          }
        },
        "targets": [
          {"expr": "predict_linear(node_filesystem_free_bytes{mountpoint=\"/\",fstype!=\"tmpfs\"}[6h], 24*3600)", "refId": "A", "legendFormat": "Dung lượng trống sau 24h"}
        ]
      },
      {
        "id": 17, "type": "timeseries",
        "title": "💽 Disk I/O Bottleneck (Thời gian ổ cứng bận)",
        "gridPos": {"x": 12, "y": 41, "w": 12, "h": 12},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"legend": legend_options},
        "fieldConfig": {"defaults": {"unit": "s", "custom": {"lineWidth": 2}}},
        "targets": [
          {"expr": "rate(node_disk_read_time_seconds_total[5m])", "refId": "A", "legendFormat": "Đọc (Read Time/sec)"},
          {"expr": "rate(node_disk_write_time_seconds_total[5m])", "refId": "B", "legendFormat": "Ghi (Write Time/sec)"}
        ]
      },
      # ─── Row 6: ADVANCED SRE (Z-Score + DB Tracing) ─────────────────────────
      {
        "id": 18, "type": "timeseries",
        "title": "🧠 Z-Score CPU Anomaly Detector (Máy phát hiện bão/Lệch chuẩn 1h)",
        "gridPos": {"x": 0, "y": 53, "w": 24, "h": 9},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"legend": legend_options},
        "fieldConfig": {
          "defaults": {
            "unit": "short", 
            "custom": {"lineWidth": 2, "fillOpacity": 15},
            "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "orange", "value": 2.0}, {"color": "red", "value": 3.0}]}
          }
        },
        "targets": [
          {
            "expr": "abs((100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[2m])) * 100)) - avg_over_time((100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[2m])) * 100))[1h:2m])) / (stddev_over_time((100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[2m])) * 100))[1h:2m]) + 0.001)",
            "refId": "A",
            "legendFormat": "CPU Z-Score (σ)"
          }
        ]
      },
      {
        "id": 19, "type": "table",
        "title": "🐘 Top 10 Slowest SQL Queries (pg_stat_statements)",
        "gridPos": {"x": 0, "y": 62, "w": 24, "h": 10},
        "datasource": {"type": "postgres", "uid": "bfinlnsq4hkw0e"},
        "targets": [
          {
            "datasource": {"type": "postgres", "uid": "bfinlnsq4hkw0e"},
            "editorMode": "code",
            "format": "table",
            "rawQuery": True,
            "rawSql": "SELECT substring(query for 80) as query_preview, calls, round(total_exec_time::numeric, 2) as total_ms, round(mean_exec_time::numeric, 2) as avg_ms FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;",
            "refId": "A"
          }
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
