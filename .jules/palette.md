## 2024-11-12 - Conditional ARIA Labels for Collapsible UI Elements
**Learning:** When text labels for buttons or links are conditionally hidden (like in a collapsible sidebar), using a static `aria-label` creates WCAG 2.5.3 (Label in Name) violations when the text *is* visible, and redundant announcements for screen readers. Sighted users relying on icons also miss context when text is hidden.
**Action:** Apply `aria-label` conditionally (e.g. `aria-label={!isOpen ? 'Label' : undefined}`) rather than statically. Include a conditional `title` attribute for native tooltips.
