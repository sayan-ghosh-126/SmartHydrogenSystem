import React, { useEffect, useState } from "react";
import Card from "../components/Card.jsx";
import Chart from "../components/Chart.jsx";
import { PredictionAPI, StorageAPI, useFetch } from "../api/index.js";

export default function Home() {
  const [summary, setSummary] = useState(null);
  const [prodTrend, setProdTrend] = useState([]);
  const [renewable, setRenewable] = useState({ solar: 0, wind: 0, hydro: 0 });
  const [alerts, setAlerts] = useState([]);

  const summaryReq = useFetch(() => PredictionAPI.getDashboardSummary(), 10000);
  const renewableReq = useFetch(() => PredictionAPI.getRenewablePrediction(), 10000);
  const tanksReq = useFetch(() => StorageAPI.getAllTanks(), 10000);

  useEffect(() => {
    if (summaryReq.data) {
      setSummary(summaryReq.data);
      setProdTrend((t) => [...t.slice(-47), summaryReq.data.production.total_current_output || 0]);
    }
  }, [summaryReq.data]);

  useEffect(() => { if (renewableReq.data) setRenewable(renewableReq.data); }, [renewableReq.data]);
  useEffect(() => {
    if (tanksReq.data) {
      const storageAlerts = tanksReq.data.flatMap((t) => t.warnings.map((w) => ({ tank: t.name, type: w })));
      setAlerts(storageAlerts);
    }
  }, [tanksReq.data]);

  return (
    <div className="grid cols-2">
      <div className="grid cols-2">
        <Card title="Total Production Today">
          <div className="value">{summary ? Math.round(summary.production.total_current_output || 0) : "-"}</div>
          <div className="muted">Current output</div>
        </Card>
        <Card title="Current Storage Level">
          <div className="value">{summary ? Math.round(summary.storage.total_level || 0) : "-"}</div>
          <div className="muted">Across tanks</div>
        </Card>
        <Card title="Active Transport Vehicles">
          <div className="value">{summary ? summary.transport.fleet_size : "-"}</div>
          <div className="muted">Fleet size</div>
        </Card>
        <Card title="Demand Prediction">
          <div className="value">{summary ? summary.predictions.next_day_demand : "-"}</div>
          <div className="muted">Next day</div>
        </Card>
      </div>
      <div className="grid cols-2">
        <Card title="Production Trends">
          <Chart data={prodTrend} color="var(--blue)" />
        </Card>
        <Card title="Renewable Availability">
          <div className="row" style={{ gap: 24 }}>
            <div>
              <div className="muted">Solar</div>
              <div className="value" style={{ color: "var(--accent)" }}>{Math.round((renewable.solar || 0) * 100)}%</div>
            </div>
            <div>
              <div className="muted">Wind</div>
              <div className="value" style={{ color: "var(--blue)" }}>{Math.round((renewable.wind || 0) * 100)}%</div>
            </div>
            <div>
              <div className="muted">Hydro</div>
              <div className="value" style={{ color: "var(--green)" }}>{Math.round((renewable.hydro || 0) * 100)}%</div>
            </div>
          </div>
        </Card>
        <Card title="Alerts">
          {alerts.length === 0 && <div className="muted">No active alerts</div>}
          {alerts.map((a, i) => (
            <div key={i} className="badge warning">{a.type} in {a.tank}</div>
          ))}
        </Card>
      </div>
    </div>
  );
}