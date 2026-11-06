## 2024-11-06 — Accessible Custom Controls
**Found:** Custom radio buttons and checkboxes in CalculatorSection were built using `<button>` elements (for radios) and `hidden` native inputs (for checkboxes), rendering them inaccessible to screen readers and keyboard navigation.
**Why it existed:** Developers often build custom UI by hiding native inputs with `display: none` or using `div`/`button` without realizing it removes them from the accessibility tree and breaks native focus management.
**Fix:** Converted simulated radios to `<label>` with `<input type="radio" className="sr-only peer">`, and moved native checkbox inputs before their custom styling element with `sr-only peer`. Added `peer-focus-visible` for keyboard focus states.
**Learning:** Always use native inputs for forms. Hide them visually with `sr-only` instead of `hidden`, and use sibling selectors (Tailwind's `peer`) to style the custom UI based on the native input's state (checked, focus-visible).
**Watch for:** Other custom toggles, switches, or stylized form elements that might be bypassing native accessibility properties by using `hidden` or generic tags.
