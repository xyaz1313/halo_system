# Frontend Testing Spec

Minimal for now — the frontend is a simple read-only browser.

## Framework

- TBD based on tech choice (Vitest if React, manual if plain HTML/JS)

## Tests

### Smoke Tests

- Each page route loads without error
- Navbar renders with all links
- Navbar links navigate to correct routes

### Data Display Tests

- Each table page fetches from the correct admin API route
- Table renders correct columns for the model
- Table renders rows matching API response data
- Empty table shows empty state (not an error)

## Running Tests

TBD — depends on frontend tech choice.
