/**
 * Fetch wrapper for admin API endpoints.
 */

/**
 * Fetch data from an admin endpoint.
 * @param {string} endpoint - Resource name (e.g. "accounts")
 * @returns {Promise<Array>} Parsed JSON array
 * @throws {Error} On HTTP non-OK, network failure, or non-array response
 */
export async function fetchAdmin(endpoint) {
  let response;
  try {
    response = await fetch(`/api/v1/admin/${endpoint}`, {
      headers: { Accept: "application/json" },
    });
  } catch (err) {
    throw new Error(`Network error: ${err.message}`);
  }

  if (!response.ok) {
    let body = "";
    try {
      body = await response.text();
    } catch {
      // ignore body read failure
    }
    throw new Error(`Failed to load: ${response.status} ${body}`);
  }

  const data = await response.json();
  if (!Array.isArray(data)) {
    throw new Error("Expected array response from API");
  }
  return data;
}
