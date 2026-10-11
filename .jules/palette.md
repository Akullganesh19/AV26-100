## 2024-10-11 - Missing ARIA labels on icon-only toggle buttons
**Learning:** Icon-only interactive elements lacking explicit ARIA labels and focus states decrease screen reader accessibility.
**Action:** Add `aria-label`, state attributes (like `aria-expanded` or `aria-pressed`), and explicit focus styles via `focus-visible:ring` to icon-only buttons.
