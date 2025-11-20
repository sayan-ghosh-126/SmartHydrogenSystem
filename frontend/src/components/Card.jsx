import React from "react";
export default function Card({ title, children, right }) {
  return (
    <div className="card">
      <div className="row" style={{ justifyContent: "space-between" }}>
        <h3>{title}</h3>
        {right}
      </div>
      <div>{children}</div>
    </div>
  );
}