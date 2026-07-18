import { timingSafeEqual } from "node:crypto";
import type { NextRequest } from "next/server";

export type SettingsRole = "admin" | "super-admin";

function secureEqual(left: string, right: string): boolean {
  const leftBuffer = Buffer.from(left);
  const rightBuffer = Buffer.from(right);
  if (leftBuffer.length !== rightBuffer.length) {
    return false;
  }
  return timingSafeEqual(leftBuffer, rightBuffer);
}

export function authorizeSettingsWrite(
  request: NextRequest,
  role: SettingsRole,
): { authorized: true } | { authorized: false; status: number; message: string } {
  const envName =
    role === "super-admin"
      ? "ZYLORA_SUPER_ADMIN_SETTINGS_KEY"
      : "ZYLORA_ADMIN_SETTINGS_KEY";
  const expectedKey = process.env[envName];

  if (!expectedKey) {
    if (process.env.NODE_ENV !== "production") {
      return { authorized: true };
    }
    return {
      authorized: false,
      status: 503,
      message: `${envName} is not configured.`,
    };
  }

  const providedKey = request.headers.get("x-zylora-settings-key") ?? "";
  if (!providedKey || !secureEqual(providedKey, expectedKey)) {
    return {
      authorized: false,
      status: 401,
      message: "Invalid settings access key.",
    };
  }

  return { authorized: true };
}
