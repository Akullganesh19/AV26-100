## 2024-05-20 — Systemic Form & Icon Accessibility Sweep
**Found:** Unassociated form labels in reusable input components (`DiagnosticsCenter`), missing ARIA labels on icon-only buttons (`MainLayout`, `LoginPage`), and lack of ID association on static form pages (`LoginPage`).
**Why it existed:** Reusable components passed string props to labels but didn't generate unique IDs. Icon buttons lacked screen reader context in a UI prioritizing visual real estate.
**Fix:** Introduced `React.useId()` in `DiagnosticsCenter`'s `Input` and `Select`. Added `htmlFor` and explicit `id` attributes in `LoginPage`. Added descriptive `aria-label`s to the sidebar toggle and password visibility toggle. Added `focus-visible` styling for keyboard navigation feedback.
**Learning:** Reusable form components must encapsulate unique ID generation rather than relying on parents. Ensure all icon-only buttons are explicitly labeled for screen readers.
**Watch for:** Other custom input components created in the future missing `React.useId()` or explicit ID tracking.
