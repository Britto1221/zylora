import { revalidatePath } from "next/cache";
import { NextResponse, type NextRequest } from "next/server";
import { ZodError } from "zod";
import { authorizeSettingsWrite } from "@/lib/settings-auth";
import {
  getTenantSiteSettings,
  tenantSiteSettingsInputSchema,
  updateTenantSiteSettings,
} from "@/lib/site-settings";

export const dynamic = "force-dynamic";

export async function GET(
  _request: NextRequest,
  context: { params: Promise<{ slug: string }> },
) {
  const { slug } = await context.params;
  const settings = await getTenantSiteSettings(slug);
  return NextResponse.json({ settings });
}

export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ slug: string }> },
) {
  const authorization = authorizeSettingsWrite(request, "admin");
  if (!authorization.authorized) {
    return NextResponse.json(
      { error: authorization.message },
      { status: authorization.status },
    );
  }

  try {
    const { slug } = await context.params;
    const body = await request.json();
    const input = tenantSiteSettingsInputSchema.parse(body);
    const settings = await updateTenantSiteSettings(slug, input);
    revalidatePath(`/sites/${slug}`);
    revalidatePath(`/admin/sites/${slug}/settings`);
    revalidatePath(`/admin/sites/${slug}/dashboard`);
    return NextResponse.json({ settings });
  } catch (error) {
    if (error instanceof ZodError) {
      return NextResponse.json(
        { error: "Invalid landing-page settings.", issues: error.issues },
        { status: 400 },
      );
    }
    console.error("Unable to update tenant landing-page settings", error);
    return NextResponse.json(
      { error: "Unable to save landing-page settings." },
      { status: 500 },
    );
  }
}
