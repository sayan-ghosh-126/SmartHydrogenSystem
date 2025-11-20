from typing import List, Dict, Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ..transport_logic import evaluate_vehicle


router = APIRouter()


class AssignBody(BaseModel):
    vehicle_id: str
    destination: List[float]
    hydrogen_load: float


_VEHICLES: Dict[str, Dict[str, Any]] = {}


def _seed_fleet() -> List[Dict[str, Any]]:
    modes = ["truck", "pipeline", "tanker", "cargo ship"]
    statuses = ["idle", "en-route", "maintenance", "loading"]
    base_points = [
        (37.7749, -122.4194),
        (34.0522, -118.2437),
        (40.7128, -74.0060),
        (41.8781, -87.6298),
        (47.6062, -122.3321),
        (29.7604, -95.3698),
        (51.5074, -0.1278),
        (48.8566, 2.3522),
        (35.6895, 139.6917),
        (52.5200, 13.4050),
    ]
    dest_points = [
        (36.1699, -115.1398),
        (32.7157, -117.1611),
        (42.3601, -71.0589),
        (39.9526, -75.1652),
        (45.5152, -122.6784),
        (25.7617, -80.1918),
        (55.7558, 37.6173),
        (41.9028, 12.4964),
        (37.5665, 126.9780),
        (50.1109, 8.6821),
    ]
    fleet = []
    loads = [12000, 28000, 45000, 75000, 150000, 300000, 800000, 50000, 90000, 220000]
    for i in range(10):
        v = {
            "id": f"veh-{i+1}",
            "vehicle_id": f"VH{i+1:03d}",
            "mode": modes[i % len(modes)],
            "status": statuses[i % len(statuses)],
            "load": float(loads[i % len(loads)]),
            "current_location": [base_points[i][0], base_points[i][1]],
            "destination": [dest_points[i][0], dest_points[i][1]],
        }
        _VEHICLES[v["vehicle_id"]] = v
        fleet.append(v)
    return fleet


@router.get("/fleet")
def fleet(decision_mode: str = Query("ml")):
    if not _VEHICLES:
        _seed_fleet()
    enriched = []
    for v in _VEHICLES.values():
        d = evaluate_vehicle(v, decision_mode=decision_mode)
        enriched.append({**v, **d})
    return enriched


@router.post("/fleet/assign")
def assign(body: AssignBody):
    if body.vehicle_id not in _VEHICLES:
        return {"ok": False, "error": "unknown vehicle"}
    v = _VEHICLES[body.vehicle_id]
    v["destination"] = body.destination
    v["load"] = float(body.hydrogen_load)
    d = evaluate_vehicle(v, decision_mode="ml")
    _VEHICLES[body.vehicle_id] = {**v}
    return {"ok": True, "vehicle": {**v, **d}}


@router.post("/train")
def train_model():
    from ..transport_ml import train_model, init_model
    train_model()
    init_model()
    return {"ok": True, "message": "model retrained"}


@router.get("/history")
def history():
    return []

@router.get("/route")
def route(source: str, destination: str):
    try:
        slat, slon = [float(x) for x in source.split(",")]
        dlat, dlon = [float(x) for x in destination.split(",")]
    except Exception:
        return {"ok": False, "error": "invalid source/destination"}
    from ..transport_logic import osrm_route, compute_distance
    info = osrm_route((slat, slon), (dlat, dlon))
    if not info.get("distance_km"):
        info["distance_km"] = compute_distance((slat, slon), (dlat, dlon))
        info["approximate"] = True
    return {"ok": True, "route": info}

class OptimizeBody(BaseModel):
    destination: List[float]
    hydrogen_load: float

@router.post("/fleet/optimize")
def fleet_optimize(body: OptimizeBody):
    if not _VEHICLES:
        _seed_fleet()
    best = None
    best_eff = -1
    from ..transport_logic import evaluate_vehicle
    for v in _VEHICLES.values():
        vv = {**v, "destination": body.destination, "load": float(body.hydrogen_load)}
        d = evaluate_vehicle(vv, decision_mode="ml")
        eff = d.get("efficiency_score", 0)
        if eff > best_eff:
            best_eff = eff
            best = {**vv, **d}
    eta_min = best.get("recommended_route", {}).get("duration_min") if best else None
    energy_cost = best.get("cost_estimate") if best else None
    return {"ok": True, "best": best, "eta_min": eta_min, "energy_cost": energy_cost}

class DemandBody(BaseModel):
    region: str
    weather_risk: float = 0.3
    traffic_score: float = 0.5

@router.post("/demand/predict")
def demand_predict(body: DemandBody):
    # simple synthetic demand estimate using ML efficiency prediction as proxy
    from ..transport_ml import predict_efficiency
    features = {"distance_km": 20.0, "avg_traffic_score": body.traffic_score, "weather_risk": body.weather_risk, "mode": "truck"}
    eff = predict_efficiency(features)
    demand = max(100.0, 1000.0 * (eff / 100.0))
    return {"ok": True, "predicted_demand_kg": round(demand, 1), "eff_score": eff}

# ML namespace (aliases)
@router.get("/ml/demand-predict")
def ml_demand_predict(city: str = "kolkata"):
    from ..transport_ml import predict_efficiency
    features = {"distance_km": 20.0, "avg_traffic_score": 0.5, "weather_risk": 0.3, "mode": "truck"}
    eff = predict_efficiency(features)
    demand = max(100.0, 1000.0 * (eff / 100.0))
    return {"ok": True, "city": city, "predicted_demand_kg": round(demand, 1), "eff_score": eff}

class RouteOptimizeBody(BaseModel):
    source: List[float]
    destination: List[float]
    mode: str = "truck"

@router.post("/ml/route-optimize")
def ml_route_optimize(body: RouteOptimizeBody):
    from ..transport_logic import osrm_route, compute_distance, BASE_RATE
    src = (float(body.source[0]), float(body.source[1]))
    dst = (float(body.destination[0]), float(body.destination[1]))
    info = osrm_route(src, dst)
    distance = info.get("distance_km") or compute_distance(src, dst)
    rate = BASE_RATE.get(body.mode, 1.0)
    cost_estimate = distance * rate
    from ..transport_ml import predict_efficiency
    eff = predict_efficiency({
        "distance_km": distance,
        "avg_traffic_score": 0.5,
        "weather_risk": 0.3,
        "mode": body.mode,
    })
    return {"ok": True, "route": info, "distance_km": distance, "efficiency_score": eff, "cost_estimate": round(cost_estimate, 2)}

class FleetDecisionBody(BaseModel):
    destination: List[float]
    hydrogen_load: float

@router.post("/ml/fleet-decision")
def ml_fleet_decision(body: FleetDecisionBody):
    return fleet_optimize(OptimizeBody(destination=body.destination, hydrogen_load=body.hydrogen_load))

@router.get("/storage")
def storage():
    return [{"id": "st-1", "capacity_kg": 500000, "level_kg": 320000}, {"id": "st-2", "capacity_kg": 350000, "level_kg": 280000}]

@router.get("/production")
def production():
    return [{"plant": "A", "output_kg": 12000}, {"plant": "B", "output_kg": 18000}]