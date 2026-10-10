## 2026-10-10 - Custom Checkbox Keyboard Focus Accessibility
**Learning:** Using `hidden` on custom native checkboxes removes them from the accessibility tree, making them un-focusable via keyboard.
**Action:** Use `.sr-only.peer` on the `<input>` element (placed before the custom visual element) and apply `.peer-focus-visible` utilities to the adjacent visual element to render explicit focus states.
