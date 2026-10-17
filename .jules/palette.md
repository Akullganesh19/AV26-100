## 2025-02-28 - Custom Checkbox Accessibility
**Learning:** Using `className="hidden"` on native `<input type="checkbox">` elements for custom styling removes them from the accessibility tree, making them unfocusable and invisible to screen readers.
**Action:** Always use `className="sr-only peer"` on the native input instead, and apply `peer-focus-visible` classes (like `peer-focus-visible:ring-2 peer-focus-visible:ring-brand-primary`) to the adjacent visual element to ensure keyboard focus visibility while maintaining custom styles.
