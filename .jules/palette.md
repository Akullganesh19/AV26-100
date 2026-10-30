## 2024-05-18 — Custom Form Element Accessibility
**Found:** Interactive custom elements (checkboxes, radios, sliders) built with generic divs/buttons or hidden native inputs.
**Why it existed:** Tailwind UI custom styling required hiding native inputs, leading to lost accessibility trees and focus states.
**Fix:** Replaced `hidden` with `sr-only peer` on inputs, added `peer-focus-visible` for custom focus rings, and added `role="radiogroup"`, `role="radio"`, and `aria-checked` to custom radio buttons.
**Learning:** Always use `sr-only peer` instead of `hidden` for custom styled inputs to maintain keyboard navigation. Ensure custom interactive elements have appropriate ARIA roles.
**Watch for:** Other custom form components that might be masking native inputs completely.
