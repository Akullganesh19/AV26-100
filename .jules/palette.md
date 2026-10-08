## 2026-10-08 - Added accessible icon-only button states
**Learning:** Icon-only navigation toggles in the layout lack ARIA labels and explicit focus indicators, which makes them inaccessible to screen readers and keyboard users.
**Action:** Always provide an `aria-label`, `aria-expanded` (if it toggles a section), and `.focus-visible:ring-2` on icon-only buttons to preserve accessibility and keyboard navigability.
