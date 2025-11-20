from typing import List, Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi import Request

from .transport_ml import init_model
from .routes.transport import router as transport_router, _seed_fleet
from fastapi import APIRouter
from dotenv import load_dotenv
from .simulator import Simulator


app = FastAPI(title="Smart Hydrogen Transport API")

cors_env = os.getenv("CORS_ORIGINS", "*")
origins = [o.strip() for o in cors_env.split(",")] if cors_env else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")
api_router.include_router(transport_router)
app.include_router(api_router)


sim = Simulator()


@app.on_event("startup")
async def startup_event():
    load_dotenv()
    init_model()
    sim.set_fleet(_seed_fleet())
    sim.start()


@app.get("/api/stream")
async def stream():
    return await sim.stream()


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/system/traffic")
def system_traffic():
    return {"traffic": sim.state.get("traffic", 0.5)}


@app.get("/api/system/weather")
def system_weather():
    return {"weather": sim.state.get("weather", 0.5)}


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)