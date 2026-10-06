## 2024-10-06 - Accessible Custom Checkboxes Focus States
**Learning:** Custom checkboxes styled with a visual div and a hidden input using `display: none` (like `.hidden` in Tailwind) remove the element from the accessibility tree and prevent keyboard navigation and focus.
**Action:** Use `.sr-only.peer` on the `<input>` element placed immediately before the visual element, and apply `.peer-focus-visible` utilities to the adjacent visual element to explicitly render focus states when navigating by keyboard.
