import { apiClient } from "../config.js";

export const PredictionAPI = {
  getDemandPrediction: () => apiClient.request("get", "/prediction/demand"),
  getRenewablePrediction: () => apiClient.request("get", "/prediction/renewable"),
  getStorageAlerts: () => apiClient.request("get", "/prediction/storage-alerts"),
  getDashboardSummary: () => apiClient.request("get", "/dashboard/summary"),
};