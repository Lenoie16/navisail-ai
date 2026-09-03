"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main role="alert">
      <h1>Something went wrong</h1>
      <p>The command center could not load this view.</p>
      <button type="button" onClick={reset}>
        Try again
      </button>
    </main>
  );
}
