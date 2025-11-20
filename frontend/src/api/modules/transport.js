import { apiClient } from "../config.js";

export const TransportAPI = {
  getFleet: () => apiClient.request("get", "/transport/fleet"),
  addVehicle: (payload) => apiClient.request("post", "/transport/add-vehicle", payload),
  getOptimalRoute: (payload) => apiClient.request("post", "/transport/optimal-route", payload),
};