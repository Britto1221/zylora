"use client";
import { useEffect } from "react";
export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => { console.error("Zylora UI error", error.digest); }, [error]);
  return <html><body><main className="login-shell"><section className="login-card"><p className="eyebrow">System error</p><h1>Something went wrong.</h1><p>The API and worker report production incidents through the configured Sentry DSN and alert webhook. Reference: {error.digest ?? "unavailable"}.</p><button className="button" onClick={reset}>Try again</button></section></main></body></html>;
}
