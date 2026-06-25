## $(date +%Y-%m-%d) — Accessible Custom Form Elements
**Found:** Custom radio buttons (for service type and timeline) and checkboxes (for add-ons) in `CalculatorSection.tsx` were built with native interactive elements (`button`, `input type="checkbox"`) but overridden by custom styles that ruined their accessibility. Specifically, checkboxes were hidden (`display: none`), removing them from keyboard focus. The custom `button` radios lacked `role="radio"`, `aria-checked`, and focus-visible states. The range slider also lacked an `aria-label` and focus ring.
**Why it existed:** Developers often hide the native `input` entirely to style a custom square/circle next to it, breaking focusability. Native radios were replaced by standard `button` elements to enable complex layouts (text on left, price on right) but without carrying over semantics.
**Fix:**
1. Replaced `hidden` on checkboxes with `sr-only peer` and added `peer-focus-visible` styling to the visual `div` wrapper.
2. Added `role="radiogroup"`, `aria-labelledby`, `role="radio"`, and `aria-checked` attributes to the custom radio button groups.
3. Added `focus-visible:ring` to the custom buttons and range input. Added `aria-label` to the range input.
**Learning:** Always use `sr-only` coupled with `peer` for custom checkboxes/radios rather than `hidden` to preserve keyboard focus. When replacing native radios with buttons, explicitly wire up `role="radio"` and `aria-checked`.
**Watch for:** Other custom toggles, switches, or grouped select components across the codebase that might similarly drop native form semantics.
