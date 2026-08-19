#!/bin/sh
set -eu

# Cổng kiểm soát APP→DATA: TCP proxy duy nhất tới PostgreSQL
# Chỉ forward cổng 5432, không expose dịch vụ khác

DATA_HOST="${DATA_HOST:-data-db}"
DATA_PORT="${DATA_PORT:-5432}"
LISTEN_PORT="${LISTEN_PORT:-5432}"

echo "[gateway-app-data] Proxy ${LISTEN_PORT} -> ${DATA_HOST}:${DATA_PORT}"

exec socat \
  "TCP-LISTEN:${LISTEN_PORT},fork,reuseaddr,bind=0.0.0.0" \
  "TCP:${DATA_HOST}:${DATA_PORT}"
