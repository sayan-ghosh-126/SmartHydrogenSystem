import React, { useEffect, useMemo, useState } from "react";
import Card from "../components/Card.jsx";
import Table from "../components/Table.jsx";
import Chart from "../components/Chart.jsx";
import Modal from "../components/Modal.jsx";
import { ProductionAPI, useFetch, usePost } from "../api/index.js";

export default function Production() {
  const [units, setUnits] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", type: "solar", renewable_source: "solar", max_capacity: 1000 });
  const [trendSolar, setTrendSolar] = useState([]);
  const [trendWind, setTrendWind] = useState([]);
  const [trendHydro, setTrendHydro] = useState([]);

  const unitsReq = useFetch(() => ProductionAPI.getAllProductionUnits(), 10000);
  useEffect(() => {
    const data = unitsReq.data || [];
    setUnits(data);
    const sumByType = (t) => data.filter((u) => u.type.toLowerCase() === t).reduce((s, u) => s + (Number(u.current_output) || 0), 0);
    setTrendSolar((p) => [...p.slice(-47), sumByType("solar")]);
    setTrendWind((p) => [...p.slice(-47), sumByType("wind")]);
    setTrendHydro((p) => [...p.slice(-47), sumByType("hydro")]);
  }, [unitsReq.data]);

  const addUnit = usePost((payload) => ProductionAPI.addProductionUnit(payload));
  async function submit() {
    const res = await addUnit.execute(form);
    if (res.success) setOpen(false);
    unitsReq.refresh();
  }

  const cols = useMemo(() => ([
    { key: "name", label: "Name" },
    { key: "type", label: "Type" },
    { key: "renewable_source", label: "Source" },
    { key: "current_output", label: "Current Output" },
    { key: "max_capacity", label: "Max Capacity" },
  ]), []);

  return (
    <div className="grid cols-2">
      <Card title="Production Units" right={<button className="btn" onClick={() => setOpen(true)}>Add Production Unit</button>}>
        <Table columns={cols} data={units} />
      </Card>
      <div className="grid cols-3">
        <Card title="Solar Output">
          <Chart data={trendSolar} color="var(--accent)" />
        </Card>
        <Card title="Wind Output">
          <Chart data={trendWind} color="var(--blue)" />
        </Card>
        <Card title="Hydro Output">
          <Chart data={trendHydro} color="var(--green)" />
        </Card>
      </div>
      <Modal open={open} title="Add Production Unit" onClose={() => setOpen(false)}>
        <div className="form">
          <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value, renewable_source: e.target.value })}>
            <option value="solar">solar</option>
            <option value="wind">wind</option>
            <option value="hydro">hydro</option>
          </select>
          <input type="number" placeholder="Max Capacity" value={form.max_capacity} onChange={(e) => setForm({ ...form, max_capacity: Number(e.target.value) })} />
          <button className="btn" onClick={submit}>Save</button>
        </div>
      </Modal>
    </div>
  );
}