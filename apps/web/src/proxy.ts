import { NextRequest, NextResponse } from "next/server";

const protectedPrefixes = ["/admin", "/portal", "/preview"];

function normalizeHost(value: string | null): string {
  return (value ?? "").split(":")[0].toLowerCase();
}

export function proxy(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const host = normalizeHost(request.headers.get("host"));
  const rootDomain = normalizeHost(process.env.NEXT_PUBLIC_ROOT_DOMAIN ?? "localhost");
  const appHosts = new Set([
    rootDomain,
    "www." + rootDomain,
    "localhost",
    "127.0.0.1",
    ...String(process.env.ZYLORA_APP_HOSTS ?? "").split(",").map((value) => normalizeHost(value.trim())).filter(Boolean),
  ]);

  const protectedRoute = protectedPrefixes.some((prefix) => pathname.startsWith(prefix));
  if (protectedRoute && !request.cookies.get("zylora_access_token")) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  const internalPath =
    pathname.startsWith("/api") ||
    pathname.startsWith("/_next") ||
    pathname.startsWith("/admin") ||
    pathname.startsWith("/portal") ||
    pathname.startsWith("/preview") ||
    pathname.startsWith("/login") ||
    pathname.startsWith("/site");

  const isSubdomain = rootDomain !== "localhost" && host.endsWith(`.${rootDomain}`) && host !== `www.${rootDomain}`;
  const isDevelopmentSubdomain = host.endsWith(".localhost");
  const isCustomDomain = Boolean(host) && !appHosts.has(host) && !host.endsWith(".vercel.app");

  if (!internalPath && (isSubdomain || isDevelopmentSubdomain || isCustomDomain)) {
    const rewrite = request.nextUrl.clone();
    rewrite.pathname = `/site${pathname}`;
    const response = NextResponse.rewrite(rewrite);
    response.headers.set("x-zylora-host", host);
    return response;
  }

  const response = NextResponse.next();
  response.headers.set("x-zylora-host", host);
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
