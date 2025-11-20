import React from "react";
export default function Table({ columns = [], data = [] }) {
  return (
    <table className="table">
      <thead>
        <tr>
          {columns.map((c) => (
            <th key={c.key || c}>{c.label || c}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={i}>
            {columns.map((c) => (
              <td key={c.key || c}>{c.render ? c.render(row) : row[c.key || c]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}