import { NextRequest, NextResponse } from "next/server";

const protectedPrefixes = ["/admin", "/portal", "/preview"];

export function proxy(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const isProtected = protectedPrefixes.some((prefix) =>
    pathname.startsWith(prefix),
  );

  if (
    isProtected &&
    !request.cookies.get("zylora_access_token") &&
    pathname !== "/login"
  ) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  const response = NextResponse.next();
  response.headers.set("x-zylora-host", request.headers.get("host") ?? "");
  return response;
}

export const config = {
  matcher: [
    "/admin/:path*",
    "/portal/:path*",
    "/preview/:path*",
    "/site/:path*",
  ],
};
