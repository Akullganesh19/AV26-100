# Palette's Journal

## 2025-05-14 - [Improve calculator accessibility and keyboard navigation]
**Learning:** Many custom UI components (like sliders, checkboxes, and radio button groups) are often implemented using non-semantic elements or by hiding native inputs, which makes them inaccessible to screen readers and keyboard users. Using `sr-only` instead of `hidden` and adding ARIA roles/states is crucial for accessibility.
**Action:** Always check custom form elements for keyboard focusability and ARIA roles. Use `sr-only` for native inputs that need to stay accessible.
