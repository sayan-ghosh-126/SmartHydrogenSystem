import React, { useEffect, useState } from "react";
import Card from "../components/Card.jsx";
import Chart from "../components/Chart.jsx";
import { PredictionAPI, useFetch } from "../api/index.js";

function solarAvail(h) { return h >= 8 && h <= 18 ? Math.max(0, 1 - Math.abs(13 - h) / 5) : 0.1; }
function windAvail(h) { return h >= 18 || h < 8 ? 0.8 : 0.4; }
function hydroAvail() { return 0.6; }

export default function Predictions() {
  const [demand, setDemand] = useState(0);
  const [renewable, setRenewable] = useState({ solar: 0, wind: 0, hydro: 0 });
  const [alerts, setAlerts] = useState(null);
  const [forecast, setForecast] = useState([]);

  const demandReq = useFetch(() => PredictionAPI.getDemandPrediction(), 10000);
  const renewableReq = useFetch(() => PredictionAPI.getRenewablePrediction(), 10000);
  const alertsReq = useFetch(() => PredictionAPI.getStorageAlerts(), 10000);

  useEffect(() => {
    if (demandReq.data) {
      const d = demandReq.data.predicted_next_day_demand || 0;
      setDemand(d);
      const now = new Date();
      const arr = [];
      for (let i = 0; i < 24; i++) {
        const h = (now.getHours() + i) % 24;
        const factor = (solarAvail(h) + windAvail(h) + hydroAvail()) / 3;
        arr.push(d * factor);
      }
      setForecast(arr);
    }
  }, [demandReq.data]);

  useEffect(() => { if (renewableReq.data) setRenewable(renewableReq.data); }, [renewableReq.data]);
  useEffect(() => { if (alertsReq.data) setAlerts(alertsReq.data); }, [alertsReq.data]);

  const health = (() => {
    const over = alerts && alerts.demand_exceeds_capacity ? 1 : 0;
    const tankIssues = alerts ? alerts.tank_alerts.length : 0;
    const score = 100 - over * 40 - Math.min(60, tankIssues * 10);
    return Math.max(0, score);
  })();

  return (
    <div className="grid cols-2">
      <Card title="Demand Forecast">
        <Chart data={forecast} color="var(--blue)" />
      </Card>
      <Card title="Renewable Prediction">
        <div className="row" style={{ gap: 24 }}>
          <div>
            <div className="muted">Solar</div>
            <div className="value">{Math.round((renewable.solar || 0) * 100)}%</div>
          </div>
          <div>
            <div className="muted">Wind</div>
            <div className="value">{Math.round((renewable.wind || 0) * 100)}%</div>
          </div>
          <div>
            <div className="muted">Hydro</div>
            <div className="value">{Math.round((renewable.hydro || 0) * 100)}%</div>
          </div>
        </div>
      </Card>
      <Card title="Storage Alerts">
        {!alerts && <div className="muted">Loading</div>}
        {alerts && alerts.tank_alerts.length === 0 && <div className="muted">No tank alerts</div>}
        {alerts && alerts.tank_alerts.map((t) => (
          <div key={t.tank_id} className="badge warning">Tank {t.tank_id}: {t.alerts.join(", ")}</div>
        ))}
      </Card>
      <Card title="System Health">
        <div className="value">{Math.round(health)}%</div>
        {alerts && alerts.demand_exceeds_capacity && <div className="badge warning">Demand exceeds capacity</div>}
      </Card>
    </div>
  );
}