#!/usr/bin/env bash
# Ghim digest ảnh Docker vào compose/docker-compose.yml
set -euo pipefail

IMAGES=(
  "nginx:1.27-alpine"
  "postgres:16-alpine"
  "alpine:3.20"
  "python:3.12-slim-bookworm"
)

COMPOSE="compose/docker-compose.yml"

for img in "${IMAGES[@]}"; do
  echo "Pulling ${img}..."
  docker pull "${img}" >/dev/null
  DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' "${img}" 2>/dev/null | cut -d@ -f2)
  if [ -n "${DIGEST}" ]; then
    echo "  ${img}@${DIGEST}"
  fi
done

echo "Cập nhật thủ công digest trong ${COMPOSE} từ output trên."
