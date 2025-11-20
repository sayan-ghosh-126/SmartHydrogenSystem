import React, { useEffect, useMemo, useState } from "react";
import Card from "../components/Card.jsx";
import Gauge from "../components/Gauge.jsx";
import Table from "../components/Table.jsx";
import Modal from "../components/Modal.jsx";
import { StorageAPI, useFetch, usePost } from "../api/index.js";

export default function Storage() {
  const [tanks, setTanks] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", capacity: 5000, current_level: 2500, pressure: 300, temperature: 25 });

  const tanksReq = useFetch(() => StorageAPI.getAllTanks(), 10000);
  useEffect(() => { if (tanksReq.data) setTanks(tanksReq.data); }, [tanksReq.data]);

  const addTank = usePost((payload) => StorageAPI.addStorageTank(payload));
  async function submit() {
    const res = await addTank.execute(form);
    if (res.success) setOpen(false);
    tanksReq.refresh();
  }

  const cols = useMemo(() => ([
    { key: "name", label: "Name" },
    { key: "pressure", label: "Pressure" },
    { key: "temperature", label: "Temperature" },
    { key: "capacity", label: "Capacity" },
    { key: "current_level", label: "Current Level" },
    { key: "leakage_detected", label: "Leakage", render: (r) => r.leakage_detected ? <span className="badge warning">Leak</span> : <span className="badge">OK</span> },
  ]), []);

  return (
    <div className="grid cols-2">
      <Card title="Tanks" right={<button className="btn secondary" onClick={() => setOpen(true)}>Add Tank</button>}>
        <Table columns={cols} data={tanks} />
      </Card>
      <div className="grid cols-3">
        {tanks.map((t) => {
          const pct = t.capacity ? (Number(t.current_level) || 0) / Number(t.capacity) * 100 : 0;
          return (
            <Card key={t.id} title={t.name} right={t.warnings.length ? <span className="badge warning">Alert</span> : <span className="badge">Safe</span>}>
              <div className="row" style={{ gap: 24 }}>
                <Gauge value={pct} />
                <div>
                  <div className="muted">Pressure</div>
                  <div className="value">{Math.round(Number(t.pressure) || 0)} bar</div>
                  <div className="muted">Temperature</div>
                  <div className="value">{Math.round(Number(t.temperature) || 0)} °C</div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
      <Modal open={open} title="Add Tank" onClose={() => setOpen(false)}>
        <div className="form">
          <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input type="number" placeholder="Capacity" value={form.capacity} onChange={(e) => setForm({ ...form, capacity: Number(e.target.value) })} />
          <input type="number" placeholder="Current Level" value={form.current_level} onChange={(e) => setForm({ ...form, current_level: Number(e.target.value) })} />
          <input type="number" placeholder="Pressure" value={form.pressure} onChange={(e) => setForm({ ...form, pressure: Number(e.target.value) })} />
          <input type="number" placeholder="Temperature" value={form.temperature} onChange={(e) => setForm({ ...form, temperature: Number(e.target.value) })} />
          <button className="btn" onClick={submit}>Save</button>
        </div>
      </Modal>
    </div>
  );
}