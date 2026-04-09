/**
 * Shared helpers for Playwright frontend tests.
 */
import { MOCK_DATA } from "./mocks/data.js";

/**
 * Intercept all admin API routes and return mock data.
 * Returns a map of resource -> request count for verification.
 */
export async function mockAllAdminRoutes(page) {
  const requestCounts = {};
  for (const resource of Object.keys(MOCK_DATA)) {
    requestCounts[resource] = 0;
  }

  await page.route("**/api/v1/admin/**", (route) => {
    const url = route.request().url();
    for (const resource of Object.keys(MOCK_DATA)) {
      if (url.endsWith(`/admin/${resource}`)) {
        requestCounts[resource]++;
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(MOCK_DATA[resource]),
        });
      }
    }
    return route.abort();
  });

  return requestCounts;
}

/**
 * Intercept a specific admin route and return custom data.
 */
export async function mockAdminRoute(page, resource, data, status = 200) {
  await page.route(`**/api/v1/admin/${resource}`, (route) => {
    return route.fulfill({
      status,
      contentType: "application/json",
      body: JSON.stringify(data),
    });
  });
}

/**
 * Intercept a specific admin route and abort (simulate network failure).
 */
export async function mockAdminRouteAbort(page, resource) {
  await page.route(`**/api/v1/admin/${resource}`, (route) => {
    return route.abort("failed");
  });
}

/**
 * Navigate to a specific hash route and wait for the table or content to load.
 */
export async function navigateToRoute(page, resource) {
  await page.goto(`/static/index.html#/${resource}`);
  // Wait for content area to have either a table or an error/message
  await page.waitForFunction(() => {
    const content = document.getElementById("content");
    return content && content.textContent !== "Loading...";
  }, { timeout: 5000 });
}
