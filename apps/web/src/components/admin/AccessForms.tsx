"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { clientApi } from "@/lib/api/client";

function Feedback({ success, error }: { success: string; error: string }) {
  return <>
    {success ? <div className="success">{success}</div> : null}
    {error ? <div className="error">{error}</div> : null}
  </>;
}

export function InvitationForm({ tenantId }: { tenantId: string }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true); setSuccess(""); setError("");
    const form = new FormData(event.currentTarget);
    try {
      const result = await clientApi<{ developmentUrl?: string }>(`/access/${tenantId}/invitations`, {
        method: "POST",
        body: JSON.stringify({
          email: form.get("email"),
          role: form.get("role"),
          expires_days: Number(form.get("expiresDays")),
        }),
      });
      setSuccess(result.developmentUrl ? `Invitation created. Local URL: ${result.developmentUrl}` : "Invitation sent.");
      router.refresh();
      event.currentTarget.reset();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to invite user.");
    } finally { setBusy(false); }
  }
  return (
    <form className="stack" onSubmit={submit}>
      <Feedback success={success} error={error} />
      <div className="field-grid">
        <div className="field"><label htmlFor="inviteEmail">Email</label><input className="input" id="inviteEmail" name="email" type="email" required /></div>
        <div className="field"><label htmlFor="inviteRole">Role</label><select className="select" id="inviteRole" name="role"><option value="CLIENT_ADMIN">Client admin</option><option value="CLIENT_VIEWER">Client viewer</option></select></div>
        <div className="field"><label htmlFor="expiresDays">Expires after</label><select className="select" id="expiresDays" name="expiresDays" defaultValue="7"><option value="3">3 days</option><option value="7">7 days</option><option value="14">14 days</option><option value="30">30 days</option></select></div>
      </div>
      <button className="button" disabled={busy}>{busy ? "Creating invitation…" : "Invite client user"}</button>
    </form>
  );
}

export function CredentialForm({ tenantId }: { tenantId: string }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true); setSuccess(""); setError("");
    const form = new FormData(event.currentTarget);
    try {
      await clientApi(`/access/${tenantId}/credentials`, {
        method: "POST",
        body: JSON.stringify({ provider: form.get("provider"), secret: form.get("secret") }),
      });
      setSuccess("Encrypted credential saved.");
      router.refresh();
      event.currentTarget.reset();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to save credential.");
    } finally { setBusy(false); }
  }
  return (
    <form className="stack" onSubmit={submit}>
      <Feedback success={success} error={error} />
      <div className="field-grid">
        <div className="field"><label htmlFor="provider">AI provider</label><select className="select" id="provider" name="provider"><option value="openai">OpenAI</option><option value="anthropic">Anthropic</option><option value="google">Google</option></select></div>
        <div className="field"><label htmlFor="secret">API key</label><input className="input mono" id="secret" name="secret" type="password" required autoComplete="off" /></div>
      </div>
      <div className="field-hint">The key is encrypted server-side and is never returned to the browser after saving.</div>
      <button className="button" disabled={busy}>{busy ? "Encrypting…" : "Save encrypted key"}</button>
    </form>
  );
}
