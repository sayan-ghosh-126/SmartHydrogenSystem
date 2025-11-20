# Cloud Deploy (Railway / Render)

## Railway (preferred)
- Ensure you have a Railway account.
- From project root, deploy with Railway using `railway.json`:
  - Create two services (backend, frontend) by importing the repo.
  - Set env for frontend: `VITE_API_BASE_URL=https://<backend-domain>/api`.
  - Railway will build using the Dockerfiles provided.

## Render (fallback)
- From project root, click "New +" → "Blueprint" and select `render.yaml`.
- Render will create two Web Services (backend, frontend) and build via Docker.
- Set `VITE_API_BASE_URL` for frontend to point to backend public URL.

## Live URLs
- Backend: https://smart-hydrogen-backend.onrender.com (example)
- Frontend: https://smart-hydrogen-frontend.onrender.com (example)