## 2023-11-01 — Accessible Custom Checkboxes and Radio Buttons
**Found:** Custom checkboxes using `hidden` on native inputs, and simulated radio buttons (`<button>`) lacking ARIA roles.
**Why it existed:** Native inputs are often hidden for styling purposes without realizing it removes them from the accessibility tree. `<button>` elements were used for custom layouts without conveying their radio button behavior.
**Fix:** Used `sr-only peer` on inputs and `peer-focus-visible` for styling. Added `role="radiogroup"`, `role="radio"`, and `aria-checked` to simulated radio buttons.
**Learning:** When building custom styled controls, always keep native inputs in the DOM with `sr-only` for checkboxes/radios, or properly implement ARIA roles for custom elements.
**Watch for:** Other custom form controls in the codebase that use `display: none` or `hidden` on their native inputs or lack appropriate ARIA roles.
