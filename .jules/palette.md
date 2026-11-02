## 2024-11-02 - Collapsible Sidebar Accessibility
**Learning:** When text labels are hidden in collapsed sidebars (e.g., icon-only buttons/links), they lose accessibility context for screen readers and tooltips for sighted users.
**Action:** Add `aria-label` for screen readers and conditional `title` attributes when the text is visually hidden to maintain context and provide a native tooltip.
