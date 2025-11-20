from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import psycopg2
import psycopg2.extras
from datetime import datetime
import math
import random

router = APIRouter(prefix="/transport")

class AddVehicle(BaseModel):
    vehicle_id: str
    mode: str
    location: str | None = None
    status: str | None = None
    hydrogen_load: float | None = None
    destination: str | None = None

class RouteRequest(BaseModel):
    start_location: str
    end_location: str
    hydrogen_load: float

def conn():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise HTTPException(status_code=500, detail="DATABASE_URL not set")
    return psycopg2.connect(url)

def parse_coords(s: str):
    try:
        parts = [p.strip() for p in s.split(",")]
        if len(parts) == 2:
            return float(parts[0]), float(parts[1])
    except Exception:
        pass
    return None

def haversine_km(a, b):
    (lat1, lon1) = a
    (lat2, lon2) = b
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    sa = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(sa), math.sqrt(1 - sa))
    return R * c

def simulate_weather():
    w = random.choice(["Clear", "Rain", "Storm", "Fog", "Snow"])
    risk = {"Clear": 0, "Rain": 10, "Storm": 30, "Fog": 15, "Snow": 20}[w]
    return w, risk

def simulate_population_risk(distance_km: float):
    base = 5 if distance_km < 100 else 10 if distance_km < 300 else 15
    return base + random.uniform(0, 15)

@router.post("/add-vehicle")
def add_vehicle(payload: AddVehicle):
    with conn() as c:
        with c.cursor() as cur:
            cur.execute(
                "INSERT INTO transport_fleet(vehicle_id, mode, location, status, hydrogen_load, destination) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
                (
                    payload.vehicle_id,
                    payload.mode,
                    payload.location,
                    payload.status or "idle",
                    payload.hydrogen_load,
                    payload.destination,
                ),
            )
            new_id = cur.fetchone()[0]
    return {"id": new_id}

@router.get("/fleet")
def fleet():
    with conn() as c:
        with c.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, vehicle_id, mode, location, status, hydrogen_load, destination FROM transport_fleet ORDER BY id")
            rows = cur.fetchall()
    return rows

@router.post("/optimal-route")
def optimal_route(req: RouteRequest):
    a = parse_coords(req.start_location)
    b = parse_coords(req.end_location)
    if a and b:
        base_distance = haversine_km(a, b)
    else:
        base_distance = random.uniform(50, 1000)

    candidates = []
    for factor in [0.95, 1.0, 1.1]:
        dist = base_distance * factor
        weather, w_risk = simulate_weather()
        p_risk = simulate_population_risk(dist)
        total_risk = dist + w_risk + p_risk
        speed_kmh = 60.0
        eta_hours = dist / speed_kmh
        candidates.append({
            "route": {
                "waypoints": [req.start_location, req.end_location],
            },
            "distance_km": round(dist, 3),
            "estimated_time_hours": round(eta_hours, 2),
            "weather": weather,
            "risk_score": round(total_risk, 3),
            "details": {
                "weather_risk": round(w_risk, 2),
                "population_density_risk": round(p_risk, 2),
                "algorithm": "distance + weather_risk + population_density_risk",
            },
        })

    best = min(candidates, key=lambda x: x["risk_score"])
    best["safest"] = True
    return {"start": req.start_location, "end": req.end_location, "hydrogen_load": req.hydrogen_load, "selected": best, "candidates": candidates}