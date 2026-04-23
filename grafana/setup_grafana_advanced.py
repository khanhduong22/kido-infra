#!/usr/bin/env python3
"""
Auto-setup Grafana:
1. Add PostgreSQL (TimescaleDB) datasource
2. Import pg_stat_statements dashboard (ID 12271)
3. Create Z-Score CPU anomaly alert rule
"""

import json, urllib.request, urllib.error, time

GRAFANA_URL = 'http://localhost:3000'
GRAFANA_AUTH = ('admin', 'KidoOps2026!')
TIMESCALE_HOST = 'timescaledb'  # Internal hostname over ops_bridge
TIMESCALE_PORT = 5432            # Internal port
TIMESCALE_DB   = 'postgres'
TIMESCALE_USER = 'postgres'
TIMESCALE_PASS = 'learning_timescale_2026'

def gf_req(method, path, body=None):
    url = GRAFANA_URL + path
    data = json.dumps(body).encode() if body else None
    import base64
    token = base64.b64encode(f"{GRAFANA_AUTH[0]}:{GRAFANA_AUTH[1]}".encode()).decode()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {token}',
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  HTTP {e.code}: {body[:300]}")
        return None

# ── 1. Add / update TimescaleDB datasource ──────────────────────────────────
print("\n[1] Checking existing datasources...")
existing = gf_req('GET', '/api/datasources')
pg_ds = next((d for d in existing if d.get('name') == 'TimescaleDB'), None)

ds_payload = {
    "name": "TimescaleDB",
    "type": "postgres",
    "url": f"{TIMESCALE_HOST}:{TIMESCALE_PORT}",
    "database": TIMESCALE_DB,
    "user": TIMESCALE_USER,
    "secureJsonData": {"password": TIMESCALE_PASS},
    "jsonData": {
        "sslmode": "disable",
        "maxOpenConns": 5,
        "connMaxLifetime": 14400,
        "postgresVersion": 1600,
        "timescaledb": True,
        "database": TIMESCALE_DB
    },
    "access": "proxy",
    "isDefault": False,
}

if pg_ds:
    print(f"  Found existing datasource id={pg_ds['id']}, updating...")
    result = gf_req('PUT', f"/api/datasources/{pg_ds['id']}", ds_payload)
    ds_uid = pg_ds.get('uid', '')
else:
    print("  Creating new datasource...")
    result = gf_req('POST', '/api/datasources', ds_payload)
    ds_uid = (result or {}).get('datasource', {}).get('uid', '')

print(f"  Datasource UID: {ds_uid}")

# ── 2. Import pg_stat_statements dashboard from grafana.com ─────────────────
print("\n[2] Importing pg_stat_statements dashboard...")

# Fetch the dashboard JSON from grafana.com
import urllib.request as ur
try:
    with ur.urlopen('https://grafana.com/api/dashboards/12271/revisions/7/download', timeout=20) as r:
        dash_json = json.loads(r.read())
    print(f"  Downloaded dashboard: {dash_json.get('title','?')}")

    # Replace datasource refs
    dash_str = json.dumps(dash_json)
    # Replace any ${DS_POSTGRESQL} or similar template vars
    dash_str = dash_str.replace('${DS_POSTGRESQL}', ds_uid)
    dash_str = dash_str.replace('${DS_TIMESCALEDB}', ds_uid)
    dash_json = json.loads(dash_str)

    # Fix datasource uid in all panels
    def fix_datasource(obj, uid):
        if isinstance(obj, dict):
            if obj.get('type') == 'postgres' or (isinstance(obj.get('uid'), str) and '${' in obj['uid']):
                obj['uid'] = uid
            for v in obj.values():
                fix_datasource(v, uid)
        elif isinstance(obj, list):
            for item in obj:
                fix_datasource(item, uid)
    fix_datasource(dash_json, ds_uid)
    dash_json['id'] = None  # let grafana assign new id
    dash_json['uid'] = 'pg-stat-statements'

    import_payload = {
        "dashboard": dash_json,
        "overwrite": True,
        "folderId": 0,
        "inputs": [{"name": "DS_POSTGRESQL", "type": "datasource", "pluginId": "postgres", "value": ds_uid}],
    }
    result = gf_req('POST', '/api/dashboards/import', import_payload)
    if result:
        print(f"  ✅ Dashboard imported: {result.get('importedUrl', 'check grafana')}")
    else:
        print("  ⚠️  Import might have failed, check Grafana manually")
except Exception as e:
    print(f"  ❌ Failed to fetch dashboard from grafana.com: {e}")

# ── 3. Create Z-Score CPU Anomaly Alert Rule ─────────────────────────────────
print("\n[3] Setting up Z-Score CPU anomaly alert...")

# First get the Prometheus datasource UID
prom_ds = next((d for d in (existing or []) if d.get('type') == 'prometheus'), None)
if not prom_ds:
    all_ds = gf_req('GET', '/api/datasources') or []
    prom_ds = next((d for d in all_ds if d.get('type') == 'prometheus'), None)

prom_uid = (prom_ds or {}).get('uid', 'prometheus')
print(f"  Prometheus UID: {prom_uid}")

# Get or create alert folder
folders = gf_req('GET', '/api/folders') or []
alert_folder = next((f for f in folders if f.get('title') == 'KidoOps Alerts'), None)
if not alert_folder:
    alert_folder = gf_req('POST', '/api/folders', {"title": "KidoOps Alerts"})
