export default function ForgotPasswordPage() {
  const resetUrl = process.env.NEXT_PUBLIC_AUTH_PASSWORD_RESET_URL ?? "#";

  return (
    <main>
      <h1>Reset your password</h1>
      <section className="card">
        <p>Password reset is handled by the configured identity provider.</p>
        <a href={resetUrl}>Continue to password reset</a>
      </section>
    </main>
  );
}
