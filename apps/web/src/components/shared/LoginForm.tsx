"use client";

import { ChangeEvent, FormEvent, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export function LoginForm() {
  const router = useRouter();
  const search = useSearchParams();
  const devEnabled = process.env.NEXT_PUBLIC_ENABLE_DEV_LOGIN === "true";
  const [email, setEmail] = useState("admin@zylora.dev");
  const [password, setPassword] = useState("zylora-admin");
  const [error, setError] = useState(search.get("error") ? "Authentication could not be completed." : "");
  const [busy, setBusy] = useState(false);
  const next = search.get("next") ?? "/admin/dashboard";

  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError("");
    const response = await fetch(`/api/auth/login?next=${encodeURIComponent(next)}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
    const result = await response.json(); setBusy(false);
    if (!response.ok) { setError(result.detail ?? "Unable to sign in."); return; }
    router.push(result.next); router.refresh();
  }

  return <div className="stack">
    {error ? <div className="error">{error}</div> : null}
    <a className="button" href={`/api/auth/login?next=${encodeURIComponent(next)}`}>Continue with secure sign-in</a>
    {devEnabled ? <form className="stack" onSubmit={submit}>
      <div className="divider"><span>Development only</span></div>
      <div className="field"><label htmlFor="email">Email address</label><input className="input" id="email" type="email" value={email} onChange={(e: ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)} required /></div>
      <div className="field"><label htmlFor="password">Password</label><input className="input" id="password" type="password" value={password} onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)} required /></div>
      <button className="button button-secondary" disabled={busy} type="submit">{busy ? "Signing in…" : "Use development login"}</button>
    </form> : null}
  </div>;
}
