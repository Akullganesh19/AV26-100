## 2024-08-14 — Custom Checkbox and Radio Button Accessibility
**Found:** Custom checkboxes using `className="hidden"` on `<input>` break keyboard navigation. Custom radio buttons using `<button>` lack semantics and focus states.
**Why it existed:** Developers often hide the native input visually, accidentally removing it from the accessibility tree, and use basic buttons for radio groups without adding ARIA attributes.
**Fix:** Used `sr-only peer` on `<input>` and `peer-focus-visible:ring-2` on the custom visual checkbox element. Added `role="radio"`, `aria-checked`, and `focus-visible:ring-2` to custom radio buttons.
**Learning:** Never use `hidden` or `display: none` on inputs that power custom visual controls. Use Tailwind's `peer` utilities to style adjacent visual elements based on the invisible native input's state, preserving accessibility.
**Watch for:** Other custom UI controls in the app that might be hiding native elements or missing focus states and semantics.
