// @ts-check
import { test, expect } from "@playwright/test";
import { ROUTES, COLUMNS, MOCK_DATA } from "./mocks/data.js";
import { mockAllAdminRoutes, mockAdminRoute, navigateToRoute } from "./helpers.js";

/**
 * Format a value the same way the frontend does, for assertion comparison.
 */
function formatValue(value) {
  if (value === null || value === undefined) {
    return "\u2014"; // em dash
  }
  if (Array.isArray(value)) {
    if (value.length === 0) {
      return "\u2014"; // em dash for empty arrays
    }
    return value.map(formatValue).join(", ");
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

/**
 * Humanize a column key the same way the frontend does.
 */
function humanizeHeader(col) {
  return col
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

test.describe("Data display tests", () => {
  test.describe("Each page fetches from correct admin endpoint", () => {
    for (const resource of ROUTES) {
      test(`#/${resource} fetches /api/v1/admin/${resource}`, async ({ page }) => {
        const requestCounts = await mockAllAdminRoutes(page);
        await navigateToRoute(page, resource);

        expect(requestCounts[resource]).toBeGreaterThanOrEqual(1);
      });
    }
  });

  test.describe("Table columns match column definitions", () => {
    for (const resource of ROUTES) {
      test(`#/${resource} renders correct column headers`, async ({ page }) => {
        await mockAllAdminRoutes(page);
        await navigateToRoute(page, resource);

        const headers = page.locator("table thead th");
        const expectedColumns = COLUMNS[resource];

        await expect(headers).toHaveCount(expectedColumns.length);

        for (let i = 0; i < expectedColumns.length; i++) {
          await expect(headers.nth(i)).toHaveText(humanizeHeader(expectedColumns[i]));
        }
      });
    }
  });

  test.describe("Table rows match mock response data", () => {
    for (const resource of ROUTES) {
      test(`#/${resource} renders correct row data`, async ({ page }) => {
        await mockAllAdminRoutes(page);
        await navigateToRoute(page, resource);

        const rows = page.locator("table tbody tr");
        const expectedRows = MOCK_DATA[resource];
        const columns = COLUMNS[resource];

        await expect(rows).toHaveCount(expectedRows.length);

        for (let rowIdx = 0; rowIdx < expectedRows.length; rowIdx++) {
          const cells = rows.nth(rowIdx).locator("td");
          for (let colIdx = 0; colIdx < columns.length; colIdx++) {
            const expected = formatValue(expectedRows[rowIdx][columns[colIdx]]);
            await expect(cells.nth(colIdx)).toHaveText(expected);
          }
        }
      });
    }
  });

  test.describe("Empty response renders headers plus 'No records found'", () => {
    for (const resource of ROUTES) {
      test(`#/${resource} empty response shows column headers and empty message`, async ({ page }) => {
        await mockAdminRoute(page, resource, []);
        await navigateToRoute(page, resource);

        // Column headers should still render
        const headers = page.locator("table thead th");
        const expectedColumns = COLUMNS[resource];
        await expect(headers).toHaveCount(expectedColumns.length);

        for (let i = 0; i < expectedColumns.length; i++) {
          await expect(headers.nth(i)).toHaveText(humanizeHeader(expectedColumns[i]));
        }

        // Body should have one row with "No records found"
        const bodyRows = page.locator("table tbody tr");
        await expect(bodyRows).toHaveCount(1);

        const cell = bodyRows.first().locator("td");
        await expect(cell).toHaveText("No records found");
        await expect(cell).toHaveAttribute("colspan", String(expectedColumns.length));
      });
    }
  });

  test("null values render as em dash", async ({ page }) => {
    await mockAllAdminRoutes(page);

    // Accounts mock has null caretaker_name, caretaker_email, patient_notes on second row
    await navigateToRoute(page, "accounts");

    const secondRow = page.locator("table tbody tr").nth(1);
    const cells = secondRow.locator("td");

    // patient_notes is column index 5, caretaker_name is 6, caretaker_email is 7
    await expect(cells.nth(5)).toHaveText("\u2014");
    await expect(cells.nth(6)).toHaveText("\u2014");
    await expect(cells.nth(7)).toHaveText("\u2014");

    // Anchors mock has null owner_account_id on first row (column index 3)
    await navigateToRoute(page, "anchors");
    const firstRow = page.locator("table tbody tr").nth(0);
    await expect(firstRow.locator("td").nth(3)).toHaveText("\u2014");

    // Calendars mock has null last_synced_at on second row (column index 5)
    await navigateToRoute(page, "calendars");
    const calSecondRow = page.locator("table tbody tr").nth(1);
    await expect(calSecondRow.locator("td").nth(5)).toHaveText("\u2014");
  });

  test("alert_types array renders as comma-separated string", async ({ page }) => {
    await mockAllAdminRoutes(page);
    await navigateToRoute(page, "preferences");

    const firstRow = page.locator("table tbody tr").nth(0);
    const cells = firstRow.locator("td");

    // alert_types is column index 3
    await expect(cells.nth(3)).toHaveText("departure, arrival, low_battery");

    // Second row has empty array — renders as em dash
    const secondRow = page.locator("table tbody tr").nth(1);
    await expect(secondRow.locator("td").nth(3)).toHaveText("\u2014");
  });
});
