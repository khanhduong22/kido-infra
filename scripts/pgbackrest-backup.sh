#!/bin/bash
# pgBackRest backup script
# Usage: pgbackrest-backup.sh [full|diff|incr]
# Schedule:
#   Sunday 3:30 AM    -> full (snapshot)
#   Mon/Wed/Fri 3:30  -> diff
#   Tue/Thu/Sat 3:30  -> incr

set -euo pipefail

TYPE=${1:-full}
CONTAINER=postgres
STANZA=maindb
LOG="/var/log/pgbackrest/backup-$(date +%Y%m%d-%H%M%S).log"

echo "[$(date)] Starting ${TYPE} backup for stanza ${STANZA}" | tee -a "$LOG"

docker exec -u postgres "$CONTAINER" \
  pgbackrest --stanza="$STANZA" --type="$TYPE" --log-level-console=info backup 2>&1 | tee -a "$LOG"

EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
  echo "[$(date)] ${TYPE} backup completed successfully" | tee -a "$LOG"
  # Send notification
  curl -s -X POST "https://api.telegram.org/$TELEGRAM_BOT_TOKEN/sendMessage" \
    -H "Content-Type: application/json" \
    -d "{\"chat_id\": REDACTED, \"text\": \"✅ pgBackRest ${TYPE} backup completed\nStanza: ${STANZA}\nTime: $(date '+%Y-%m-%d %H:%M')\"}" > /dev/null 2>&1
else
  echo "[$(date)] ${TYPE} backup FAILED with exit code ${EXIT_CODE}" | tee -a "$LOG"
  curl -s -X POST "https://api.telegram.org/$TELEGRAM_BOT_TOKEN/sendMessage" \
    -H "Content-Type: application/json" \
    -d "{\"chat_id\": REDACTED, \"text\": \"🔴 pgBackRest ${TYPE} backup FAILED\nStanza: ${STANZA}\nExit code: ${EXIT_CODE}\nCheck: ${LOG}\"}" > /dev/null 2>&1
fi

# Clean old logs (>30 days)
find /var/log/pgbackrest/ -name "backup-*.log" -mtime +30 -delete 2>/dev/null

exit $EXIT_CODE
