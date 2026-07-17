"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { clientApi } from "@/lib/api/client";

export function PauseClientForm({ tenantId, paused }: { tenantId: string; paused: boolean }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const reason = String(form.get("reason") ?? "").trim();
    if (!reason) {
      setError("A reason note is required.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await clientApi(`/admin/clients/${tenantId}/pause`, {
        method: "POST",
        body: JSON.stringify({ paused: !paused, reason }),
      });
      event.currentTarget.reset();
      router.refresh();
    } catch (reasonValue) {
      setError(reasonValue instanceof Error ? reasonValue.message : "Unable to update pause state.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="stack" onSubmit={submit}>
      {error ? <div className="error">{error}</div> : null}
      <div className="field">
        <label htmlFor="pauseReason">Required reason for {paused ? "unpausing" : "pausing"}</label>
        <textarea className="textarea" id="pauseReason" name="reason" required maxLength={1000} placeholder={paused ? "Why is billing resuming?" : "Why should recurring invoices be held?"} />
      </div>
      <button className="button secondary" disabled={busy} type="submit">
        {busy ? "Saving…" : paused ? "Unpause client" : "Pause recurring billing"}
      </button>
      <p className="cell-sub">Pausing skips new recurring invoices. The client portal and public website remain fully accessible.</p>
    </form>
  );
}

export function TenantNoteForm({ tenantId }: { tenantId: string }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const text = String(form.get("text") ?? "").trim();
    if (!text) return;
    setBusy(true);
    setError("");
    try {
      await clientApi(`/admin/clients/${tenantId}/notes`, {
        method: "POST",
        body: JSON.stringify({ text }),
      });
      event.currentTarget.reset();
      router.refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to add note.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="stack" onSubmit={submit}>
      {error ? <div className="error">{error}</div> : null}
      <div className="field"><label htmlFor="clientNote">New internal note</label><textarea className="textarea" id="clientNote" name="text" required maxLength={5000} placeholder="Plain-text operational context for this client…" /></div>
      <button className="button" disabled={busy} type="submit">{busy ? "Adding…" : "Add note"}</button>
    </form>
  );
}
