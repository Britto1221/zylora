"use client";

import { ChangeEvent, FormEvent, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export function LoginForm() {
  const router = useRouter();
  const search = useSearchParams();
  const [email, setEmail] = useState("admin@zylora.dev");
  const [password, setPassword] = useState("zylora-admin");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const next = search.get("next") ?? "/admin/dashboard";
    const response = await fetch(`/api/auth/login?next=${encodeURIComponent(next)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const result = await response.json();
    setBusy(false);
    if (!response.ok) {
      setError(result.detail ?? "Unable to sign in.");
      return;
    }
    router.push(result.next);
    router.refresh();
  }

  return (
    <form className="stack" onSubmit={submit}>
      {error ? <div className="error">{error}</div> : null}
      <div className="field">
        <label htmlFor="email">Email address</label>
        <input
          className="input"
          id="email"
          type="email"
          autoComplete="username"
          value={email}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setEmail(event.target.value)}
          required
        />
      </div>
      <div className="field">
        <label htmlFor="password">Password</label>
        <input
          className="input"
          id="password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setPassword(event.target.value)}
          required
        />
      </div>
      <button className="button" disabled={busy} type="submit">
        {busy ? "Signing in…" : "Enter Zylora"}
      </button>
    </form>
  );
}
