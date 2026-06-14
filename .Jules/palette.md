# Palette's Journal

## 2025-05-14 - [Improve calculator accessibility and keyboard navigation]
**Learning:** Custom UI components must use semantic ARIA roles and states (e.g., `radiogroup`, `radio`, `aria-checked`) to be accessible. Replaying `hidden` with `sr-only` is essential for keeping interactive elements in the tab order and accessibility tree while maintaining custom visuals. Focus rings are critical for keyboard navigation.
**Action:** Always verify custom form elements for keyboard accessibility. Use `sr-only` for native inputs and ensure focus visibility.
