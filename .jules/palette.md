## 2024-10-14 - Checkbox focus states
**Learning:** When styling custom native checkboxes in Tailwind, use `.sr-only.peer` on the `<input>` element (placed before the custom visual element) instead of `.hidden` to preserve keyboard focusability within the accessibility tree, and apply `.peer-focus-visible` utilities to the adjacent visual element to render explicit focus states.
**Action:** Remember to use `.sr-only.peer` instead of `.hidden` for accessibility of checkboxes.
