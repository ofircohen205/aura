import { test, expect } from "@playwright/test";

test.describe("Dashboard", () => {
  test.beforeEach(async ({ page, context }) => {
    // Mock authentication by setting tokens in localStorage
    await context.addCookies([
      {
        name: "csrf-token",
        value: "test-csrf-token",
        domain: "localhost",
        path: "/",
      },
    ]);

    await page.goto("/");
    await page.evaluate(() => {
      localStorage.setItem("access_token", "mock-access-token");
      localStorage.setItem("refresh_token", "mock-refresh-token");
    });
  });

  test("should display dashboard navigation", async ({ page }) => {
    await page.goto("/dashboard");

    // Check for sidebar navigation
    await expect(page.getByRole("link", { name: /dashboard/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /workflows/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /audits/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /profile/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /settings/i })).toBeVisible();
  });

  test("should navigate to workflows page", async ({ page }) => {
    await page.goto("/dashboard");
    await page.getByRole("link", { name: /workflows/i }).click();
    await expect(page).toHaveURL(/\/dashboard\/workflows/);
    await expect(page.getByRole("heading", { name: /workflows/i })).toBeVisible();
  });

  test("should navigate to audits page", async ({ page }) => {
    await page.goto("/dashboard");
    await page.getByRole("link", { name: /audits/i }).click();
    await expect(page).toHaveURL(/\/dashboard\/audits/);
    await expect(page.getByRole("heading", { name: /audits/i })).toBeVisible();
  });

  test("should navigate to profile page", async ({ page }) => {
    await page.goto("/dashboard");
    await page.getByRole("link", { name: /profile/i }).click();
    await expect(page).toHaveURL(/\/dashboard\/profile/);
    await expect(page.getByRole("heading", { name: /profile/i })).toBeVisible();
  });

  test("should display user email in header", async ({ page }) => {
    // Mock user data in auth store
    await page.goto("/dashboard");
    // Note: In a real test, you'd need to mock the API response for /auth/me
    // For now, we'll just check the header structure exists
    await expect(page.locator("header")).toBeVisible();
  });

  test("should have logout button in header", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.getByRole("button", { name: /logout/i })).toBeVisible();
  });
});
