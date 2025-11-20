const base = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
async function req(path, options = {}) {
  const r = await fetch(base + path, options);
  if (!r.ok) throw new Error("Request failed");
  const ct = r.headers.get("content-type") || "";
  if (ct.includes("application/json")) return r.json();
  return r.text();
}
export const api = {
  productionAll: () => req("/production/all"),
  productionAdd: (body) => req("/production/add", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
  productionUpdateOutput: (id, body) => req(`/production/update-output/${id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
  storageAll: () => req("/storage/all"),
  storageAdd: (body) => req("/storage/add", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
  storageUpdate: (id, body) => req(`/storage/update/${id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
  transportFleet: () => req("/transport/fleet"),
  transportOptimalRoute: (body) => req("/transport/optimal-route", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
  predictionDemand: () => req("/prediction/demand"),
  predictionRenewable: () => req("/prediction/renewable"),
  predictionStorageAlerts: () => req("/prediction/storage-alerts"),
  dashboardSummary: () => req("/dashboard/summary"),
};