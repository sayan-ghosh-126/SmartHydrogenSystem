import React from 'react'
import TransportFleet from './components/TransportFleet.jsx'

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Smart Hydrogen Transport</h1>
      </header>
      <main>
        <TransportFleet />
      </main>
    </div>
  )
}