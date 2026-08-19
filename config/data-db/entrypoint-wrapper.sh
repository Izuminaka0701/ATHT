#!/bin/sh
set -eu

# Bind PostgreSQL chỉ trên IP miền DATA
DATA_IP="$(hostname -i | awk '{print $1}')"

echo "[data-db] listen_addresses=${DATA_IP}"

exec docker-entrypoint.sh postgres \
  -c "config_file=/etc/postgresql/postgresql.conf" \
  -c "hba_file=/etc/postgresql/pg_hba.conf" \
  -c "listen_addresses=${DATA_IP}"
