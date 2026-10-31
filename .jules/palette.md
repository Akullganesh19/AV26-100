## 2024-10-31 — Accessible custom form controls in Calculator
**Found:** Custom radio buttons (using `<button>`) and custom checkboxes (using `hidden` on native inputs) in the estimation calculator were missing required accessibility semantics.
**Why it existed:** Native form controls are notoriously hard to style identically across browsers, so developers often build visual replicas, inadvertently dropping keyboard and screen reader support.
**Fix:** Restored semantics using `role="radiogroup"`, `role="radio"`, and `aria-checked` on buttons. Swapped `hidden` for Tailwind's `sr-only peer` on checkboxes to maintain DOM presence and enable `peer-focus-visible` styling for keyboard navigation.
**Learning:** Always use `sr-only` instead of `hidden` for native inputs driving custom UI, and explicitly map ARIA roles/states for simulated controls.
**Watch for:** Other forms or filters using `<div onClick={...}>` or `<button>` as radios/checkboxes without proper roles.
