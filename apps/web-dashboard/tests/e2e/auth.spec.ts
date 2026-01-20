import { test, expect } from "@playwright/test";

test.describe("Authentication Flow", () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage before each test
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
  });

  test("should redirect to login when not authenticated", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/auth\/login/);
  });

  test("should display login form", async ({ page }) => {
    await page.goto("/auth/login");
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /login/i })).toBeVisible();
    // Check for register link
    await expect(page.getByRole("link", { name: /register/i })).toBeVisible();
  });

  test("should show validation errors for invalid input", async ({ page }) => {
    await page.goto("/auth/login");

    // Try to submit empty form
    await page.getByRole("button", { name: /login/i }).click();

    // Should show validation errors
    await expect(page.getByText(/invalid email address/i)).toBeVisible();
    await expect(page.getByText(/password is required/i)).toBeVisible();
  });

  test("should navigate to register page", async ({ page }) => {
    await page.goto("/auth/login");
    await page.getByRole("link", { name: /register/i }).click();
    await expect(page).toHaveURL(/\/auth\/register/);
  });

  test("should display register form", async ({ page }) => {
    await page.goto("/auth/register");
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/username/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
    await expect(page.getByLabel(/confirm password/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /register/i })).toBeVisible();
  });

  test("should show password validation errors", async ({ page }) => {
    await page.goto("/auth/register");

    // Fill form with weak password
    await page.getByLabel(/email/i).fill("test@example.com");
    await page.getByLabel(/username/i).fill("testuser");
    await page.getByLabel(/password/i).fill("weak");
    await page.getByLabel(/confirm password/i).fill("weak");
    await page.getByRole("button", { name: /register/i }).click();

    // Should show password validation error
    await expect(page.getByText(/password must be at least 8 characters/i)).toBeVisible();
  });
});
