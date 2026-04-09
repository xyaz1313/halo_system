/**
 * Generic table renderer using DOM APIs and DocumentFragment.
 */

/**
 * Format a cell value for display.
 * @param {*} value
 * @returns {string}
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
 * Humanize a column key for display as a header.
 * Replaces underscores with spaces and title-cases each word.
 * @param {string} col
 * @returns {string}
 */
function humanizeHeader(col) {
  return col
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Render a table into a container element.
 * @param {HTMLElement} container - Element to render into (will be cleared)
 * @param {string[]} columns - Ordered column keys
 * @param {Array<Object>} rows - Data rows
 */
export function renderTable(container, columns, rows) {
  const fragment = document.createDocumentFragment();

  const table = document.createElement("table");
  table.setAttribute("role", "grid");

  // Header
  const thead = document.createElement("thead");
  const headerRow = document.createElement("tr");
  for (const col of columns) {
    const th = document.createElement("th");
    th.textContent = humanizeHeader(col);
    th.setAttribute("scope", "col");
    headerRow.appendChild(th);
  }
  thead.appendChild(headerRow);
  table.appendChild(thead);

  // Body
  const tbody = document.createElement("tbody");
  if (rows.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.setAttribute("colspan", String(columns.length));
    td.textContent = "No records found";
    tr.appendChild(td);
    tbody.appendChild(tr);
  } else {
    for (const row of rows) {
      const tr = document.createElement("tr");
      for (const col of columns) {
        const td = document.createElement("td");
        td.textContent = formatValue(row[col]);
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
  }
  table.appendChild(tbody);

  fragment.appendChild(table);
  container.textContent = "";
  container.appendChild(fragment);
}
