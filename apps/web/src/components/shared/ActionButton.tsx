"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { clientApi } from "@/lib/api/client";

export function ActionButton({
  path,
  method = "POST",
  label,
  confirm,
  body,
  className = "button secondary small",
}: {
  path: string;
  method?: "POST" | "PATCH" | "DELETE";
  label: string;
  confirm?: string;
  body?: unknown;
  className?: string;
}) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function run() {
    if (confirm && !window.confirm(confirm)) return;
    setBusy(true);
    setError("");
    try {
      await clientApi(path, {
        method,
        body: body === undefined ? undefined : JSON.stringify(body),
      });
      router.refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Action failed.");
      setBusy(false);
    }
  }

  return (
    <span>
      <button className={className} type="button" onClick={run} disabled={busy}>
        {busy ? "Working…" : label}
      </button>
      {error ? <span className="cell-sub">{error}</span> : null}
    </span>
  );
}
