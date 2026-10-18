## 2025-01-20 — Form Labels and Icon Accessibility Sweep
**Found:** Widespread lack of programmatic form labels, aria-labels for icon-only buttons, and loading states missing screen-reader accessible text.
**Why it existed:** Components were likely built primarily for visual feedback (relying on placeholders, nearby text, or loading spinners) without applying `htmlFor`/`id` linking or `aria-label`/`aria-hidden` attributes for assistive technologies.
**Fix:** Added explicit `htmlFor` and `id` linking to all form fields in `LoginPage.tsx` and dynamically generated IDs using `React.useId()` in `DiagnosticsCenter.tsx` components. Added `aria-label` to icon-only buttons (like the menu and password toggles) and explicitly hid visual icons with `aria-hidden="true"`.
**Learning:** The application's UI components are heavily reliant on visual styling and layout for context. Future work must always ensure interactive elements are fully described to screen readers.
**Watch for:** Other forms or new custom form components (like `Input` or `Select`) missing `id` and `htmlFor` properties. Any button with only an icon should have a clear `aria-label`.
