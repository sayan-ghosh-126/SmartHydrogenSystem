#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -f "frontend/.env.local" ]; then
  set -a
  . frontend/.env.local
  set +a
fi

echo "Installing backend deps"
python -m pip install --upgrade pip || true
pip install -r backend/requirements.txt

echo "Installing frontend deps"
cd frontend
npm install
cd ..

echo "Starting backend on :8000"
python -m backend.server &
BACK_PID=$!

echo "Starting frontend dev on :5173"
cd frontend
npm run dev -- --host 0.0.0.0 &
FRONT_PID=$!
cd ..

(sleep 2 && (command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:5173 || (command -v open >/dev/null 2>&1 && open http://localhost:5173) || echo "Open http://localhost:5173")) &

echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Health: http://localhost:8000/api/health"

wait $BACK_PID $FRONT_PID