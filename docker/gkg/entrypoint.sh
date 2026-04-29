#!/bin/bash
set -e

echo "Building Knowledge Graph for /workspace..."
# Allow running even if directory has git config owned by another user (common in docker volumes)
git config --global --add safe.directory /workspace || true

gkg index

echo "Starting Knowledge Graph Server..."
gkg server start --port 27496 &
sleep 2
exec socat TCP-LISTEN:27495,fork,bind=0.0.0.0 TCP:127.0.0.1:27496
