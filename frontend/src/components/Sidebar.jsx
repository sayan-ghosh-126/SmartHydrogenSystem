import React from "react";
import { NavLink } from "react-router-dom";
export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div style={{ width: 14, height: 14, background: "var(--green)", borderRadius: 4 }} />
        <span>SmartHydrogenSystem</span>
      </div>
      <nav className="nav">
        <NavLink to="/" end>Home</NavLink>
        <NavLink to="/production">Production</NavLink>
        <NavLink to="/storage">Storage</NavLink>
        <NavLink to="/transport">Transport</NavLink>
        <NavLink to="/predictions">Predictions</NavLink>
      </nav>
    </aside>
  );
}