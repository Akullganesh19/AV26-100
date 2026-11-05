## 2024-11-05 - Accessible Collapsible Sidebars
**Learning:** When text labels for buttons or links are visually hidden (e.g., in collapsible sidebars), they become completely inaccessible to screen readers and lack visual context for sighted users relying on icons.
**Action:** Always include an `aria-label` for screen readers and a conditional `title` attribute to provide a native tooltip for sighted users when elements are visually collapsed.
