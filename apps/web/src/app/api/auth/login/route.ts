import { NextRequest, NextResponse } from "next/server";

const API_URL =
  process.env.API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000/api/v1";

export async function POST(request: NextRequest) {
  const payload = await request.json();
  const response = await fetch(`${API_URL}/auth/development-login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    cache: "no-store",
  });
  const data = await response.json();
  if (!response.ok) {
    return NextResponse.json(data, { status: response.status });
  }
  const next = request.nextUrl.searchParams.get("next") ?? "/admin/dashboard";
  const result = NextResponse.json({ ok: true, next });
  result.cookies.set("zylora_access_token", data.access_token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    maxAge: data.expires_in ?? 43200,
    path: "/",
  });
  return result;
}
