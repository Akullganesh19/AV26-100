## 2025-02-23 - Custom Checkbox Accessibility
**Learning:** When styling custom checkboxes with Tailwind, using className="hidden" removes the element from the accessibility tree, breaking keyboard navigation. Tailwind's peer classes rely on DOM order.
**Action:** Always use className="sr-only peer" on the input, place it before the custom visual element in the DOM, and use peer-focus-visible classes to style the visual focus state.
