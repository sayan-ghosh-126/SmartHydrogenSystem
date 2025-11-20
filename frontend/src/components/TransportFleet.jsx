import React, { useEffect, useMemo, useState } from 'react'
import RouteMap from './RouteMap.jsx'

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
        const resp = await fetch('/api/transport/fleet')
        const json = await resp.json()
        setData(json.fleet || [])
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
                <th>Efficiency Score</th>
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
                    <td>
                      <ScoreBadge score={v.efficiency_score ?? 0} />
                    </td>
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
        </aside>
      </div>
    </div>
  )
}