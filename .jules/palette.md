## 2025-02-18 — Accessible Custom Controls
**Found:** Custom UI controls (radio buttons, checkboxes) lacked proper ARIA roles, states, and keyboard focus visibility. Checkboxes were completely hidden from screen readers due to `className="hidden"`.
**Why it existed:** Developers often prioritize visual aesthetics for custom controls, ignoring semantic HTML and screen reader accessibility. Hiding the native `<input>` entirely removes it from the accessibility tree.
**Fix:** Added `role="radiogroup"`, `role="radio"`, and `aria-checked` to pseudo-radio buttons. Replaced `className="hidden"` on checkboxes with `className="sr-only peer"` (ensuring it's in the DOM before the visual element) and used `peer-focus-visible:ring-2` for accessible focus states. Added `aria-label` to the range slider.
**Learning:** When building custom controls in Tailwind, always use `sr-only peer` on the native `<input>` to preserve accessibility while hiding it visually, and use `peer-focus-visible` for keyboard focus styles.
**Watch for:** Other custom implementations of standard HTML form controls throughout the codebase that might be inaccessible.
