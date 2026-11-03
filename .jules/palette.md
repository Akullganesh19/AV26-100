## 2026-11-03 - Keyboard Accessible Custom Form Controls
**Learning:** When building custom checkboxes with Tailwind, using `hidden` on the native input completely breaks keyboard navigation. The input must be visually hidden using `sr-only peer` and placed immediately before the custom visual element in the DOM to utilize `peer-focus-visible` styles.
**Action:** Always verify keyboard focus states and use `sr-only peer` rather than `hidden` for custom inputs.
