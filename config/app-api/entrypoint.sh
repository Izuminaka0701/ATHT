#!/bin/sh
set -eu

# Bind chỉ trên IP của miền APP — resolve qua DNS Docker
APP_IP="$(python3 -c "import socket; print(socket.gethostbyname('app-api'))")"
export BIND_ADDRESS="${BIND_ADDRESS:-$APP_IP}"

echo "[app-api] Binding to ${BIND_ADDRESS}:${BIND_PORT:-5000}"

exec gunicorn \
  --bind "${BIND_ADDRESS}:${BIND_PORT:-5000}" \
  --workers 1 \
  --timeout 30 \
  --access-logfile - \
  app:app
