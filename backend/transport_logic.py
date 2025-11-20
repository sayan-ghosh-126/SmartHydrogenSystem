import math
import random
from typing import Dict, Tuple, Any

import requests


def haversine_km(src: Tuple[float, float], dst: Tuple[float, float]) -> float:
    R = 6371.0
    lat1, lon1 = math.radians(src[0]), math.radians(src[1])
    lat2, lon2 = math.radians(dst[0]), math.radians(dst[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


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


def evaluate_vehicle(vehicle: Dict[str, Any]) -> Dict[str, Any]:
    mode = vehicle.get("mode", "truck")
    status = vehicle.get("status", "idle")
    load = float(vehicle.get("load", 0))
    src = tuple(vehicle.get("current_location", [0.0, 0.0]))
    dst = tuple(vehicle.get("destination", [0.0, 0.0]))

    capacity = MODE_CAPACITY.get(mode, 30000.0)
    overloaded = load > capacity
    load_ratio = min(load / capacity, 1.5)

    straight_distance = haversine_km(src, dst)
    route_info = osrm_route(src, dst)
    route_distance = route_info.get("distance_km") or straight_distance

    seed = hash(vehicle.get("id", "0")) % 100000
    rng = random.Random(seed)
    traffic_factor = 1.0 + rng.uniform(-0.1, 0.25)
    weather_factor = 1.0 + rng.uniform(-0.05, 0.2)

    energy_factor = MODE_ENERGY_FACTOR.get(mode, 1.0)

    base = 100.0
    penalty = 0.0
    penalty += min(route_distance / 20.0, 40.0)
    penalty += load_ratio * 20.0
    penalty += (traffic_factor - 1.0) * 100.0 * 0.2
    penalty += (weather_factor - 1.0) * 100.0 * 0.15
    penalty += energy_factor * 10.0
    if status == "maintenance":
        penalty += 30.0
    elif status == "loading":
        penalty += 10.0

    score = max(0.0, min(100.0, base - penalty))

    if status == "maintenance":
        action = "hold"
    elif overloaded:
        action = "load-balance"
    elif score < 50.0:
        action = "hold"
    else:
        detour_ratio = route_distance / max(straight_distance, 0.1)
        if detour_ratio > 1.3:
            action = "reroute"
        elif status in ("idle", "loading"):
            action = "dispatch"
        else:
            action = "dispatch"

    return {
        "recommended_action": action,
        "efficiency_score": round(score, 1),
        "recommended_route": route_info,
        "capacity": capacity,
        "overloaded": overloaded,
    }