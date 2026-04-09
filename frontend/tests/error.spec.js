// @ts-check
import { test, expect } from "@playwright/test";
import { mockAllAdminRoutes, mockAdminRoute, mockAdminRouteAbort } from "./helpers.js";

test.describe("Error tests", () => {
  test("mocked 500 response shows error message with HTTP status code", async ({ page }) => {
    await mockAdminRoute(page, "accounts", { detail: "Internal server error" }, 500);
    await page.goto("/static/index.html#/accounts");

    // Wait for error to render
    await page.waitForFunction(() => {
      const content = document.getElementById("content");
      return content && content.textContent !== "Loading...";
    }, { timeout: 5000 });

    const content = page.locator("#content");
    const text = await content.textContent();

    // Should contain the status code
    expect(text).toContain("500");
    // Should be a "Failed to load" style message
    expect(text).toContain("Failed to load");
  });

  test("mocked network failure shows transport error message without status code", async ({ page }) => {
    await mockAdminRouteAbort(page, "accounts");
    await page.goto("/static/index.html#/accounts");

    // Wait for error to render
    await page.waitForFunction(() => {
      const content = document.getElementById("content");
      return content && content.textContent !== "Loading...";
    }, { timeout: 5000 });

    const content = page.locator("#content");
    const text = await content.textContent();

    // Should show network error message
    expect(text).toContain("Network error");
    // Should NOT contain a numeric HTTP status code
    expect(text).not.toMatch(/\b[45]\d{2}\b/);
  });

  test("invalid hash route shows 'Unknown route' message", async ({ page }) => {
    await mockAllAdminRoutes(page);
    await page.goto("/static/index.html#/nonexistent");

    const content = page.locator("#content");
    await expect(content).toHaveText("Unknown route");
  });

  test("non-array API response shows error message", async ({ page }) => {
    // Return an object instead of an array
    await mockAdminRoute(page, "accounts", { not: "an array" });
    await page.goto("/static/index.html#/accounts");

    await page.waitForFunction(() => {
      const content = document.getElementById("content");
      return content && content.textContent !== "Loading...";
    }, { timeout: 5000 });

    const content = page.locator("#content");
    const text = await content.textContent();
    expect(text).toContain("Expected array response");
  });
});
