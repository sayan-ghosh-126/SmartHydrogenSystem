import { useState } from "react";

export function usePut(fn) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  async function execute(...args) {
    setLoading(true);
    setError(null);
    const res = await fn(...args);
    if (res.success) setData(res.data);
    else setError(res.message);
    setLoading(false);
    return res;
  }
  return { data, loading, error, execute };
}