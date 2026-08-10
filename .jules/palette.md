## 2024-08-10 — Custom Checkbox Accessibility and Focus States
**Found:** Custom checkboxes and pseudo radio buttons lacked keyboard navigation and focus visibility due to `className="hidden"` on the underlying `<input>`.
**Why it existed:** Developers often hide the default input to style a custom element, but this removes it from the accessibility tree, making it invisible to screen readers and breaking keyboard navigation. Pseudo radios missed focus rings.
**Fix:** Changed `hidden` to `sr-only peer` on the input, placed it before the visual element, and added `peer-focus-visible:ring-2`. Added `role="radio"`, `aria-checked`, and `focus-visible` styles to pseudo radio buttons.
**Learning:** Never use `hidden` or `display: none` on interactive elements you intend to replace visually. Use `sr-only` and `peer` to style custom interactive elements.
**Watch for:** Other forms or components where custom UI is built by hiding the native semantic element completely.
