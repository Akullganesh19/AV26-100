## 2024-10-27 — Accessible Checkboxes and Radio Groups
**Found:** Custom checkboxes were using `hidden` and custom radio buttons had no roles or focus states.
**Why it existed:** The native inputs were hidden for styling, breaking accessibility and focus tree entirely.
**Fix:** Changed `hidden` to `sr-only peer` for checkboxes to preserve focus and used `peer-focus-visible` for styling. Added `role="radiogroup"` and `role="radio"` for custom radio buttons along with `aria-checked`.
**Learning:** Using `display: none` (`hidden`) removes elements from the accessibility tree. Use `sr-only` to visually hide elements while keeping them accessible and focusable.
**Watch for:** Other custom styled inputs (checkboxes, radios, file uploads) using `hidden` instead of `sr-only`.
