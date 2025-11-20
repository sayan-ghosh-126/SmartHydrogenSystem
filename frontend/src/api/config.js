import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
});

async function request(method, url, data, config = {}) {
  let attempt = 0;
  let lastErr = null;
  const delays = [250, 500, 1000];
  while (attempt < 3) {
    try {
      const res = await client.request({ method, url, data, ...config });
      return { success: true, data: res.data, message: "" };
    } catch (err) {
      lastErr = err;
      const status = err?.response?.status;
      const shouldRetry = !status || status >= 500;
      if (!shouldRetry || attempt === 2) {
        const message = err?.response?.data?.detail || err?.message || "Request failed";
        return { success: false, data: null, message };
      }
      const wait = delays[attempt] || 1000;
      await new Promise((r) => setTimeout(r, wait));
      attempt += 1;
    }
  }
  const message = lastErr?.message || "Request failed";
  return { success: false, data: null, message };
}

export const apiClient = { request };
export { BASE_URL };