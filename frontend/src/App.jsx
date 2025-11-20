import React from 'react'
import TransportFleet from './components/TransportFleet.jsx'
import RealTimeMap from './components/RealTimeMap.jsx'

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Smart Hydrogen Transport</h1>
      </header>
      <main>
        <TransportFleet />
        <div className="content" style={{ marginTop: 16 }}>
          <h2>Real-time Simulator</h2>
          <RealTimeMap />
        </div>
      </main>
    </div>
  )
}