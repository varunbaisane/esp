import { useState, useEffect } from "react";

export function useDelay(isLoading: boolean, delayMs = 200) {
  const [showLoader, setShowLoader] = useState(false);

  useEffect(() => {
    let timeoutId: number;

    if (isLoading) {
      timeoutId = window.setTimeout(() => {
        setShowLoader(true);
      }, delayMs);
    } else {
      setShowLoader(false);
    }

    return () => {
      if (timeoutId) {
        window.clearTimeout(timeoutId);
      }
    };
  }, [isLoading, delayMs]);

  return showLoader;
}
