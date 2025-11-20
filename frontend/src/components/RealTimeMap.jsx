import React, { useEffect, useRef, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet'
import L from 'leaflet'

import { API_BASE_URL } from '../lib/api.js'

export default function RealTimeMap() {
  const [vehicles, setVehicles] = useState([])
  const [tw, setTw] = useState({ traffic: 0.5, weather: 0.5 })
  const [center, setCenter] = useState([19.0760, 72.8777])

  useEffect(() => {
    const es = new EventSource(`${API_BASE_URL}/stream`)
    es.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data)
        setVehicles(msg.vehicles || [])
        setTw({ traffic: msg.traffic, weather: msg.weather })
        if (msg.vehicles && msg.vehicles.length > 0) {
          setCenter([msg.vehicles[0].lat, msg.vehicles[0].lon])
        }
      } catch {}
    }
    return () => es.close()
  }, [])

  return (
    <div className="route-map">
      <div style={{ padding: 8 }}>
        <span>Traffic: {tw.traffic.toFixed(2)} | Weather: {tw.weather.toFixed(2)}</span>
      </div>
      <MapContainer center={center} zoom={5} style={{ height: '420px', width: '100%' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors" />
        {vehicles.map(v => (
          <Marker key={v.vehicle_id} position={[v.lat, v.lon]} icon={L.icon({ iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png', iconSize: [25, 41], iconAnchor: [12, 41] })}>
            <Popup>
              <div>
                <div>{v.vehicle_id}</div>
                <div>Status: {v.status}</div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}