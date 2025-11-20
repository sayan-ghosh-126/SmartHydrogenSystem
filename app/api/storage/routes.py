from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import psycopg2
import psycopg2.extras
from datetime import datetime

router = APIRouter(prefix="/storage")

class StorageCreate(BaseModel):
    name: str
    capacity: float
    current_level: float
    pressure: float
    temperature: float

class StorageUpdate(BaseModel):
    pressure: float | None = None
    temperature: float | None = None
    current_level: float | None = None
    leakage_detected: bool | None = None

def conn():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise HTTPException(status_code=500, detail="DATABASE_URL not set")
    return psycopg2.connect(url)

def warnings_for(pressure: float | None, temperature: float | None, leakage: bool | None):
    w = []
    if pressure is not None and pressure > 700:
        w.append("HIGH_PRESSURE")
    if temperature is not None and temperature > 80:
        w.append("HIGH_TEMPERATURE")
    if leakage:
        w.append("LEAKAGE_DETECTED")
    return w

@router.post("/add")
def add_tank(payload: StorageCreate):
    with conn() as c:
        with c.cursor() as cur:
            cur.execute(
                "INSERT INTO storage_tanks(name, pressure, temperature, capacity, current_level, leakage_detected, updated_at) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                (
                    payload.name,
                    payload.pressure,
                    payload.temperature,
                    payload.capacity,
                    payload.current_level,
                    False,
                    datetime.utcnow(),
                ),
            )
            new_id = cur.fetchone()[0]
    return {"id": new_id}

@router.get("/all")
def all_tanks():
    with conn() as c:
        with c.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, name, pressure, temperature, capacity, current_level, leakage_detected, updated_at FROM storage_tanks ORDER BY id")
            rows = cur.fetchall()
            out = []
            for r in rows:
                w = warnings_for(r.get("pressure"), r.get("temperature"), r.get("leakage_detected"))
                out.append({
                    "id": r["id"],
                    "name": r["name"],
                    "pressure": r.get("pressure"),
                    "temperature": r.get("temperature"),
                    "current_level": r.get("current_level"),
                    "capacity": r.get("capacity"),
                    "leakage_detected": r.get("leakage_detected"),
                    "warnings": w
                })
    return out

@router.put("/update/{id}")
def update_tank(id: int, payload: StorageUpdate):
    fields = []
    values = []
    if payload.pressure is not None:
        fields.append("pressure=%s")
        values.append(payload.pressure)
    if payload.temperature is not None:
        fields.append("temperature=%s")
        values.append(payload.temperature)
    if payload.current_level is not None:
        fields.append("current_level=%s")
        values.append(payload.current_level)
    if payload.leakage_detected is not None:
        fields.append("leakage_detected=%s")
        values.append(payload.leakage_detected)
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    values.append(datetime.utcnow())
    values.append(id)
    with conn() as c:
        with c.cursor() as cur:
            cur.execute(
                f"UPDATE storage_tanks SET {', '.join(fields)}, updated_at=%s WHERE id=%s",
                values,
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Tank not found")
    return {"updated": True}