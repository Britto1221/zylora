import { Suspense } from "react";
import { LoginForm } from "@/components/shared/LoginForm";

export default function LoginPage() {
  return (
    <main className="login-shell">
      <section className="login-art">
        <div className="brand">
          <span className="brand-mark">Z</span>
          <span className="brand-copy"><strong>Zylora</strong><span>Managed growth infrastructure</span></span>
        </div>
        <div>
          <p className="eyebrow" style={{ color: "#777" }}>Operations console</p>
          <h1>Every client. One precise system.</h1>
          <p style={{ maxWidth: 560, color: "#888", lineHeight: 1.7 }}>
            Build, publish, capture leads, manage messaging, and improve organic visibility
            without losing control of the client experience.
          </p>
        </div>
      </section>
      <section className="login-form-wrap">
        <div className="login-card">
          <p className="eyebrow">Administrator access</p>
          <h2>Welcome back.</h2>
          <p className="lede">Use the development credentials below locally. Production authentication is handled by the configured identity provider.</p>
          <Suspense fallback={<div className="notice">Loading secure sign-in…</div>}>
            <LoginForm />
          </Suspense>
          <p className="login-footnote">
            Development: admin@zylora.dev / zylora-admin. This endpoint is disabled automatically when ENVIRONMENT=production.
          </p>
        </div>
      </section>
    </main>
  );
}
