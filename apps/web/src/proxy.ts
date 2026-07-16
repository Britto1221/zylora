import { NextRequest, NextResponse } from "next/server";

export function proxy(request: NextRequest) {
  const response = NextResponse.next();
  response.headers.set("x-zylora-host", request.headers.get("host") ?? "");
  return response;
}

export const config = {
  matcher: ["/admin/:path*", "/portal/:path*", "/site/:path*"],
};
