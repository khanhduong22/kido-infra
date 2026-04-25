# VPS Operations Runbook

## Server Info
- **VPS**: Contabo 4 vCores / 8GB RAM / 145GB SSD
- **OS**: Ubuntu 24.04
- **Host**: vmi3171169

## Cron Jobs

| Schedule | Task | Log |
|----------|------|-----|
| `0 2 * * *` | Backup DB (`/root/backup-db.sh`) | `/var/log/backup-db.log` |
| `0 */4 * * *` | Docker image prune (>4h unused) | `/var/log/docker-prune.log` |
| `0 4 * * 0` | Restart Docker daemon | `/var/log/docker-restart.log` |

## Docker Config
- **daemon.json**: `/etc/docker/daemon.json`
  - Log: max 10MB x 3 files
  - Build cache cap: 12GB

## Services & Ports

| Service | Container | Port | URL |
|---------|-----------|------|-----|
| Grafana | grafana | 3000 | https://grafana.khanhdp.com |
| SigNoz | signoz | 8088 | https://signoz.khanhdp.com |
| ClickHouse | signoz-clickhouse | 8123/9000 | internal |
| ZooKeeper | signoz-zookeeper-1 | 2181 | internal |
| Otel Collector | signoz-otel-collector | 4317/4318 | internal |
| Portainer | portainer | 9000 | internal (via NPM) |
| Dozzle | dozzle | 8080 | internal |
| Uptime Kuma | uptime-kuma | 3002→3001 | internal |
| Nginx Proxy Manager | nginx-proxy-manager | 81/80/443 | internal |
| IT Tools | it-tools | 8086 | internal |

## Known Issues & Fixes

### Portainer healthcheck fails
- **Issue**: Portainer CE không có `curl` hay `wget` → healthcheck fail → dockerd spam errors → CPU spike
- **Fix**: healthcheck đổi thành `echo 'ok'` trong `/opt/kido-infra/common/docker-compose.yml`
- **Lesson**: Không dùng curl/wget trong healthcheck cho Portainer CE

### Docker/containerd CPU leak
- **Issue**: Sau ~30 ngày uptime, dockerd + containerd ăn >100% CPU
- **Fix**: Cron restart Docker mỗi Chủ nhật 4:00 AM
- **Symptom**: Load average > 10 trên 4 cores

### SigNoz architecture
- **SigNoz BẮT BUỘC** chạy cluster mode với Zookeeper + Distributed tables
- **KHÔNG** convert ReplicatedMergeTree → MergeTree → sẽ mất data
- SigNoz managed via: `/opt/signoz/deploy/docker/`
- Schema migrations chạy qua `signoz-telemetrystore-migrator` container

### Grafana ClickHouse queries
- Data source UID: `afk5t1ojwwbuod` (ClickHouse-SigNoz)
- Data source UID: `bfinlnsq4hkw0e` (TimescaleDB)
- ClickHouse plugin format: `"format": 1` (table), KHÔNG dùng `"format": "time_series"`
- Join `time_series_v4` để lấy labels: `JSONExtractString(t.labels, 'container.name')`
- Time column: `unix_milli` (Int64), convert bằng `fromUnixTimestamp64Milli(unix_milli)`
- Filter memory: `state = 'used'`, disk: `device = '/dev/sda1' AND state = 'used'`

## Useful Commands

```bash
# Check system health
uptime && free -h && df -h /

# Docker container stats
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Restart SigNoz stack
cd /opt/signoz/deploy/docker && docker compose up -d

# Check ClickHouse tables
docker exec signoz-clickhouse clickhouse-client -q "SHOW TABLES FROM signoz_metrics"

# Check ClickHouse data size
docker exec signoz-clickhouse clickhouse-client -q "SELECT database, formatReadableSize(sum(bytes)) FROM system.parts GROUP BY database"

# Grafana API (admin auth)
curl -s http://localhost:3000/api/datasources -u "admin:KidoOps2026!"
```
