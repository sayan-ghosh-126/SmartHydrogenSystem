import React from "react";
export default function Gauge({ value = 0 }) {
  const size = 140;
  const stroke = 14;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, value));
  const offset = c - (pct / 100) * c;
  return (
    <div style={{ display: "grid", placeItems: "center" }}>
      <svg width={size} height={size}>
        <circle cx={size/2} cy={size/2} r={r} stroke="#e5e7eb" strokeWidth={stroke} fill="none" />
        <circle cx={size/2} cy={size/2} r={r} stroke="var(--green)" strokeWidth={stroke} fill="none" strokeDasharray={c} strokeDashoffset={offset} transform={`rotate(-90 ${size/2} ${size/2})`} />
        <text x="50%" y="50%" dominantBaseline="middle" textAnchor="middle" fontSize="18" fill="var(--text)">{Math.round(pct)}%</text>
      </svg>
    </div>
  );
}