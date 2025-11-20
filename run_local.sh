#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -f "frontend/.env.local" ]; then
  set -a
  . frontend/.env.local
  set +a
fi

API_ARG=${VITE_API_BASE_URL:-http://backend:8000/api}

echo "Building containers with API base: $API_ARG"
docker compose build --build-arg VITE_API_BASE_URL="$API_ARG"
docker compose up -d

echo "Frontend: http://localhost"
echo "Backend: http://localhost:8000"
echo "API Health: http://localhost/api/health"