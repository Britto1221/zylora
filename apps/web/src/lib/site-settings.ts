import { promises as fs } from "node:fs";
import path from "node:path";
import { z } from "zod";

export const siteSlugSchema = z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, "Invalid site slug.");

export const platformSettingsSchema = z.object({
  zyloraContactEmail: z.string().trim().email().max(254),
  updatedAt: z.string().datetime(),
});

export const tenantSiteSettingsSchema = z.object({
  businessName: z.string().trim().min(2).max(120),
  email: z.string().trim().email().max(254),
  phone: z.string().trim().min(5).max(32),
  address: z.string().trim().min(5).max(300),
  updatedAt: z.string().datetime(),
});

export const tenantSiteSettingsInputSchema = tenantSiteSettingsSchema.omit({
  updatedAt: true,
});

export const platformSettingsInputSchema = platformSettingsSchema.omit({
  updatedAt: true,
});

export type PlatformSettings = z.infer<typeof platformSettingsSchema>;
export type TenantSiteSettings = z.infer<typeof tenantSiteSettingsSchema>;
export type TenantSiteSettingsInput = z.infer<typeof tenantSiteSettingsInputSchema>;
export type PlatformSettingsInput = z.infer<typeof platformSettingsInputSchema>;

type TenantSiteSettingsMap = Record<string, TenantSiteSettings>;

const dataDirectory = process.env.ZYLORA_SETTINGS_DATA_DIR
  ? path.resolve(process.env.ZYLORA_SETTINGS_DATA_DIR)
  : path.join(process.cwd(), "data");
const platformSettingsPath = path.join(dataDirectory, "platform-settings.json");
const tenantSettingsPath = path.join(dataDirectory, "tenant-sites.json");

const defaultPlatformSettings: PlatformSettings = {
  zyloraContactEmail: "hello@zylora.ai",
  updatedAt: "2026-07-17T00:00:00.000Z",
};

function titleFromSlug(slug: string): string {
  return slug
    .split("-")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function defaultTenantSettings(slug: string): TenantSiteSettings {
  return {
    businessName: titleFromSlug(slug) || "Demo Business",
    email: "hello@example.com",
    phone: "+91 90000 00000",
    address: "Chennai, Tamil Nadu, India",
    updatedAt: "2026-07-17T00:00:00.000Z",
  };
}

async function ensureDataDirectory(): Promise<void> {
  await fs.mkdir(dataDirectory, { recursive: true });
}

async function readJson<T>(filePath: string, fallback: T): Promise<T> {
  try {
    const raw = await fs.readFile(filePath, "utf8");
    return JSON.parse(raw) as T;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") {
      return fallback;
    }
    throw error;
  }
}

async function writeJsonAtomically(filePath: string, value: unknown): Promise<void> {
  await ensureDataDirectory();
  const tempPath = `${filePath}.${process.pid}.${Date.now()}.tmp`;
  await fs.writeFile(tempPath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
  await fs.rename(tempPath, filePath);
}

export async function getPlatformSettings(): Promise<PlatformSettings> {
  const value = await readJson(platformSettingsPath, defaultPlatformSettings);
  const parsed = platformSettingsSchema.safeParse(value);
  return parsed.success ? parsed.data : defaultPlatformSettings;
}

export async function updatePlatformSettings(
  input: PlatformSettingsInput,
): Promise<PlatformSettings> {
  const parsed = platformSettingsInputSchema.parse(input);
  const value: PlatformSettings = {
    ...parsed,
    updatedAt: new Date().toISOString(),
  };
  await writeJsonAtomically(platformSettingsPath, value);
  return value;
}

export async function getTenantSiteSettings(
  slug: string,
): Promise<TenantSiteSettings> {
  const validatedSlug = siteSlugSchema.parse(slug);
  const allSettings = await readJson<TenantSiteSettingsMap>(tenantSettingsPath, {});
  const candidate = allSettings[validatedSlug];
  const parsed = tenantSiteSettingsSchema.safeParse(candidate);
  return parsed.success ? parsed.data : defaultTenantSettings(validatedSlug);
}

export async function updateTenantSiteSettings(
  slug: string,
  input: TenantSiteSettingsInput,
): Promise<TenantSiteSettings> {
  const validatedSlug = siteSlugSchema.parse(slug);
  const parsed = tenantSiteSettingsInputSchema.parse(input);
  const allSettings = await readJson<TenantSiteSettingsMap>(tenantSettingsPath, {});
  const value: TenantSiteSettings = {
    ...parsed,
    updatedAt: new Date().toISOString(),
  };
  allSettings[validatedSlug] = value;
  await writeJsonAtomically(tenantSettingsPath, allSettings);
  return value;
}
