import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const response = NextResponse.redirect(new URL("/login", request.url));
  response.cookies.set("zylora_access_token", "", { httpOnly: true, expires: new Date(0), path: "/" });
  return response;
}
