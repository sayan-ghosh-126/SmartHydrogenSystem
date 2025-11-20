import React, { useEffect, useMemo, useState } from 'react'
import RouteMap from './RouteMap.jsx'
import { api } from '../lib/api.js'
import { Chart, ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
Chart.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const capacityByMode = {
  truck: 30000,
  pipeline: 500000,
  tanker: 100000,
  'cargo ship': 1000000,
}

function ScoreBadge({ score }) {
  let cls = 'score-badge'
  if (score > 80) cls += ' green'
  else if (score >= 50) cls += ' yellow'
  else cls += ' red'
  return <span className={cls}>{score}</span>
}

function ActionBadge({ action }) {
  return <span className={`action-badge ${action}`}>{action}</span>
}

export default function TransportFleet() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    async function fetchFleet() {
      setLoading(true)
      setError('')
      try {
        const resp = await api.get('/fleet?decision_mode=ml')
        setData(resp || [])
      } catch (e) {
        setError('Failed to load fleet')
      } finally {
        setLoading(false)
      }
    }
    fetchFleet()
  }, [])

  const summary = useMemo(() => {
    let highEff = 0
    let overloaded = 0
    let maintenance = 0
    for (const v of data) {
      if ((v.efficiency_score || 0) > 80) highEff += 1
      const capacity = capacityByMode[v.mode] || 30000
      if ((v.load || 0) > capacity) overloaded += 1
      if (v.status === 'maintenance') maintenance += 1
    }
    return { highEff, overloaded, maintenance }
  }, [data])

  return (
    <div className="transport-fleet">
      <div className="layout">
        <div className="content">
          <div className="toolbar">
            <h2>Transport Fleet</h2>
          </div>
          {loading && <div>Loading…</div>}
          {error && <div className="error">{error}</div>}
          <table className="fleet-table">
            <thead>
              <tr>
                <th>Vehicle</th>
                <th>Mode</th>
                <th>Status</th>
                <th>Load (kg)</th>
                <th>Destination</th>
                <th>Decision</th>
                <th>Efficiency</th>
                <th>Capacity</th>
                <th>Cost</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {data.length === 0 ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center' }}>No fleet data</td>
                </tr>
              ) : (
                data.map((v) => (
                  <tr key={v.id}>
                    <td>{v.vehicle_id}</td>
                    <td>{v.mode}</td>
                    <td>{v.status}</td>
                    <td>{Math.round(v.load)}</td>
                    <td>
                      {Array.isArray(v.destination) ? (
                        <span>
                          {v.destination[0].toFixed(4)}, {v.destination[1].toFixed(4)}
                        </span>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td>
                      <div>
                        AI Recommendation: <ActionBadge action={v.recommended_action} />
                      </div>
                    </td>
                    <td><ScoreBadge score={v.efficiency_score ?? 0} /></td>
                    <td>{Math.round(v.capacity)}</td>
                    <td>{v.cost_estimate?.toFixed(2)}</td>
                    <td>
                      <button
                        className="view-route"
                        onClick={() =>
                          setSelected({
                            source: v.current_location,
                            destination: v.destination,
                            geometry: v.recommended_route?.geometry || null,
                          })
                        }
                      >
                        View Route
                      </button>
                      <button
                        className="view-route"
                        style={{ marginLeft: 8, background: '#8e24aa' }}
                        onClick={async () => {
                          try {
                            const dest = v.destination
                            const payload = { vehicle_id: v.vehicle_id, destination: dest, hydrogen_load: v.load }
                            await api.post('/fleet/assign', payload)
                            const refreshed = await api.get('/fleet?decision_mode=ml')
                            setData(refreshed || [])
                          } catch (e) {}
                        }}
                      >
                        Assign
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>

          {selected && (
            <div className="route-panel">
              <h3>Route Map</h3>
              <RouteMap
                source={selected.source}
                destination={selected.destination}
                geometry={selected.geometry}
              />
            </div>
          )}
        </div>

        <aside className="sidebar">
          <div className="card">
            <h3>Decision Summary</h3>
            <div className="summary-item">
              <span>High-efficiency vehicles</span>
              <strong>{summary.highEff}</strong>
            </div>
            <div className="summary-item">
              <span>Overloaded vehicles</span>
              <strong>{summary.overloaded}</strong>
            </div>
            <div className="summary-item">
              <span>Needing maintenance</span>
              <strong>{summary.maintenance}</strong>
            </div>
          </div>

          <div className="card">
            <h3>Efficiency Chart</h3>
            <div className="bar-chart">
              {[0, 20, 40, 60, 80, 100].map((bucket, idx) => {
                const next = bucket + 20
                const count = data.filter((v) => {
                  const s = v.efficiency_score || 0
                  return s >= bucket && s < next
                }).length
                return (
                  <div className="bar" key={idx}>
                    <div className="bar-label">{bucket}-{next}</div>
                    <div className="bar-value" style={{ width: `${count * 15}px` }}>{count}</div>
                  </div>
                )
              })}
            </div>
          </div>

          <div className="card">
            <h3>Model Controls</h3>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="view-route" onClick={async () => {
                try {
                  await api.post('/train', {})
                  const refreshed = await api.get('/fleet?decision_mode=ml')
                  setData(refreshed || [])
                } catch (e) {}
              }}>Retrain Model</button>
              <button className="view-route" style={{ background: '#4caf50' }} onClick={async () => {
                try {
                  const resp = await api.get('/fleet?decision_mode=rule')
                  setData(resp || [])
                } catch (e) {}
              }}>Toggle Rule-based</button>
            </div>
            <div style={{ marginTop: 8, color: '#94a3b8' }}>
              This model uses synthetic training data for demo purposes
            </div>
          </div>

          <div className="card">
            <h3>Demand Prediction</h3>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="view-route" onClick={async () => {
                try {
                  const res = await api.post('/demand/predict', { region: 'demo', weather_risk: 0.3, traffic_score: 0.5 })
                  alert(`Predicted hydrogen demand: ${res.predicted_demand_kg} kg (eff ${Math.round(res.eff_score)})`)
                } catch (e) {}
              }}>Predict Demand</button>
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}