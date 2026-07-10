
## 2024-05-18 — Fix Custom Form Controls Accessibility in CalculatorSection
**Found:** Custom radio buttons ("Service Type", "Timeline") and custom checkboxes ("Add-ons") were inaccessible. The custom radio buttons used `<button>` without `role="radio"`, `aria-checked`, or a grouping `role="radiogroup"`. The custom checkboxes used `<input type="checkbox" className="hidden">` alongside a visual `div`. The custom slider input lacked an `aria-label`. None of the interactive elements had visible keyboard focus states.
**Why it existed:** Developers used raw Tailwind classes and custom `div`/`button` elements to achieve a specific visual design, likely bypassing native HTML form controls to avoid browser-default styling inconsistencies, without reimplementing the necessary ARIA attributes and focus management required for accessibility.
**Fix:**
- Added `aria-label` and `focus-visible:ring-*` to the slider `<input>`.
- Added `id` and `aria-labelledby` to headers, `role="radiogroup"` to the container, and `role="radio"`, `aria-checked`, and `focus-visible:ring-*` to the custom radio `<button>` elements.
- Replaced `className="hidden"` with `className="sr-only peer"` on the native checkboxes, moved them to be siblings before the custom visual `div`, and used `peer-focus-visible:ring-*` to style the custom `div` when the hidden native input receives focus.
- Added `aria-hidden="true"` to decorative icons within these controls.
**Learning:** When building custom interactive elements in React/Tailwind (especially checkboxes/radios), never use `display: none` (`hidden`) on the native input. Use `sr-only peer` on the native input and `peer-focus-visible` on the adjacent custom UI element to preserve keyboard focusability and screen reader support while maintaining custom designs. Always ensure custom widget groups have appropriate ARIA roles (`radiogroup`, `radio`) and state attributes (`aria-checked`).
**Watch for:** Other custom form components (e.g., custom select dropdowns, toggles) throughout the application that might be using `hidden` or generic `div`/`button` tags without proper ARIA roles and focus management.
