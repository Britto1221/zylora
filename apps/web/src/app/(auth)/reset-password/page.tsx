export default function ResetPasswordPage() {
  return (
    <main className="login-shell">
      <section className="login-art"><h1>Secure reset.</h1></section>
      <section className="login-form-wrap">
        <div className="login-card">
          <p className="eyebrow">Account security</p>
          <h2>Choose a new password</h2>
          <p className="lede">Complete the signed password-reset flow opened by your production identity provider.</p>
          <a className="button secondary" href="/login">Return to sign in</a>
        </div>
      </section>
    </main>
  );
}
