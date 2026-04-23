#!/bin/bash
# Deploy Super Overview Dashboard to Grafana
GRAFANA_URL="http://localhost:3000"
GRAFANA_USER="admin"
GRAFANA_PASS="KidoOps2026!"

# Get Loki datasource UID
LOKI_UID=$(curl -s -u "$GRAFANA_USER:$GRAFANA_PASS" "$GRAFANA_URL/api/datasources/name/Loki" | python3 -c "import sys,json; print(json.load(sys.stdin).get('uid',''))")
PROM_UID=$(curl -s -u "$GRAFANA_USER:$GRAFANA_PASS" "$GRAFANA_URL/api/datasources/name/Prometheus" | python3 -c "import sys,json; print(json.load(sys.stdin).get('uid',''))")

echo "→ Prometheus UID: $PROM_UID"
echo "→ Loki UID: $LOKI_UID"

echo "→ Deploying Super Overview Dashboard..."

PAYLOAD=$(python3 -c "
import json, sys

prom = '$PROM_UID'
loki = '$LOKI_UID'

dashboard = {
  'overwrite': True,
  'dashboard': {
    'id': None,
    'uid': 'super-overview',
    'title': '🚀 KidoOps — Command Center',
    'tags': ['overview', 'home', 'master'],
    'timezone': 'browser',
    'schemaVersion': 38,
    'refresh': '30s',
    'time': {'from': 'now-1h', 'to': 'now'},
    'panels': [
      # ─── Row 1: VPS Health ────────────────────────────────────────────────
      {
        'id': 1, 'type': 'gauge',
        'title': '💻 CPU Usage (%)',
        'gridPos': {'x': 0, 'y': 0, 'w': 4, 'h': 4},
        'datasource': {'type': 'prometheus', 'uid': prom},
        'options': {'reduceOptions': {'calcs': ['lastNotNull']}, 'orientation': 'auto', 'showThresholdLabels': False, 'showThresholdMarkers': True},
        'fieldConfig': {
          'defaults': {
            'min': 0, 'max': 100, 'unit': 'percent',
            'thresholds': {'mode': 'absolute', 'steps': [
              {'color': 'green', 'value': None},
              {'color': 'yellow', 'value': 60},
              {'color': 'red', 'value': 85}
            ]}
          }
        },
        'targets': [{'expr': '100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[2m])) * 100)', 'refId': 'A', 'legendFormat': 'CPU %'}]
      },
      {
        'id': 2, 'type': 'gauge',
        'title': '🧠 RAM Usage (%)',
        'gridPos': {'x': 4, 'y': 0, 'w': 4, 'h': 4},
        'datasource': {'type': 'prometheus', 'uid': prom},
        'options': {'reduceOptions': {'calcs': ['lastNotNull']}, 'orientation': 'auto', 'showThresholdLabels': False, 'showThresholdMarkers': True},
        'fieldConfig': {
          'defaults': {
            'min': 0, 'max': 100, 'unit': 'percent',
            'thresholds': {'mode': 'absolute', 'steps': [
              {'color': 'green', 'value': None},
              {'color': 'yellow', 'value': 70},
              {'color': 'red', 'value': 90}
            ]}
          }
        },
        'targets': [{'expr': '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100', 'refId': 'A', 'legendFormat': 'RAM %'}]
      },
      {
        'id': 3, 'type': 'gauge',
        'title': '💾 Disk Usage (%)',
        'gridPos': {'x': 8, 'y': 0, 'w': 4, 'h': 4},
        'datasource': {'type': 'prometheus', 'uid': prom},
        'options': {'reduceOptions': {'calcs': ['lastNotNull']}, 'orientation': 'auto', 'showThresholdLabels': False, 'showThresholdMarkers': True},
        'fieldConfig': {
          'defaults': {
            'min': 0, 'max': 100, 'unit': 'percent',
            'thresholds': {'mode': 'absolute', 'steps': [
              {'color': 'green', 'value': None},
              {'color': 'yellow', 'value': 70},
              {'color': 'red', 'value': 90}
            ]}
          }
        },
        'targets': [{'expr': '(1 - (node_filesystem_avail_bytes{mountpoint=\"/\", fstype!=\"tmpfs\"} / node_filesystem_size_bytes{mountpoint=\"/\", fstype!=\"tmpfs\"})) * 100', 'refId': 'A', 'legendFormat': 'Disk /'}]
      },
      {
        'id': 4, 'type': 'stat',
        'title': '🔴 Scraper Job Failures (5m)',
        'gridPos': {'x': 12, 'y': 0, 'w': 6, 'h': 4},
        'datasource': {'type': 'prometheus', 'uid': prom},
        'options': {'reduceOptions': {'calcs': ['lastNotNull']}, 'orientation': 'auto', 'textMode': 'auto', 'colorMode': 'background'},
        'fieldConfig': {
          'defaults': {
            'thresholds': {'mode': 'absolute', 'steps': [
              {'color': 'green', 'value': None},
              {'color': 'red', 'value': 1}
            ]}
          }
        },
        'targets': [{'expr': 'sum(increase(bullmq_job_failed_total[5m])) or vector(0)', 'refId': 'A', 'legendFormat': 'Failures'}]
      },
      {
        'id': 5, 'type': 'stat',
        'title': '✅ Scraper Job Success (5m)',
        'gridPos': {'x': 18, 'y': 0, 'w': 6, 'h': 4},
        'datasource': {'type': 'prometheus', 'uid': prom},
        'options': {'reduceOptions': {'calcs': ['lastNotNull']}, 'orientation': 'auto', 'textMode': 'auto', 'colorMode': 'background'},
        'fieldConfig': {
          'defaults': {
            'thresholds': {'mode': 'absolute', 'steps': [
              {'color': 'red', 'value': None},
              {'color': 'green', 'value': 1}
            ]}
          }
        },
        'targets': [{'expr': 'sum(increase(bullmq_job_completed_total[5m])) or vector(0)', 'refId': 'A', 'legendFormat': 'Completed'}]
      },
      # ─── Row 2: CPU/RAM Timeline ──────────────────────────────────────────
      {
        'id': 6, 'type': 'timeseries',
        'title': '📈 CPU & RAM theo thời gian',
        'gridPos': {'x': 0, 'y': 4, 'w': 12, 'h': 7},
        'datasource': {'type': 'prometheus', 'uid': prom},
        'fieldConfig': {'defaults': {'unit': 'percent', 'custom': {'lineWidth': 2, 'fillOpacity': 8}}},
        'targets': [
          {'expr': '100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[2m])) * 100)', 'refId': 'A', 'legendFormat': 'CPU %'},
          {'expr': '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100', 'refId': 'B', 'legendFormat': 'RAM %'}
        ]
      },
      # ─── Row 2: Docker Top Containers ─────────────────────────────────────
      {
        'id': 7, 'type': 'bargauge',
        'title': '🐳 Docker — RAM theo Container (MB)',
        'gridPos': {'x': 12, 'y': 4, 'w': 12, 'h': 7},
        'datasource': {'type': 'prometheus', 'uid': prom},
        'options': {'reduceOptions': {'calcs': ['lastNotNull']}, 'orientation': 'horizontal', 'displayMode': 'gradient'},
        'fieldConfig': {
          'defaults': {
            'unit': 'decmbytes',
            'thresholds': {'mode': 'absolute', 'steps': [
              {'color': 'green', 'value': None},
              {'color': 'yellow', 'value': 256},
              {'color': 'red', 'value': 512}
            ]}
          }
        },
        'targets': [{'expr': 'topk(8, docker_container_mem_usage{container_status=\"running\"} / 1024 / 1024)', 'refId': 'A', 'legendFormat': '{{container_name}}'}]
      },
      # ─── Row 3: Fatal Logs & DB Connections ───────────────────────────────
      {
        'id': 8, 'type': 'logs',
        'title': '🚨 Log lỗi FATAL (Scraper)',
        'gridPos': {'x': 0, 'y': 11, 'w': 16, 'h': 9},
        'datasource': {'type': 'loki', 'uid': loki},
        'options': {'dedupStrategy': 'none', 'enableLogDetails': True, 'showLabels': False, 'showTime': True, 'sortOrder': 'Descending', 'wrapLogMessage': True},
        'targets': [{'expr': '{job=\"vietnam-market-scraper\", log_type=\"stderr\"} |= \"FATAL\"', 'refId': 'A'}]
      },
      {
        'id': 9, 'type': 'stat',
        'title': '🐘 DB Active Connections',
        'gridPos': {'x': 16, 'y': 11, 'w': 8, 'h': 4},
        'datasource': {'type': 'prometheus', 'uid': prom},
        'options': {'reduceOptions': {'calcs': ['lastNotNull']}, 'colorMode': 'background'},
        'fieldConfig': {
          'defaults': {
            'thresholds': {'mode': 'absolute', 'steps': [
              {'color': 'green', 'value': None},
              {'color': 'yellow', 'value': 50},
              {'color': 'red', 'value': 80}
            ]}
          }
        },
        'targets': [{'expr': 'pg_stat_activity_count{datname=\"postgres\"}', 'refId': 'A', 'legendFormat': 'Connections'}]
      },
      {
        'id': 10, 'type': 'stat',
        'title': '🟥 Redis — Keys trong DB',
        'gridPos': {'x': 16, 'y': 15, 'w': 4, 'h': 5},
        'datasource': {'type': 'prometheus', 'uid': prom},
        'options': {'reduceOptions': {'calcs': ['lastNotNull']}, 'colorMode': 'value'},
        'fieldConfig': {'defaults': {'thresholds': {'mode': 'absolute', 'steps': [{'color': 'blue', 'value': None}]}}},
        'targets': [{'expr': 'sum(redis_db_keys)', 'refId': 'A', 'legendFormat': 'Keys'}]
      },
      {
        'id': 11, 'type': 'stat',
        'title': '🟥 Redis — Memory Used',
        'gridPos': {'x': 20, 'y': 15, 'w': 4, 'h': 5},
        'datasource': {'type': 'prometheus', 'uid': prom},
        'options': {'reduceOptions': {'calcs': ['lastNotNull']}, 'colorMode': 'value'},
        'fieldConfig': {'defaults': {'unit': 'decmbytes', 'thresholds': {'mode': 'absolute', 'steps': [{'color': 'blue', 'value': None}, {'color': 'red', 'value': 200}]}}},
        'targets': [{'expr': 'redis_memory_used_bytes / 1024 / 1024', 'refId': 'A', 'legendFormat': 'RAM (MB)'}]
      }
    ]
  }
}

print(json.dumps(dashboard))
")

curl -s -X POST "$GRAFANA_URL/api/dashboards/db" \
  -u "$GRAFANA_USER:$GRAFANA_PASS" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" | python3 -c "import sys,json; r=json.load(sys.stdin); print('Dashboard:', r.get('status','?'), r.get('url',''))"
