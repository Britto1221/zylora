import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

const API_URL =
  process.env.API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000/api/v1";

async function forward(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  const cookieStore = await cookies();
  const token = cookieStore.get("zylora_access_token")?.value;
  const target = new URL(`${API_URL}/${path.join("/")}`);
  request.nextUrl.searchParams.forEach((value: string, key: string) => target.searchParams.append(key, value));

  const body =
    request.method === "GET" || request.method === "HEAD"
      ? undefined
      : await request.arrayBuffer();

  const response = await fetch(target, {
    method: request.method,
    headers: {
      ...(request.headers.get("content-type")
        ? { "Content-Type": request.headers.get("content-type") as string }
        : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      "X-Request-ID": request.headers.get("x-request-id") ?? crypto.randomUUID(),
    },
    body,
    cache: "no-store",
  });

  const result = await response.arrayBuffer();
  return new NextResponse(result, {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("content-type") ?? "application/json",
      ...(response.headers.get("content-disposition")
        ? { "Content-Disposition": response.headers.get("content-disposition") as string }
        : {}),
    },
  });
}

export const GET = forward;
export const POST = forward;
export const PUT = forward;
export const PATCH = forward;
export const DELETE = forward;
