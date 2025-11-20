import { useEffect, useRef } from "react";
export default function useInterval(cb, delay) {
  const saved = useRef();
  useEffect(() => { saved.current = cb; }, [cb]);
  useEffect(() => {
    if (delay == null) return;
    const id = setInterval(() => saved.current && saved.current(), delay);
    return () => clearInterval(id);
  }, [delay]);
}