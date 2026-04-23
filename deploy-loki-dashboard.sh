#!/bin/bash
# Deploy Loki Scraper Dashboard to Grafana
GRAFANA_URL="http://localhost:3000"
GRAFANA_USER="admin"
GRAFANA_PASS="KidoOps2026!"

# 1. Ensure Loki datasource exists
echo "→ Adding Loki datasource..."
curl -s -X POST "$GRAFANA_URL/api/datasources" \
  -u "$GRAFANA_USER:$GRAFANA_PASS" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Loki",
    "type": "loki",
    "url": "http://loki:3100",
    "access": "proxy",
    "isDefault": false
  }' | python3 -c "import sys,json; r=json.load(sys.stdin); print('Datasource:', r.get('message', r.get('name','?')))"

# 2. Get Loki datasource UID
LOKI_UID=$(curl -s -u "$GRAFANA_USER:$GRAFANA_PASS" "$GRAFANA_URL/api/datasources/name/Loki" | python3 -c "import sys,json; print(json.load(sys.stdin).get('uid',''))")
echo "→ Loki UID: $LOKI_UID"

# 3. Deploy dashboard
echo "→ Deploying Scraper Logs Dashboard..."
curl -s -X POST "$GRAFANA_URL/api/dashboards/db" \
  -u "$GRAFANA_USER:$GRAFANA_PASS" \
  -H "Content-Type: application/json" \
  -d "{
  \"overwrite\": true,
  \"dashboard\": {
    \"id\": null,
    \"uid\": \"scraper-loki-logs\",
    \"title\": \"🔍 Vietnam Market Scraper — Logs\",
    \"tags\": [\"loki\", \"scraper\", \"logs\"],
    \"timezone\": \"Asia/Ho_Chi_Minh\",
    \"schemaVersion\": 38,
    \"refresh\": \"30s\",
    \"time\": { \"from\": \"now-1h\", \"to\": \"now\" },
    \"panels\": [
      {
        \"id\": 1,
        \"title\": \"📊 Log Volume (lines/min)\",
        \"type\": \"timeseries\",
        \"gridPos\": { \"h\": 6, \"w\": 24, \"x\": 0, \"y\": 0 },
        \"datasource\": { \"type\": \"loki\", \"uid\": \"$LOKI_UID\" },
        \"targets\": [
          {
            \"expr\": \"sum by (log_type) (rate({job=\\\"vietnam-market-scraper\\\"}[1m]))\",
            \"legendFormat\": \"{{log_type}}\",
            \"refId\": \"A\"
          }
        ],
        \"fieldConfig\": {
          \"defaults\": {
            \"color\": { \"mode\": \"palette-classic\" },
            \"custom\": { \"lineWidth\": 2, \"fillOpacity\": 10 }
          },
          \"overrides\": [
            {
              \"matcher\": { \"id\": \"byName\", \"options\": \"stderr\" },
              \"properties\": [{ \"id\": \"color\", \"value\": { \"mode\": \"fixed\", \"fixedColor\": \"red\" } }]
            }
          ]
        }
      },
      {
        \"id\": 2,
        \"title\": \"🚨 Lỗi FATAL (Exceptions)\",
        \"type\": \"logs\",
        \"gridPos\": { \"h\": 10, \"w\": 24, \"x\": 0, \"y\": 6 },
        \"datasource\": { \"type\": \"loki\", \"uid\": \"$LOKI_UID\" },
        \"options\": {
          \"dedupStrategy\": \"none\",
          \"enableLogDetails\": true,
          \"showLabels\": false,
          \"showTime\": true,
          \"sortOrder\": \"Descending\",
          \"wrapLogMessage\": true
        },
        \"targets\": [
          {
            \"expr\": \"{job=\\\"vietnam-market-scraper\\\", log_type=\\\"stderr\\\"} |= \\\"FATAL\\\"\",
            \"refId\": \"A\"
          }
        ]
      },
      {
        \"id\": 3,
        \"title\": \"✅ Job Success (XONG)\",
        \"type\": \"logs\",
        \"gridPos\": { \"h\": 8, \"w\": 12, \"x\": 0, \"y\": 16 },
        \"datasource\": { \"type\": \"loki\", \"uid\": \"$LOKI_UID\" },
        \"options\": {
          \"dedupStrategy\": \"none\",
          \"enableLogDetails\": true,
          \"showLabels\": false,
          \"showTime\": true,
          \"sortOrder\": \"Descending\"
        },
        \"targets\": [
          {
            \"expr\": \"{job=\\\"vietnam-market-scraper\\\"} |= \\\"Job XONG\\\"\",
            \"refId\": \"A\"
          }
        ]
      },
      {
        \"id\": 4,
        \"title\": \"💀 Job Failures\",
        \"type\": \"logs\",
        \"gridPos\": { \"h\": 8, \"w\": 12, \"x\": 12, \"y\": 16 },
        \"datasource\": { \"type\": \"loki\", \"uid\": \"$LOKI_UID\" },
        \"options\": {
          \"dedupStrategy\": \"none\",
          \"enableLogDetails\": true,
          \"showLabels\": false,
          \"showTime\": true,
          \"sortOrder\": \"Descending\"
        },
        \"targets\": [
          {
            \"expr\": \"{job=\\\"vietnam-market-scraper\\\"} |= \\\"Error Job NGU\\\"\",
            \"refId\": \"A\"
          }
        ]
      },
      {
        \"id\": 5,
        \"title\": \"📋 All Logs (Full Stream)\",
        \"type\": \"logs\",
        \"gridPos\": { \"h\": 14, \"w\": 24, \"x\": 0, \"y\": 24 },
        \"datasource\": { \"type\": \"loki\", \"uid\": \"$LOKI_UID\" },
        \"options\": {
          \"dedupStrategy\": \"none\",
          \"enableLogDetails\": true,
          \"showLabels\": true,
          \"showTime\": true,
          \"sortOrder\": \"Descending\",
          \"wrapLogMessage\": false
        },
        \"targets\": [
          {
            \"expr\": \"{job=\\\"vietnam-market-scraper\\\"}\",
            \"refId\": \"A\"
          }
        ]
      }
    ]
  }
}" | python3 -c "import sys,json; r=json.load(sys.stdin); print('Dashboard:', r.get('status','?'), r.get('url',''))"
