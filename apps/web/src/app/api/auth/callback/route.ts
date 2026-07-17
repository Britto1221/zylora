import { NextRequest, NextResponse } from "next/server";
import { exchangeAuthorizationCode } from "@/lib/auth/oidc";

const API_URL = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");
  const state = request.nextUrl.searchParams.get("state");
  const expectedState = request.cookies.get("zylora_oauth_state")?.value;
  const verifier = request.cookies.get("zylora_oauth_verifier")?.value;
  const next = request.cookies.get("zylora_oauth_next")?.value ?? "/admin/dashboard";
  if (!code || !state || state !== expectedState || !verifier) return NextResponse.redirect(new URL("/login?error=invalid_oauth_state", request.url));
  try {
    const tokens = await exchangeAuthorizationCode(code, verifier);
    const validation = await fetch(`${API_URL}/auth/me`, { headers: { Authorization: `Bearer ${tokens.access_token}` }, cache: "no-store" });
    if (!validation.ok) throw new Error("Access token validation failed.");
    const response = NextResponse.redirect(new URL(next.startsWith("/") ? next : "/admin/dashboard", request.url));
    response.cookies.set("zylora_access_token", tokens.access_token, { httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", maxAge: tokens.expires_in ?? 3600, path: "/" });
    for (const name of ["zylora_oauth_state", "zylora_oauth_verifier", "zylora_oauth_next"]) response.cookies.delete(name);
    return response;
  } catch {
    return NextResponse.redirect(new URL("/login?error=authentication_failed", request.url));
  }
}
