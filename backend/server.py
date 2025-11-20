from typing import List, Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .transport_logic import evaluate_vehicle


app = FastAPI(title="Smart Hydrogen Transport API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def sample_fleet() -> List[Dict[str, Any]]:
    vehicles = []
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
    modes = ["truck", "pipeline", "tanker", "cargo ship"]
    statuses = ["idle", "en-route", "maintenance", "loading"]
    loads = [12000, 28000, 45000, 75000, 150000, 300000, 800000]

    for i in range(10):
        vehicles.append(
            {
                "id": f"veh-{i+1}",
                "vehicle_id": f"VH{i+1:03d}",
                "mode": modes[i % len(modes)],
                "status": statuses[i % len(statuses)],
                "load": float(loads[i % len(loads)]),
                "current_location": [base_points[i][0], base_points[i][1]],
                "destination": [dest_points[i][0], dest_points[i][1]],
            }
        )
    return vehicles


@app.get("/api/transport/fleet")
def get_fleet():
    fleet = sample_fleet()
    enriched = []
    for v in fleet:
        decision = evaluate_vehicle(v)
        enriched.append(
            {
                **v,
                "recommended_route": decision["recommended_route"],
                "recommended_action": decision["recommended_action"],
                "efficiency_score": decision["efficiency_score"],
            }
        )
    return {"fleet": enriched}


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.getenv("PORT", "8050"))
    uvicorn.run(app, host="0.0.0.0", port=port)