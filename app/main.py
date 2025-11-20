from fastapi import FastAPI
from .api.production.routes import router as production_router
from .api.storage.routes import router as storage_router
from .api.transport.routes import router as transport_router
from .api.prediction.routes import router as prediction_router
import threading
import time
import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from pathlib import Path

app = FastAPI()
app.include_router(production_router)
app.include_router(storage_router)
app.include_router(transport_router)
app.include_router(prediction_router)
try:
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
except Exception:
    pass

def compute_output(unit_type: str, hour: int, max_capacity: float) -> float:
    if unit_type.lower() == "solar":
        if 8 <= hour <= 18:
            peak = 1.0
            distance = abs(13 - hour) / 5
            factor = max(0.0, peak - distance)
        else:
            factor = 0.1
        return round(max_capacity * factor, 6)
    if unit_type.lower() == "wind":
        if hour >= 18 or hour < 8:
            factor = 0.8
        else:
            factor = 0.4
        return round(max_capacity * factor, 6)
    if unit_type.lower() == "hydro":
        return round(max_capacity * 0.6, 6)
    return 0.0

def update_loop():
    url = os.getenv("DATABASE_URL")
    if not url:
        return
    while True:
        try:
            with psycopg2.connect(url) as c:
                with c.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("SELECT id, type, max_capacity FROM production_units")
                    rows = cur.fetchall()
                    now = datetime.utcnow()
                    hour = now.hour
                    for r in rows:
                        mc = r.get("max_capacity")
                        if mc is None:
                            continue
                        out = compute_output(r.get("type", ""), hour, float(mc))
                        cur.execute(
                            "UPDATE production_units SET current_output=%s, updated_at=%s WHERE id=%s",
                            (out, now, r["id"]),
                        )
        except Exception:
            pass
        time.sleep(10)

_thread = None
_storage_thread = None

@app.on_event("startup")
def start_updater():
    global _thread
    run_migrations()
    if _thread is None:
        _thread = threading.Thread(target=update_loop, daemon=True)
        _thread.start()
    global _storage_thread
    if _storage_thread is None:
        _storage_thread = threading.Thread(target=storage_update_loop, daemon=True)
        _storage_thread.start()

@app.get("/")
def root():
    return {"status": "SmartHydrogenSystem backend"}

@app.get("/health")
def health():
    try:
        url = os.getenv("DATABASE_URL")
        if not url:
            return {"status": "ok", "db": "not_configured"}
        with psycopg2.connect(url) as c:
            with c.cursor() as cur:
                cur.execute("SELECT 1")
        return {"status": "ok", "db": "connected"}
    except Exception:
        return {"status": "degraded", "db": "error"}

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def storage_update_loop():
    url = os.getenv("DATABASE_URL")
    if not url:
        return
    import random
    while True:
        try:
            with psycopg2.connect(url) as c:
                with c.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("SELECT id, capacity, current_level, pressure, temperature, leakage_detected FROM storage_tanks")
                    rows = cur.fetchall()
                    now = datetime.utcnow()
                    for r in rows:
                        cap = float(r.get("capacity") or 0)
                        lvl = float(r.get("current_level") or 0)
                        prs = float(r.get("pressure") or 0)
                        tmp = float(r.get("temperature") or 25)
                        leak = bool(r.get("leakage_detected") or False)
                        prs += random.uniform(-5, 5)
                        target = cap * 0.5
                        delta = random.uniform(-cap * 0.01, cap * 0.01)
                        lvl = clamp(lvl + delta, 0, cap)
                        tmp += random.uniform(-1.5, 1.5)
                        if random.random() < 0.01:
                            leak = True
                        if leak:
                            lvl = clamp(lvl - abs(delta) * 2, 0, cap)
                            prs = clamp(prs - 10, 0, 1000)
                        cur.execute(
                            "UPDATE storage_tanks SET pressure=%s, temperature=%s, current_level=%s, leakage_detected=%s, updated_at=%s WHERE id=%s",
                            (prs, tmp, lvl, leak, now, r["id"]),
                        )
        except Exception:
            pass
        time.sleep(10)

def run_migrations():
    url = os.getenv("DATABASE_URL")
    if not url:
        return
    schema_env = os.getenv("SCHEMA_PATH")
    if schema_env and Path(schema_env).exists():
        schema_path = Path(schema_env)
    else:
        schema_path = Path(__file__).resolve().parent.parent / "db" / "schema.sql"
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            sql = f.read()
        with psycopg2.connect(url) as c:
            with c.cursor() as cur:
                cur.execute(sql)
    except Exception:
        pass