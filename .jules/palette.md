## 2024-05-24 — Accessible Simulated Controls
**Found:** Radio buttons and checkboxes were built using simulated `<button>` and `<label>` structures with hidden `<input>` elements.
**Why it existed:** To achieve custom visual styling that doesn't rely on browser defaults, often found in high-design generic templates.
**Fix:** Replaced `<button>` wrappers with `<label>`, added native `<input type="radio" className="sr-only peer">` (and similar for checkboxes), and placed them before the custom visual styling elements. Added `peer-focus-visible` styles to the custom elements to restore keyboard focus rings without affecting visual appearance for mouse users.
**Learning:** When custom interactive elements are built, developers often hide native inputs completely (`hidden` or `display: none`), which removes them from the accessibility tree. The `sr-only peer` pattern is crucial for maintaining both design and accessibility.
**Watch for:** Other custom toggles, switches, or checkboxes that might use `div` or `button` elements instead of semantically correct native inputs.
