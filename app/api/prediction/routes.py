from fastapi import APIRouter, HTTPException
import os
import psycopg2
import psycopg2.extras
from datetime import datetime
import math

router = APIRouter()

def conn():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise HTTPException(status_code=500, detail="DATABASE_URL not set")
    return psycopg2.connect(url)

def linear_regression_next(values):
    n = len(values)
    if n == 0:
        return 0.0
    if n == 1:
        return float(values[0])
    xs = list(range(n))
    mean_x = sum(xs) / n
    mean_y = sum(values) / n
    cov = sum((xs[i] - mean_x) * (values[i] - mean_y) for i in range(n))
    var = sum((xs[i] - mean_x) ** 2 for i in range(n))
    if var == 0:
        return float(values[-1])
    b = cov / var
    a = mean_y - b * mean_x
    next_x = n
    return float(a + b * next_x)

def solar_availability(hour):
    if 8 <= hour <= 18:
        peak = 1.0
        d = abs(13 - hour) / 5
        f = max(0.0, peak - d)
    else:
        f = 0.1
    return max(0.0, min(1.0, f))

def wind_availability(hour):
    if hour >= 18 or hour < 8:
        f = 0.8
    else:
        f = 0.4
    return f

def hydro_availability():
    return 0.6

@router.get("/prediction/demand")
def predict_demand():
    with conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT DATE(timestamp) AS d, SUM(demand_value) FROM demand_logs GROUP BY d ORDER BY d")
            rows = cur.fetchall()
            vals = [float(r[1]) for r in rows]
    pred = linear_regression_next(vals)
    return {"predicted_next_day_demand": round(pred, 3), "history_days": len(vals)}

@router.get("/prediction/renewable")
def predict_renewable():
    now = datetime.utcnow()
    h = now.hour
    solar = solar_availability(h)
    wind = wind_availability(h)
    hydro = hydro_availability()
    return {"solar": round(solar, 3), "wind": round(wind, 3), "hydro": round(hydro, 3), "hour": h}

@router.get("/prediction/storage-alerts")
def storage_alerts():
    with conn() as c:
        with c.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, capacity, current_level FROM storage_tanks")
            tanks = cur.fetchall()
            cur.execute("SELECT SUM(max_capacity) FROM production_units")
            pc = cur.fetchone()[0]
            cur.execute("SELECT DATE(timestamp) AS d, SUM(demand_value) FROM demand_logs GROUP BY d ORDER BY d")
            rows = cur.fetchall()
            vals = [float(r[1]) for r in rows]
    pred = linear_regression_next(vals)
    alerts = []
    total_capacity = float(pc or 0)
    for t in tanks:
        cap = float(t.get("capacity") or 0)
        lvl = float(t.get("current_level") or 0)
        pct = 0.0 if cap == 0 else (lvl / cap) * 100.0
        w = []
        if pct < 10.0:
            w.append("LOW_STORAGE")
        if pct > 90.0:
            w.append("HIGH_STORAGE")
        if w:
            alerts.append({"tank_id": t["id"], "level_percent": round(pct, 2), "alerts": w})
    production_alert = pred > total_capacity
    return {"predicted_demand": round(pred, 3), "production_capacity_total": round(total_capacity, 3), "demand_exceeds_capacity": production_alert, "tank_alerts": alerts}

@router.get("/dashboard/summary")
def dashboard_summary():
    with conn() as c:
        with c.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) AS count, COALESCE(SUM(max_capacity),0) AS total_max, COALESCE(SUM(current_output),0) AS total_out FROM production_units")
            prod_sum = cur.fetchone()
            cur.execute("SELECT COUNT(*) AS count, COALESCE(SUM(capacity),0) AS total_cap, COALESCE(SUM(current_level),0) AS total_level FROM storage_tanks")
            stor_sum = cur.fetchone()
            cur.execute("SELECT COUNT(*) AS count FROM transport_fleet")
            fleet_sum = cur.fetchone()
            cur.execute("SELECT DATE(timestamp) AS d, SUM(demand_value) FROM demand_logs GROUP BY d ORDER BY d")
            rows = cur.fetchall()
            vals = [float(r[1]) for r in rows]
    pred = linear_regression_next(vals)
    now = datetime.utcnow()
    h = now.hour
    renewable = {"solar": round(solar_availability(h), 3), "wind": round(wind_availability(h), 3), "hydro": round(hydro_availability(), 3)}
    summary = {
        "production": {
            "units": prod_sum.get("count"),
            "total_max_capacity": float(prod_sum.get("total_max")),
            "total_current_output": float(prod_sum.get("total_out")),
        },
        "storage": {
            "tanks": stor_sum.get("count"),
            "total_capacity": float(stor_sum.get("total_cap")),
            "total_level": float(stor_sum.get("total_level")),
        },
        "transport": {
            "fleet_size": fleet_sum.get("count"),
        },
        "predictions": {
            "next_day_demand": round(pred, 3),
            "renewable": renewable,
        },
    }
    return summary