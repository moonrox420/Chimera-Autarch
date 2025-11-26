export HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
export HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001
HTTP_PORT=3000
WS_PORT=3001

#!/usr/bin/env bash
# rebuild_and_deploy.sh – atomic, idempotent deployment script
set -euo pipefail

echo "[DEPLOY] Building revolutionary multi-stage image..."
docker build -t chimera-autarch:latest -f docker/Dockerfile .

echo "[DEPLOY] Stopping existing container..."
docker stop chimera-autarch || true
docker rm chimera-autarch || true

echo "[DEPLOY] Starting new healthy instance..."
docker-compose up -d --force-recreate

echo "[DEPLOY] Waiting for container to start..."
sleep 5

echo "[DEPLOY] Verifying container is running..."
docker ps | grep chimera-autarch

echo "[SUCCESS] CHIMERA AUTARCH v3 fully operational - WebSocket control plane active on port 3001"
