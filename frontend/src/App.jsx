import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";
import Home from "./pages/Home.jsx";
import Production from "./pages/Production.jsx";
import Storage from "./pages/Storage.jsx";
import Transport from "./pages/Transport.jsx";
import Predictions from "./pages/Predictions.jsx";

export default function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/production" element={<Production />} />
          <Route path="/storage" element={<Storage />} />
          <Route path="/transport" element={<Transport />} />
          <Route path="/predictions" element={<Predictions />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}