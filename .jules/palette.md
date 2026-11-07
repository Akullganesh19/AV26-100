## 2024-11-08 - Accessible Collapsible Navigations
**Learning:** When text labels in sidebars or navigation items are hidden behind a toggle (like a hamburger menu), icon-only states become inaccessible if missing an explicit `aria-label` or `title` tooltip. The main layout has a collapsible sidebar where icon links and logout buttons lose their text when collapsed.
**Action:** Always conditionally add `aria-label` and `title` to interactive elements when their visible text component can be hidden by UI state, to ensure screen readers and mouse users both receive context.
