import { expect, test } from "@playwright/test";

test("marketing page and admin login render", async ({ page }: { page: any }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await page.goto("/login");
  await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible();
});
