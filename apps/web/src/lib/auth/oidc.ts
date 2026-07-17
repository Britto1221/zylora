import { createHash, randomBytes } from "node:crypto";

export function base64url(value: Buffer): string {
  return value.toString("base64url");
}

export function createPkce(): { verifier: string; challenge: string } {
  const verifier = base64url(randomBytes(48));
  const challenge = base64url(createHash("sha256").update(verifier).digest());
  return { verifier, challenge };
}

export function required(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`${name} is required for production authentication.`);
  return value;
}

export async function exchangeAuthorizationCode(code: string, verifier: string) {
  const tokenUrl = required("AUTH_TOKEN_URL");
  const body = new URLSearchParams({
    grant_type: "authorization_code",
    code,
    redirect_uri: required("AUTH_REDIRECT_URI"),
    client_id: required("AUTH_CLIENT_ID"),
    code_verifier: verifier,
  });
  if (process.env.AUTH_CLIENT_SECRET) body.set("client_secret", process.env.AUTH_CLIENT_SECRET);
  const response = await fetch(tokenUrl, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
    cache: "no-store",
  });
  if (!response.ok) throw new Error("Identity provider rejected the authorization code.");
  return (await response.json()) as { access_token: string; expires_in?: number; id_token?: string };
}
