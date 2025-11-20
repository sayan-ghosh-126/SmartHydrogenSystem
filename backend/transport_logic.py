import random
from typing import Dict, Tuple, Any

import requests
from geopy.distance import geodesic

from .transport_ml import predict_efficiency, recommend_action


MODE_CAPACITY = {
    "truck": 30000.0,
    "pipeline": 500000.0,
    "tanker": 100000.0,
    "cargo ship": 1000000.0,
}

MODE_ENERGY_FACTOR = {
    "truck": 1.0,
    "pipeline": 0.4,
    "tanker": 0.8,
    "cargo ship": 0.6,
}


def osrm_route(src: Tuple[float, float], dst: Tuple[float, float]) -> Dict[str, Any]:
    try:
        src_lonlat = f"{src[1]},{src[0]}"
        dst_lonlat = f"{dst[1]},{dst[0]}"
        url = (
            f"https://router.project-osrm.org/route/v1/driving/{src_lonlat};{dst_lonlat}"
            f"?overview=full&geometries=geojson&steps=false"
        )
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if resp.status_code == 200 and data.get("routes"):
            route = data["routes"][0]
            return {
                "distance_km": route.get("distance", 0) / 1000.0,
                "duration_min": route.get("duration", 0) / 60.0,
                "geometry": route.get("geometry", {}),
            }
    except Exception:
        pass
    return {"distance_km": None, "duration_min": None, "geometry": None}


def compute_distance(src: Tuple[float, float], dst: Tuple[float, float]) -> float:
    try:
        return geodesic(src, dst).km
    except Exception:
        return 0.0


BASE_RATE = {"truck": 1.0, "pipeline": 0.4, "cargo ship": 0.6, "tanker": 0.8}


def evaluate_vehicle(vehicle: Dict[str, Any], decision_mode: str = "ml") -> Dict[str, Any]:
    mode = vehicle.get("mode", "truck")
    status = vehicle.get("status", "idle")
    load = float(vehicle.get("load", 0))
    src = tuple(vehicle.get("current_location", [0.0, 0.0]))
    dst = tuple(vehicle.get("destination", [0.0, 0.0]))

    capacity = MODE_CAPACITY.get(mode, 30000.0)
    seed = hash(vehicle.get("id", "0")) % 100000
    rng = random.Random(seed)
    traffic = max(0.0, min(1.0, 0.5 + rng.uniform(-0.2, 0.2)))
    weather = max(0.0, min(1.0, 0.5 + rng.uniform(-0.25, 0.25)))

    route_info = osrm_route(src, dst)
    route_distance = route_info.get("distance_km") or compute_distance(src, dst)

    rate = BASE_RATE.get(mode, 1.0)
    cost_estimate = route_distance * rate + weather * 10.0 + traffic * 12.0

    if decision_mode == "ml":
        features = {
            "distance_km": route_distance,
            "avg_traffic_score": traffic,
            "weather_risk": weather,
            "mode": mode,
        }
        eff = predict_efficiency(features)
        action = recommend_action(eff, load, capacity)
    else:
        overloaded = load > capacity
        base = 100.0
        penalty = min(route_distance / 25.0, 45.0) + traffic * 20.0 + weather * 15.0 + (1.2 - rate) * 12.0
        eff = max(0.0, min(100.0, base - penalty))
        if status == "maintenance":
            action = "hold"
        elif overloaded:
            action = "load-balance"
        elif eff < 50.0:
            action = "hold"
        else:
            action = "dispatch"

    return {
        "recommended_action": action,
        "efficiency_score": round(eff, 1),
        "recommended_route": route_info,
        "capacity": capacity,
        "cost_estimate": round(cost_estimate, 2),
        "distance_km": round(route_distance, 2),
    }