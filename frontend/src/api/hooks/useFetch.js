import { useEffect, useRef, useState } from "react";

export function useFetch(fn, autoRefreshInterval) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const saved = useRef(fn);

  useEffect(() => { saved.current = fn; }, [fn]);

  async function load() {
    setLoading(true);
    setError(null);
    const res = await saved.current();
    if (res.success) setData(res.data);
    else setError(res.message);
    setLoading(false);
  }

  useEffect(() => { load(); }, []);

  useEffect(() => {
    if (!autoRefreshInterval) return;
    const id = setInterval(load, autoRefreshInterval);
    return () => clearInterval(id);
  }, [autoRefreshInterval]);

  return { data, loading, error, refresh: load };
}