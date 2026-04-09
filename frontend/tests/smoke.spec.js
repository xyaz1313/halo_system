// @ts-check
import { test, expect } from "@playwright/test";
import { ROUTES, ROUTE_LABELS } from "./mocks/data.js";
import { mockAllAdminRoutes, navigateToRoute } from "./helpers.js";

test.describe("Smoke tests", () => {
  test.describe("Each hash route loads without JS errors", () => {
    for (const resource of ROUTES) {
      test(`#/${resource} loads without errors`, async ({ page }) => {
        const errors = [];
        page.on("pageerror", (err) => errors.push(err.message));

        await mockAllAdminRoutes(page);
        await navigateToRoute(page, resource);

        expect(errors).toEqual([]);
      });
    }
  });

  test.describe("Navbar renders 6 links on every route", () => {
    for (const resource of ROUTES) {
      test(`navbar has 6 links on #/${resource}`, async ({ page }) => {
        await mockAllAdminRoutes(page);
        await navigateToRoute(page, resource);

        const navLinks = page.locator("nav a[href^='#/']");
        await expect(navLinks).toHaveCount(6);
      });
    }
  });

  test.describe("Clicking each navbar link navigates correctly", () => {
    for (const resource of ROUTES) {
      test(`clicking ${ROUTE_LABELS[resource]} nav link navigates to #/${resource}`, async ({ page }) => {
        await mockAllAdminRoutes(page);
        // Start on a different route to verify navigation
        const startRoute = resource === "accounts" ? "anchors" : "accounts";
        await navigateToRoute(page, startRoute);

        const link = page.locator(`nav a[href='#/${resource}']`);
        await link.click();

        // Wait for navigation to complete
        await page.waitForFunction(
          (r) => {
            const content = document.getElementById("content");
            return (
              window.location.hash === `#/${r}` &&
              content &&
              content.textContent !== "Loading..."
            );
          },
          resource,
          { timeout: 5000 }
        );

        expect(page.url()).toContain(`#/${resource}`);
      });
    }
  });

  test("root / redirect lands on /static/index.html defaulting to #/accounts", async ({ page }) => {
    await mockAllAdminRoutes(page);
    await page.goto("/");
    // Should redirect to /static/index.html
    await page.waitForURL("**/static/index.html**");
    // Wait for default hash route
    await page.waitForFunction(
      () => window.location.hash === "#/accounts",
      { timeout: 5000 }
    );
    expect(page.url()).toContain("/static/index.html#/accounts");
  });

  test("nav element has aria-label for accessibility", async ({ page }) => {
    await mockAllAdminRoutes(page);
    await navigateToRoute(page, "accounts");

    const nav = page.locator("nav");
    await expect(nav).toHaveAttribute("aria-label", "Main navigation");
  });

  test("active nav link sets aria-current='page' correctly per route", async ({ page }) => {
    await mockAllAdminRoutes(page);

    for (const resource of ROUTES) {
      await navigateToRoute(page, resource);

      // The active link should have aria-current="page"
      const activeLink = page.locator(`nav a[href='#/${resource}']`);
      await expect(activeLink).toHaveAttribute("aria-current", "page");

      // All other nav links should NOT have aria-current
      for (const other of ROUTES) {
        if (other !== resource) {
          const otherLink = page.locator(`nav a[href='#/${other}']`);
          const ariaCurrent = await otherLink.getAttribute("aria-current");
          expect(ariaCurrent).toBeNull();
        }
      }
    }
  });
});
