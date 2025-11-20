import React, { useEffect, useRef } from 'react'
import { MapContainer, TileLayer, Polyline, useMap } from 'react-leaflet'
import L from 'leaflet'

function FitBounds({ geometry }) {
  const map = useMap()
  useEffect(() => {
    if (!geometry || !geometry.coordinates) return
    const latlngs = geometry.coordinates.map(([lon, lat]) => [lat, lon])
    const bounds = L.latLngBounds(latlngs)
    map.fitBounds(bounds, { padding: [20, 20] })
  }, [geometry, map])
  return null
}

export default function RouteMap({ source, destination, geometry }) {
  const polylineRef = useRef(null)
  const center = source || [37.7749, -122.4194]

  const positions = geometry?.coordinates
    ? geometry.coordinates.map(([lon, lat]) => [lat, lon])
    : []

  return (
    <div className="route-map">
      <MapContainer center={center} zoom={6} style={{ height: '400px', width: '100%' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />
        {positions.length > 0 && (
          <Polyline positions={positions} ref={polylineRef} color="#1e88e5" />
        )}
        <FitBounds geometry={geometry} />
      </MapContainer>
    </div>
  )
}