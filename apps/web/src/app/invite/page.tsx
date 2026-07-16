import { Suspense } from "react";
import { InvitationAcceptForm } from "@/components/shared/InvitationAcceptForm";

export default function InvitationPage() {
  return (
    <main className="login-shell">
      <section className="login-art">
        <div><p className="eyebrow" style={{ color: "#777" }}>Client access</p><h1>Your Zylora workspace is ready.</h1></div>
      </section>
      <section className="login-form-wrap">
        <div className="login-card">
          <p className="eyebrow">Secure invitation</p>
          <h2>Accept access</h2>
          <p className="lede">Use the exact invited email. Production identity verification and password creation are handled by the configured OIDC provider.</p>
          <Suspense fallback={<div className="notice">Loading invitation…</div>}><InvitationAcceptForm /></Suspense>
        </div>
      </section>
    </main>
  );
}
