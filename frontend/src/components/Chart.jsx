import React from "react";
export default function Chart({ data = [], color = "var(--blue)" }) {
  const w = 600;
  const h = 220;
  const max = Math.max(1, ...data);
  const step = data.length > 1 ? w / (data.length - 1) : 0;
  const pts = data.map((v, i) => `${i * step},${h - (v / max) * h}`).join(" ");
  return (
    <svg className="chart" viewBox={`0 0 ${w} ${h}`}> 
      <polyline points={pts} fill="none" stroke={color} strokeWidth="2" />
    </svg>
  );
}