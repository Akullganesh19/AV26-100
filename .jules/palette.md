## 2024-05-27 - Accessible Collapsible Sidebars
**Learning:** When text labels for buttons or links are visually hidden in collapsible sidebars, screen readers and sighted users lose context.
**Action:** Add an `aria-label` for screen readers and a conditional `title` attribute to provide a native tooltip for sighted users relying on icons when the sidebar is collapsed.
