## 2026-10-23 - Accessible Custom Checkboxes with Tailwind
**Learning:** Never use `hidden` on native inputs for custom checkboxes, as it removes them from the a11y tree. The input must precede the visual element in DOM order for Tailwind's `peer` class to target it using general sibling combinators.
**Action:** Use `sr-only peer` on the native input, place it before the custom visual `div`, and apply `peer-focus-visible:ring-2 peer-focus-visible:ring-[theme-color]` to the visual `div` for proper keyboard accessibility.
