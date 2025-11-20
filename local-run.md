# Local Run

## One-command run
```
./run_local.sh
```

## URLs
- Frontend: http://localhost
- Backend: http://localhost:8000
- API Health: http://localhost/api/health

## Notes
- `run_local.sh` reads `frontend/.env.local` and passes `VITE_API_BASE_URL` into the build.
- Docker compose builds and starts both services.