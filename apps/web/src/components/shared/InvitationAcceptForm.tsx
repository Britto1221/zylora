"use client";

import { ChangeEvent, FormEvent, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { clientApi } from "@/lib/api/client";

export function InvitationAcceptForm() {
  const router = useRouter();
  const params = useSearchParams();
  const token = params.get("token") ?? "";
  const tenantSlug = params.get("tenant") ?? "";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("zylora-admin");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true); setError("");
    try {
      // Local development signs in first. In production the OIDC provider already owns the session.
      if (process.env.NODE_ENV !== "production") {
        const login = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        if (!login.ok) throw new Error("Development sign-in failed.");
      }
      await clientApi("/access/invitations/accept", {
        method: "POST",
        body: JSON.stringify({ token }),
      });
      router.push(`/portal/${tenantSlug}/dashboard`);
      router.refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to accept invitation.");
      setBusy(false);
    }
  }

  return (
    <form className="stack" onSubmit={submit}>
      {error ? <div className="error">{error}</div> : null}
      {!token ? <div className="error">The invitation token is missing.</div> : null}
      <div className="field"><label htmlFor="inviteAcceptEmail">Invited email address</label><input className="input" id="inviteAcceptEmail" type="email" value={email} onChange={(event: ChangeEvent<HTMLInputElement>) => setEmail(event.target.value)} required /></div>
      <div className="field"><label htmlFor="inviteAcceptPassword">Development password</label><input className="input" id="inviteAcceptPassword" type="password" value={password} onChange={(event: ChangeEvent<HTMLInputElement>) => setPassword(event.target.value)} required /></div>
      <button className="button" disabled={busy || !token}>{busy ? "Accepting…" : "Accept invitation"}</button>
    </form>
  );
}
