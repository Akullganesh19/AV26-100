## 2024-05-18 — Form Field Accessibility Enhancements
**Found:** Custom Input and Select form components in `DiagnosticsCenter.tsx` lack semantic association between `<label>` and `<input>`/`<select>`. Inputs also lack basic ARIA attributes for screen readers.
**Why it existed:** Reusable components were built quickly without generating unique IDs for the `id` and `htmlFor` attributes, severing the programmatic connection between label text and the input field.
**Fix:** Added `React.useId()` to generate unique IDs for each field and bound `<label htmlFor={id}>` to `<input id={id}>` and `<select id={id}>`.
**Learning:** Always use `React.useId()` when creating reusable form field components in React to guarantee accessible label bindings without requiring consumers to manually pass IDs.
**Watch for:** Other custom input wrappers across the application that might be missing `id`/`htmlFor` pairings or proper ARIA roles.

## 2024-05-18 — LoginPage and IconButton Accessibility Fixes
**Found:** Login inputs missing IDs and label-to-input association. Icon buttons in `LoginPage` and `MainLayout` missing `aria-label` attributes. Missing form field associations in `DiagnosticsCenter`.
**Why it existed:** Inputs lacked IDs for explicit linkage. Icon-only buttons used icons without screen reader text.
**Fix:** Added `id` and `htmlFor` pairings in `LoginPage`, and added `aria-label` to icon-only buttons like the password toggle and menu buttons.
**Learning:** Always verify icon-only buttons have descriptive `aria-label` properties. Ensure label-to-input linkage in every form.
**Watch for:** Other standalone icons wrapping interactables.
