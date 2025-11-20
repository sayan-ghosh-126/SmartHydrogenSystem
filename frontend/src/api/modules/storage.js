import { apiClient } from "../config.js";

export const StorageAPI = {
  getAllTanks: () => apiClient.request("get", "/storage/all"),
  updateTank: (id, payload) => apiClient.request("put", `/storage/update/${id}`, payload),
  addStorageTank: (payload) => apiClient.request("post", "/storage/add", payload),
};