folder_uid = (alert_folder or {}).get('uid', '')
print(f"  Alert folder UID: {folder_uid}")

# Z-Score rule using PromQL
# Formula: (current - avg_over_time) / stddev_over_time
# If |z| > 2.5 → anomaly (2.5 standard deviations from normal = ~1% false positive rate)
zscore_rule = {
    "name": "CPU Z-Score Anomaly",
    "condition": "C",
    "data": [
        {
            "refId": "A",
            "queryType": "",
            "relativeTimeRange": {"from": 3600, "to": 0},
            "datasourceUid": prom_uid,
            "model": {
                "expr": "100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[2m])) * 100)",
                "refId": "A",
                "intervalMs": 60000,
                "maxDataPoints": 60,
            },
        },
        {
            "refId": "B",
            "queryType": "",
            "relativeTimeRange": {"from": 3600, "to": 0},
            "datasourceUid": prom_uid,
            "model": {
                # Mean over 1h rolling window
                "expr": "avg_over_time((100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[2m])) * 100))[1h:2m])",
                "refId": "B",
                "intervalMs": 60000,
                "maxDataPoints": 60,
            },
        },
        {
            "refId": "D",
            "queryType": "",
            "relativeTimeRange": {"from": 3600, "to": 0},
            "datasourceUid": prom_uid,
            "model": {
                # StdDev over 1h rolling window
                "expr": "stddev_over_time((100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[2m])) * 100))[1h:2m])",
                "refId": "D",
                "intervalMs": 60000,
                "maxDataPoints": 60,
            },
        },
        {
            # Classic reduce to get last values
            "refId": "A_reduce",
            "queryType": "",
            "relativeTimeRange": {"from": 3600, "to": 0},
            "datasourceUid": "__expr__",
            "model": {
                "type": "reduce",
                "refId": "A_reduce",
                "expression": "A",
                "reducer": "last",
                "conditions": [],
            },
        },
        {
            "refId": "B_reduce",
            "queryType": "",
            "relativeTimeRange": {"from": 3600, "to": 0},
            "datasourceUid": "__expr__",
            "model": {
                "type": "reduce",
                "refId": "B_reduce",
                "expression": "B",
                "reducer": "last",
                "conditions": [],
            },
        },
        {
            "refId": "D_reduce",
            "queryType": "",
            "relativeTimeRange": {"from": 3600, "to": 0},
            "datasourceUid": "__expr__",
            "model": {
                "type": "reduce",
                "refId": "D_reduce",
                "expression": "D",
                "reducer": "last",
                "conditions": [],
            },
        },
        {
            # Z-Score math: (current - mean) / stddev
            "refId": "ZSCORE",
            "queryType": "",
            "relativeTimeRange": {"from": 3600, "to": 0},
            "datasourceUid": "__expr__",
            "model": {
                "type": "math",
                "refId": "ZSCORE",
                "expression": "abs(($A_reduce - $B_reduce) / ($D_reduce + 0.001))",
                "conditions": [],
            },
        },
        {
            # Threshold: alert if z-score > 2.5
            "refId": "C",
            "queryType": "",
            "relativeTimeRange": {"from": 3600, "to": 0},
            "datasourceUid": "__expr__",
            "model": {
                "type": "threshold",
                "refId": "C",
                "expression": "ZSCORE",
                "conditions": [{"evaluator": {"params": [2.5], "type": "gt"}, "operator": {"type": "and"}, "query": {"params": ["ZSCORE"]}, "reducer": {"params": [], "type": "last"}, "type": "query"}],
            },
        },
    ],
    "intervalSeconds": 300,  # Evaluate every 5 minutes
    "noDataState": "OK",
    "execErrState": "Error",
    "for": "10m",  # Must be anomalous for 10 min before alerting (reduce noise)
    "labels": {"severity": "warning", "team": "kidoops"},
    "annotations": {
        "summary": "⚡ CPU Z-Score Anomaly Detected",
        "description": "CPU behavior is statistically unusual (Z-Score > 2.5σ from 1h baseline). Current CPU may be experiencing abnormal load — check for bot activity or unexpected job spikes.",
    },
    "folderUID": folder_uid,
    "ruleGroup": "zscore-alerts",
}

# Check if rule already exists
existing_rules = gf_req('GET', f'/api/ruler/grafana/api/v1/rules/{folder_uid}') or {}
rule_exists = False
for group_name, rules in existing_rules.items():
    for rule in (rules if isinstance(rules, list) else []):
        if isinstance(rule, dict) and rule.get('name') == 'CPU Z-Score Anomaly':
            rule_exists = True

if not rule_exists:
    result = gf_req('POST', '/api/ruler/grafana/api/v1/rules/' + folder_uid, {
        "name": "zscore-alerts",
        "interval": "5m",
        "rules": [zscore_rule],
    })
    if result:
        print("  ✅ Z-Score CPU anomaly alert rule created!")
    else:
        print("  ⚠️  May have failed, check Grafana Alerting > Alert rules")
else:
    print("  ℹ️  Z-Score rule already exists, skipping.")

print("\n✅ Done! Check Grafana:")
print("  - Dashboards > pg_stat_statements")
print("  - Alerting > Alert rules > KidoOps Alerts > CPU Z-Score Anomaly")
