#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker &>/dev/null; then
  echo "Docker is required" && exit 1
fi

COMPOSE_CMD="docker compose"
if ! docker compose version &>/dev/null; then
  if command -v docker-compose &>/dev/null; then
    COMPOSE_CMD="docker-compose"
  else
    echo "Docker Compose v2 or v1 is required" && exit 1
  fi
fi

DIR=$(cd "$(dirname "$0")" && pwd)
cd "$DIR"

echo "Using env file .env.production"

echo "Building images"
$COMPOSE_CMD --env-file ./.env.production -f docker-compose.yml build

echo "Starting services"
$COMPOSE_CMD --env-file ./.env.production -f docker-compose.yml up -d

echo "Waiting for services to become healthy"
sleep 5

echo "Health check backend"
curl -sS http://localhost/api/health || curl -sS http://localhost:8000/health || true

echo "Verifying services"
$COMPOSE_CMD --env-file ./.env.production -f docker-compose.yml ps

BACKEND_STATUS=$($COMPOSE_CMD --env-file ./.env.production -f docker-compose.yml ps | awk '/backend/ {print $4}')
if [[ "$BACKEND_STATUS" != "Up"* ]]; then
  echo "Backend not healthy, rebuilding and showing logs"
  $COMPOSE_CMD --env-file ./.env.production -f docker-compose.yml build backend
  $COMPOSE_CMD --env-file ./.env.production -f docker-compose.yml up -d backend
  $COMPOSE_CMD -f docker-compose.yml logs backend --tail=200 || true
fi

echo "Done"