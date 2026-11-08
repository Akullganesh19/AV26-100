## 2025-05-23 — Accessibility Improvements for Form Controls
**Found:** Simulated radio buttons built with `<button>` elements, checkboxes using `hidden`, and missing ID associations between labels and input fields.
**Why it existed:** A common pattern of relying on JS logic for state without ensuring proper HTML structure and a11y attributes.
**Fix:** Replaced `<button>` simulated radios with native `<input type="radio">` wrapped in `<label>`. Updated checkboxes to use `sr-only peer` for visual hiding. Added `React.useId()` to properly associate `<label>` and `<input>`/`<select>`.
**Learning:** Always use native form controls (`<input type="radio">`, `<input type="checkbox">`) for forms. Ensure proper label association and visibility for screen readers.
**Watch for:** Other custom UI controls lacking proper a11y structure and attributes.
