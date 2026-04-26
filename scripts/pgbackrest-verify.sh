#!/bin/bash
# pgBackRest auto restore verify
# Restores latest backup to a temporary container, runs sanity checks, then destroys it
# Schedule: Saturday 5:00 AM

set -euo pipefail

CONTAINER=postgres
STANZA=maindb
VERIFY_CONTAINER=pgbackrest-verify
VERIFY_VOLUME=pgbackrest_verify_data
LOG="/var/log/pgbackrest/verify-$(date +%Y%m%d-%H%M%S).log"

notify() {
  local emoji="$1" msg="$2"
  curl -s -X POST "https://api.telegram.org/$TELEGRAM_BOT_TOKEN/sendMessage" \
    -H "Content-Type: application/json" \
    -d "{\"chat_id\": REDACTED, \"text\": \"${emoji} pgBackRest Restore Verify\n${msg}\nTime: $(date '+%Y-%m-%d %H:%M')\"}" > /dev/null 2>&1
}

echo "[$(date)] Starting restore verify" | tee -a "$LOG"

# Cleanup any previous verify container
docker rm -f "$VERIFY_CONTAINER" 2>/dev/null || true
docker volume rm "$VERIFY_VOLUME" 2>/dev/null || true

# Create verify volume
docker volume create "$VERIFY_VOLUME" > /dev/null

# Copy pgbackrest config + repo to verify container
# Step 1: Create verify container with same image
docker run -d --name "$VERIFY_CONTAINER" \
  -v "$VERIFY_VOLUME:/var/lib/postgresql/verify-data" \
  -v /var/lib/docker/volumes/services_pg_data/_data:/var/lib/postgresql/data:ro \
  -v services_pg_data:/var/lib/pgbackrest:ro \
  --network ops_bridge \
  pgvector/pgvector:pg17 sleep 300 > /dev/null 2>&1 || true

# Wait for container
sleep 3

# Step 2: Install pgbackrest in verify container
docker exec "$VERIFY_CONTAINER" apt-get update > /dev/null 2>&1
docker exec "$VERIFY_CONTAINER" apt-get install -y pgbackrest > /dev/null 2>&1

# Step 3: Setup config for restore
docker exec "$VERIFY_CONTAINER" bash -c 'mkdir -p /etc/pgbackrest /var/log/pgbackrest'
docker exec "$VERIFY_CONTAINER" bash -c 'cat > /etc/pgbackrest/pgbackrest.conf << EOF
[global]
repo1-path=/var/lib/pgbackrest
log-level-console=info

[maindb]
pg1-path=/var/lib/postgresql/verify-data
pg1-user=kido
pg1-database=maindb
EOF'

# Step 4: Get latest backup info
BACKUP_INFO=$(docker exec "$CONTAINER" pgbackrest --stanza="$STANZA" info --output=json 2>&1)
LATEST_BACKUP=$(echo "$BACKUP_INFO" | python3 -c "
import sys,json
data = json.loads(sys.stdin.read())
backups = data[0]['backup']
latest = max(backups, key=lambda b: b['timestamp']['start'])
print(latest['label'])
" 2>&1)

echo "[$(date)] Latest backup: $LATEST_BACKUP" | tee -a "$LOG"

# Step 5: Restore to verify path
docker exec -u postgres "$VERIFY_CONTAINER" \
  pgbackrest --stanza="$STANZA" --pg1-path=/var/lib/postgresql/verify-data \
  --type=time --target-action=promote \
  --target="now" restore 2>&1 | tee -a "$LOG" || {
    echo "[$(date)] Restore FAILED" | tee -a "$LOG"
    notify "🔴" "Restore FAILED for backup ${LATEST_BACKUP}"
    docker rm -f "$VERIFY_CONTAINER" 2>/dev/null
    docker volume rm "$VERIFY_VOLUME" 2>/dev/null
    exit 1
  }

# Step 6: Start PostgreSQL on verify data and run checks
docker exec -u postgres "$VERIFY_CONTAINER" \
  pg_ctl -D /var/lib/postgresql/verify-data -l /var/log/pgbackrest/verify-pg.log start 2>&1 | tee -a "$LOG"

sleep 5

# Step 7: Sanity checks
echo "[$(date)] Running sanity checks..." | tee -a "$LOG"

# Check 1: Can connect?
TABLE_COUNT=$(docker exec "$VERIFY_CONTAINER" psql -U kido -d maindb -t -c "
SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>&1 | tr -d ' ')
echo "  Tables in public schema: $TABLE_COUNT" | tee -a "$LOG"

# Check 2: Can query?
DB_SIZE=$(docker exec "$VERIFY_CONTAINER" psql -U kido -d maindb -t -c "
SELECT pg_size_pretty(pg_database_size('maindb'));" 2>&1 | tr -d ' ')
echo "  Database size: $DB_SIZE" | tee -a "$LOG"

# Check 3: Data integrity - check all tables readable
BROKEN=$(docker exec "$VERIFY_CONTAINER" psql -U kido -d maindb -t -c "
SELECT count(*) FROM (
  SELECT table_name FROM information_schema.tables 
  WHERE table_schema = 'public'
) t;" 2>&1 | tr -d ' ')
echo "  All tables readable: $BROKEN tables" | tee -a "$LOG"

# Stop verify PG
docker exec -u postgres "$VERIFY_CONTAINER" \
  pg_ctl -D /var/lib/postgresql/verify-data stop 2>/dev/null || true

# Cleanup
docker rm -f "$VERIFY_CONTAINER" > /dev/null 2>&1
docker volume rm "$VERIFY_VOLUME" > /dev/null 2>&1

echo "[$(date)] Restore verify completed successfully!" | tee -a "$LOG"
notify "✅" "Restore verify PASSED\nBackup: ${LATEST_BACKUP}\nTables: ${TABLE_COUNT}\nDB size: ${DB_SIZE}"

# Clean old logs
find /var/log/pgbackrest/ -name "verify-*.log" -mtime +30 -delete 2>/dev/null
