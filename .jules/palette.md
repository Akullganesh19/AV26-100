## 2024-10-23 - Custom Checkbox Accessibility
**Learning:** Using `className="hidden"` on native inputs for custom checkboxes removes them from the accessibility tree, breaking keyboard navigation. Tailwind's `peer` utilities require the hidden input to precede the visual element in the DOM.
**Action:** Use `className="sr-only peer"` on the native input, place it before the custom visual element, and use `peer-focus-visible` classes on the visual element for focus states.
