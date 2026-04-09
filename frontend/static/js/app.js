/**
 * Router and initialization for the Halo Admin frontend.
 */

import { COLUMNS } from "./columns.js";
import { fetchAdmin } from "./api.js";
import { renderTable } from "./table.js";

const ROUTES = ["accounts", "anchors", "tags", "associations", "calendars", "preferences"];

const content = document.getElementById("content");

/** Generation counter to prevent race conditions from rapid navigation. */
let navigationGeneration = 0;

/**
 * Extract the resource name from the current hash.
 * Returns null if hash is empty or root, "unknown" if hash does not match
 * a known route, or the resource name if valid.
 */
function getRouteFromHash() {
  const hash = window.location.hash;
  if (!hash || hash === "#" || hash === "#/") {
    return null;
  }
  const resource = hash.replace("#/", "");
  if (ROUTES.includes(resource)) {
    return resource;
  }
  return "unknown";
}

/**
 * Update the navbar to mark the active link.
 */
function updateNavbar(activeResource) {
  const links = document.querySelectorAll("nav a[href^='#/']");
  for (const link of links) {
    const linkResource = link.getAttribute("href").replace("#/", "");
    if (linkResource === activeResource) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  }
}

/**
 * Navigate to the given resource: update navbar, fetch data, render table.
 */
async function navigate(resource) {
  const gen = ++navigationGeneration;

  updateNavbar(resource);

  // Show loading state
  content.textContent = "Loading...";

  try {
    const rows = await fetchAdmin(resource);
    if (gen !== navigationGeneration) return; // stale response, discard
    const columns = COLUMNS[resource];
    renderTable(content, columns, rows);
  } catch (err) {
    if (gen !== navigationGeneration) return; // stale error, discard
    content.textContent = err.message;
  }
}

/**
 * Handle hash changes.
 */
function onHashChange() {
  const resource = getRouteFromHash();
  if (resource === "unknown") {
    content.textContent = "Unknown route";
  } else if (resource) {
    navigate(resource);
  } else {
    // Default to accounts
    window.location.hash = "#/accounts";
  }
}

// Initialize
window.addEventListener("hashchange", onHashChange);

// On initial load, navigate based on current hash or default
onHashChange();
