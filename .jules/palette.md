## $(date +%Y-%m-%d) — Accessible Custom Form Controls

**Found:** Custom pseudo-radio buttons, custom checkboxes, and range sliders were inaccessible to screen reader and keyboard users in `CalculatorSection.tsx`. Sliders lacked labels, pseudo-radios lacked roles and ARIA states, checkboxes were completely hidden from the accessibility tree, and all lacked visual focus indicators.
**Why it existed:** The components were built prioritizing visual aesthetics over semantic HTML, relying on `<div>` and `<button>` elements for styling without adding the necessary accessibility layer, and using `className="hidden"` which inherently destroys keyboard accessibility.
**Fix:**
- Added `aria-label` to the `Slider` input.
- Added `role="radiogroup"` to pseudo-radio containers, and `role="radio"`, `aria-checked` to the button elements.
- Replaced `className="hidden"` with `className="sr-only peer"` on checkboxes and moved the input *before* the visual indicator element.
- Added `focus-visible:ring-2` (and `peer-focus-visible` for checkboxes) to all interactive elements to ensure keyboard focus visibility.
**Learning:** When building custom checkboxes or radio buttons in Tailwind, do not use `className="hidden"` on the underlying `<input>` element, as this removes it from the accessibility tree and breaks keyboard navigation. Instead, apply `className="sr-only peer"` to the input (ensuring the input is placed *before* the visual element in the DOM tree so the peer modifier works) and use `peer-focus-visible` (e.g., `peer-focus-visible:ring-2`) on the adjacent custom visual element.
**Watch for:** Other areas of the application using custom form components or visual overrides that might be using `className="hidden"` or lacking ARIA roles.
