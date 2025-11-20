from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import psycopg2
import psycopg2.extras
from datetime import datetime

router = APIRouter(prefix="/production")

class ProductionCreate(BaseModel):
    name: str
    type: str
    renewable_source: str | None = None
    max_capacity: float

class OutputUpdate(BaseModel):
    current_output: float

def conn():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise HTTPException(status_code=500, detail="DATABASE_URL not set")
    return psycopg2.connect(url)

@router.post("/add")
def add_unit(payload: ProductionCreate):
    with conn() as c:
        with c.cursor() as cur:
            cur.execute(
                "INSERT INTO production_units(name, type, renewable_source, current_output, max_capacity, updated_at) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
                (
                    payload.name,
                    payload.type,
                    payload.renewable_source,
                    0,
                    payload.max_capacity,
                    datetime.utcnow(),
                ),
            )
            new_id = cur.fetchone()[0]
    return {"id": new_id}

@router.get("/all")
def all_units():
    with conn() as c:
        with c.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, name, type, renewable_source, current_output, max_capacity, updated_at FROM production_units ORDER BY id")
            rows = cur.fetchall()
    return rows

@router.put("/update-output/{id}")
def update_output(id: int, payload: OutputUpdate):
    with conn() as c:
        with c.cursor() as cur:
            cur.execute(
                "UPDATE production_units SET current_output=%s, updated_at=%s WHERE id=%s",
                (payload.current_output, datetime.utcnow(), id),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Unit not found")
    return {"updated": True}