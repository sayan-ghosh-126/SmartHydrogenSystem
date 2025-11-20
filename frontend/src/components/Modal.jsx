import React from "react";
export default function Modal({ open, title, children, onClose }) {
  if (!open) return null;
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="row" style={{ justifyContent: "space-between" }}>
          <h3>{title}</h3>
          <button className="btn" onClick={onClose}>Close</button>
        </div>
        <div>{children}</div>
      </div>
    </div>
  );
}