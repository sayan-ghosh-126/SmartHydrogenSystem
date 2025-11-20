import { apiClient } from "../config.js";

export const ProductionAPI = {
  getAllProductionUnits: () => apiClient.request("get", "/production/all"),
  updateOutput: (id, payload) => apiClient.request("put", `/production/update-output/${id}`, payload),
  addProductionUnit: (payload) => apiClient.request("post", "/production/add", payload),
};