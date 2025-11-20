import React, { useEffect, useMemo, useState } from "react";
import Card from "../components/Card.jsx";
import Table from "../components/Table.jsx";
import { TransportAPI, useFetch, usePost } from "../api/index.js";

export default function Transport() {
  const [fleet, setFleet] = useState([]);
  const [form, setForm] = useState({ start_location: "37.7749,-122.4194", end_location: "34.0522,-118.2437", hydrogen_load: 500 });
  const [route, setRoute] = useState(null);

  const fleetReq = useFetch(() => TransportAPI.getFleet(), 15000);
  useEffect(() => { if (fleetReq.data) setFleet(fleetReq.data); }, [fleetReq.data]);

  const cols = useMemo(() => ([
    { key: "vehicle_id", label: "Vehicle" },
    { key: "mode", label: "Mode" },
    { key: "status", label: "Status" },
    { key: "hydrogen_load", label: "Load" },
    { key: "destination", label: "Destination" },
  ]), []);

  const planRoute = usePost((payload) => TransportAPI.getOptimalRoute(payload));
  async function plan() {
    const res = await planRoute.execute(form);
    if (res.success) setRoute(res.data);
  }

  return (
    <div className="grid cols-2">
      <Card title="Fleet">
        <Table columns={cols} data={fleet} />
      </Card>
      <Card title="Route Planner">
        <div className="form">
          <input placeholder="Start" value={form.start_location} onChange={(e) => setForm({ ...form, start_location: e.target.value })} />
          <input placeholder="End" value={form.end_location} onChange={(e) => setForm({ ...form, end_location: e.target.value })} />
          <input type="number" placeholder="Hydrogen Load" value={form.hydrogen_load} onChange={(e) => setForm({ ...form, hydrogen_load: Number(e.target.value) })} />
          <button className="btn" onClick={plan}>Plan Optimal Route</button>
        </div>
        <div className="map">Map Placeholder</div>
        {route && (
          <div className="grid cols-2" style={{ marginTop: 12 }}>
            <div className="card">
              <div className="muted">Safest Route</div>
              <div className="value">{route.selected.distance_km} km</div>
            </div>
            <div className="card">
              <div className="muted">Estimated Time</div>
              <div className="value">{route.selected.estimated_time_hours} h</div>
            </div>
            <div className="card">
              <div className="muted">Weather</div>
              <div className="value">{route.selected.weather}</div>
            </div>
            <div className="card">
              <div className="muted">Risk Score</div>
              <div className="value">{route.selected.risk_score}</div>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}