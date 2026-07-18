import { revalidatePath } from "next/cache";
import { NextResponse, type NextRequest } from "next/server";
import { ZodError } from "zod";
import { authorizeSettingsWrite } from "@/lib/settings-auth";
import {
  getPlatformSettings,
  platformSettingsInputSchema,
  updatePlatformSettings,
} from "@/lib/site-settings";

export const dynamic = "force-dynamic";

export async function GET() {
  const settings = await getPlatformSettings();
  return NextResponse.json({ settings });
}

export async function PUT(request: NextRequest) {
  const authorization = authorizeSettingsWrite(request, "super-admin");
  if (!authorization.authorized) {
    return NextResponse.json(
      { error: authorization.message },
      { status: authorization.status },
    );
  }

  try {
    const body = await request.json();
    const input = platformSettingsInputSchema.parse(body);
    const settings = await updatePlatformSettings(input);
    revalidatePath("/");
    revalidatePath("/super-admin/settings");
    revalidatePath("/super-admin/dashboard");
    return NextResponse.json({ settings });
  } catch (error) {
    if (error instanceof ZodError) {
      return NextResponse.json(
        { error: "Enter a valid Zylora email address.", issues: error.issues },
        { status: 400 },
      );
    }
    console.error("Unable to update Zylora platform settings", error);
    return NextResponse.json(
      { error: "Unable to save Zylora settings." },
      { status: 500 },
    );
  }
}
