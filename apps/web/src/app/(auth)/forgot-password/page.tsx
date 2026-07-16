export default function ForgotPasswordPage() {
  return (
    <main className="login-shell">
      <section className="login-art"><h1>Password recovery.</h1></section>
      <section className="login-form-wrap">
        <div className="login-card">
          <p className="eyebrow">Account security</p>
          <h2>Reset your password</h2>
          <p className="lede">
            In production, password recovery is completed by the configured OIDC identity provider. Add its hosted recovery URL to the deployment environment.
          </p>
          <a className="button" href={process.env.NEXT_PUBLIC_AUTH_PASSWORD_RESET_URL ?? "/login"}>Continue</a>
        </div>
      </section>
    </main>
  );
}
