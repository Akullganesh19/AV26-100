## 2026-11-01 - Keyboard Accessible Custom Checkboxes
**Learning:** Using 'hidden' on native inputs for custom checkboxes breaks keyboard focus. The native input must remain in the accessibility tree.
**Action:** Always use 'sr-only peer' on the native input placed right before the custom visual element to apply 'peer-focus-visible' styles and ensure keyboard navigation works.
