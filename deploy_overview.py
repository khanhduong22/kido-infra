import json, urllib.request, urllib.error, base64

GRAFANA_URL = "http://localhost:3000"
PROM_UID = "bfic8xgcwqv40c"
LOKI_UID = "afik649p9kzy8d"
AUTH = base64.b64encode(b"admin:KidoOps2026!").decode()

dashboard = {
  "overwrite": True,
  "dashboard": {
    "id": None,
    "uid": "super-overview",
    "title": "🚀 KidoOps — Command Center",
    "tags": ["overview", "home"],
    "timezone": "browser",
    "schemaVersion": 38,
    "refresh": "30s",
    "time": {"from": "now-1h", "to": "now"},
    "panels": [
      # ─── Row 1: 3 Gauges + 2 Stats ────────────────────────────────────────
      {
        "id": 1, "type": "gauge",
        "title": "💻 CPU Usage",
        "gridPos": {"x": 0, "y": 0, "w": 4, "h": 5},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "showThresholdMarkers": True},
        "fieldConfig": {
          "defaults": {
            "min": 0, "max": 100, "unit": "percent",
            "thresholds": {"mode": "absolute", "steps": [
              {"color": "green", "value": None},
              {"color": "yellow", "value": 60},
              {"color": "red", "value": 85}
            ]}
          }
        },
        "targets": [{"expr": "100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[2m])) * 100)", "refId": "A", "legendFormat": "CPU %"}]
      },
      {
        "id": 2, "type": "gauge",
        "title": "🧠 RAM Usage",
        "gridPos": {"x": 4, "y": 0, "w": 4, "h": 5},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "showThresholdMarkers": True},
        "fieldConfig": {
          "defaults": {
            "min": 0, "max": 100, "unit": "percent",
            "thresholds": {"mode": "absolute", "steps": [
              {"color": "green", "value": None},
              {"color": "yellow", "value": 70},
              {"color": "red", "value": 90}
            ]}
          }
        },
        "targets": [{"expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100", "refId": "A", "legendFormat": "RAM %"}]
      },
      {
        "id": 3, "type": "gauge",
        "title": "💾 Disk Usage",
        "gridPos": {"x": 8, "y": 0, "w": 4, "h": 5},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "showThresholdMarkers": True},
        "fieldConfig": {
          "defaults": {
            "min": 0, "max": 100, "unit": "percent",
            "thresholds": {"mode": "absolute", "steps": [
              {"color": "green", "value": None},
              {"color": "yellow", "value": 70},
              {"color": "red", "value": 90}
            ]}
          }
        },
        "targets": [{"expr": "(1 - (node_filesystem_avail_bytes{mountpoint=\"/\",fstype!=\"tmpfs\"} / node_filesystem_size_bytes{mountpoint=\"/\",fstype!=\"tmpfs\"})) * 100", "refId": "A"}]
      },
      {
        "id": 4, "type": "stat",
        "title": "💀 Job Failures (5m)",
        "gridPos": {"x": 12, "y": 0, "w": 6, "h": 5},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "colorMode": "background", "textMode": "auto"},
        "fieldConfig": {
          "defaults": {
            "thresholds": {"mode": "absolute", "steps": [
              {"color": "green", "value": None},
              {"color": "red", "value": 1}
            ]}
          }
        },
        "targets": [{"expr": "sum(increase(bullmq_job_failed_total[5m])) or vector(0)", "refId": "A", "legendFormat": "Failures"}]
      },
      {
        "id": 5, "type": "stat",
        "title": "✅ Job Completed (5m)",
        "gridPos": {"x": 18, "y": 0, "w": 6, "h": 5},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "colorMode": "background", "textMode": "auto"},
        "fieldConfig": {
          "defaults": {
            "thresholds": {"mode": "absolute", "steps": [
              {"color": "red", "value": None},
              {"color": "green", "value": 1}
            ]}
          }
        },
        "targets": [{"expr": "sum(increase(bullmq_job_completed_total[5m])) or vector(0)", "refId": "A", "legendFormat": "Completed"}]
      },
      # ─── Row 2: Timeline + Docker RAM ─────────────────────────────────────
      {
        "id": 6, "type": "timeseries",
        "title": "📈 CPU & RAM theo thời gian",
        "gridPos": {"x": 0, "y": 5, "w": 12, "h": 7},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "fieldConfig": {"defaults": {"unit": "percent", "custom": {"lineWidth": 2, "fillOpacity": 8}}},
        "targets": [
          {"expr": "100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[2m])) * 100)", "refId": "A", "legendFormat": "CPU %"},
          {"expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100", "refId": "B", "legendFormat": "RAM %"}
        ]
      },
      {
        "id": 7, "type": "bargauge",
        "title": "🐳 Docker — RAM per Container",
        "gridPos": {"x": 12, "y": 5, "w": 12, "h": 7},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "orientation": "horizontal", "displayMode": "gradient"},
        "fieldConfig": {
          "defaults": {
            "unit": "decmbytes",
            "thresholds": {"mode": "absolute", "steps": [
              {"color": "green", "value": None},
              {"color": "yellow", "value": 256},
              {"color": "red", "value": 512}
            ]}
          }
        },
        "targets": [{"expr": "topk(8, docker_container_mem_usage{container_status=\"running\"} / 1024 / 1024)", "refId": "A", "legendFormat": "{{container_name}}"}]
      },
      # ─── Row 3: Fatal logs + DB/Redis stats ───────────────────────────────
      {
        "id": 8, "type": "logs",
        "title": "🚨 Log FATAL — Scrapers",
        "gridPos": {"x": 0, "y": 12, "w": 16, "h": 9},
        "datasource": {"type": "loki", "uid": LOKI_UID},
        "options": {"dedupStrategy": "none", "enableLogDetails": True, "showLabels": False, "showTime": True, "sortOrder": "Descending", "wrapLogMessage": True},
        "targets": [{"expr": "{job=\"vietnam-market-scraper\", log_type=\"stderr\"} |= \"FATAL\"", "refId": "A"}]
      },
      {
        "id": 9, "type": "stat",
        "title": "🐘 DB Active Connections",
        "gridPos": {"x": 16, "y": 12, "w": 8, "h": 4},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "colorMode": "background"},
        "fieldConfig": {
          "defaults": {
            "thresholds": {"mode": "absolute", "steps": [
              {"color": "green", "value": None},
              {"color": "yellow", "value": 50},
              {"color": "red", "value": 80}
            ]}
          }
        },
        "targets": [{"expr": "pg_stat_activity_count{datname=\"postgres\"}", "refId": "A", "legendFormat": "Connections"}]
      },
      {
        "id": 10, "type": "stat",
        "title": "🟥 Redis Memory",
        "gridPos": {"x": 16, "y": 16, "w": 4, "h": 5},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "colorMode": "value"},
        "fieldConfig": {"defaults": {"unit": "decmbytes", "thresholds": {"mode": "absolute", "steps": [{"color": "blue", "value": None}]}}},
        "targets": [{"expr": "redis_memory_used_bytes / 1024 / 1024", "refId": "A", "legendFormat": "MB"}]
      },
      {
        "id": 11, "type": "stat",
        "title": "🟥 Redis Keys",
        "gridPos": {"x": 20, "y": 16, "w": 4, "h": 5},
        "datasource": {"type": "prometheus", "uid": PROM_UID},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "colorMode": "value"},
        "fieldConfig": {"defaults": {"thresholds": {"mode": "absolute", "steps": [{"color": "blue", "value": None}]}}},
        "targets": [{"expr": "sum(redis_db_keys)", "refId": "A", "legendFormat": "Keys"}]
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
with urllib.request.urlopen(req) as resp:
  result = json.loads(resp.read())
  print("✅ Dashboard:", result.get("status"), result.get("url"))
