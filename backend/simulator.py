import asyncio
import time
import random
from typing import Dict, Any, List

from fastapi.responses import StreamingResponse
import json


class Simulator:
    def __init__(self):
        self.state: Dict[str, Any] = {"vehicles": {}, "traffic": 0.5, "weather": 0.5}
        self._task = None

    def set_fleet(self, vehicles: List[Dict[str, Any]]):
        self.state["vehicles"] = {v["vehicle_id"]: v for v in vehicles}

    async def run(self):
        rng = random.Random(123)
        while True:
            self.state["traffic"] = max(0.0, min(1.0, self.state["traffic"] + rng.uniform(-0.05, 0.05)))
            self.state["weather"] = max(0.0, min(1.0, self.state["weather"] + rng.uniform(-0.05, 0.05)))
            for v in list(self.state["vehicles"].values()):
                src = v.get("current_location", [0.0, 0.0])
                dst = v.get("destination", [0.0, 0.0])
                lat = src[0] + (dst[0] - src[0]) * 0.01
                lon = src[1] + (dst[1] - src[1]) * 0.01
                v["current_location"] = [lat, lon]
            await asyncio.sleep(2)

    def start(self):
        loop = asyncio.get_event_loop()
        if self._task is None or self._task.done():
            self._task = loop.create_task(self.run())

    async def stream(self):
        async def gen():
            while True:
                ts = int(time.time() * 1000)
                payload = {
                    "timestamp": ts,
                    "traffic": self.state.get("traffic", 0.5),
                    "weather": self.state.get("weather", 0.5),
                    "vehicles": [
                        {
                            "vehicle_id": v["vehicle_id"],
                            "lat": v["current_location"][0],
                            "lon": v["current_location"][1],
                            "status": v.get("status", "idle"),
                        }
                        for v in self.state.get("vehicles", {}).values()
                    ],
                }
                msg = f"data: {json.dumps(payload)}\n\n"
                yield msg
                await asyncio.sleep(2)
        return StreamingResponse(gen(), media_type="text/event-stream")