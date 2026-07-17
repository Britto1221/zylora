import { randomBytes } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";
import { createPkce, required } from "@/lib/auth/oidc";

const API_URL = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export async function GET(request: NextRequest) {
  const next = request.nextUrl.searchParams.get("next") ?? "/admin/dashboard";
  const state = randomBytes(32).toString("base64url");
  const { verifier, challenge } = createPkce();
  const url = new URL(required("AUTH_AUTHORIZATION_URL"));
  url.searchParams.set("response_type", "code");
  url.searchParams.set("client_id", required("AUTH_CLIENT_ID"));
  url.searchParams.set("redirect_uri", required("AUTH_REDIRECT_URI"));
  url.searchParams.set("scope", "openid email profile");
  url.searchParams.set("state", state);
  url.searchParams.set("code_challenge", challenge);
  url.searchParams.set("code_challenge_method", "S256");
  const response = NextResponse.redirect(url);
  const cookie = { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax" as const, path: "/", maxAge: 600 };
  response.cookies.set("zylora_oauth_state", state, cookie);
  response.cookies.set("zylora_oauth_verifier", verifier, cookie);
  response.cookies.set("zylora_oauth_next", next, cookie);
  return response;
}

export async function POST(request: NextRequest) {
  if (process.env.NODE_ENV === "production" || process.env.NEXT_PUBLIC_ENABLE_DEV_LOGIN !== "true") {
    return NextResponse.json({ detail: "Development login is disabled." }, { status: 404 });
  }
  const payload = await request.json();
  const response = await fetch(`${API_URL}/auth/development-login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), cache: "no-store" });
  const data = await response.json();
  if (!response.ok) return NextResponse.json(data, { status: response.status });
  const next = request.nextUrl.searchParams.get("next") ?? "/admin/dashboard";
  const result = NextResponse.json({ ok: true, next });
  result.cookies.set("zylora_access_token", data.access_token, { httpOnly: true, sameSite: "lax", secure: false, maxAge: data.expires_in ?? 43200, path: "/" });
  return result;
}
