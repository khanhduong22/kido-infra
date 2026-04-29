#!/bin/bash
set -e

echo "Building Knowledge Graph for /workspace..."
# Allow running even if directory has git config owned by another user (common in docker volumes)
git config --global --add safe.directory /workspace || true

gkg index

echo "Starting Knowledge Graph Server..."
exec gkg server start --host 0.0.0.0 --port 27495
