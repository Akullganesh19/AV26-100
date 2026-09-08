## 2025-09-08 — Accessible Custom Form Controls
**Found:** Custom checkboxes and radio buttons in the CalculatorSection were hidden (`display: none` via `hidden` class) or implemented as plain `button` elements without `focus-visible` styles or proper ARIA roles.
**Why it existed:** Custom UI styling often relies on hiding the native input entirely and swapping a visual element based on state, stripping away native focus management and screen reader semantics.
**Fix:** Swapped `hidden` for `sr-only peer` on checkboxes and applied `peer-focus-visible` styles to the custom visual boxes. Upgraded custom radio buttons with `role="radio"`, `aria-checked`, and `focus-visible` classes within `role="radiogroup"` containers.
**Learning:** Always preserve the native input or explicitly add back ARIA roles and keyboard focus styles when building custom form controls with Tailwind.
**Watch for:** Other custom form elements (switches, tabs, segmented controls) that might be missing focus rings or semantic roles.
