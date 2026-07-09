## 2025-07-09 — Accessibility Improvements: Form Labels and Async State Indicators
**Found:** Custom form components (`Input`, `Select`) lacked semantic connections between their `<label>` and `<input>`/`<select>` elements. Several buttons triggering async operations (like diagnosis tools, authentication, and alert acknowledgements) lacked `aria-busy` indicators. Additionally, decorative icons inside buttons and forms lacked `aria-hidden="true"`, and icon-only buttons lacked `aria-label`.
**Why it existed:** Rapid UI development often prioritizes visual layout over semantic accessibility. Custom wrapper components frequently overlook generating unique IDs for `htmlFor`/`id` linking, and visual loading spinners are added without their semantic ARIA equivalents.
**Fix:**
1. Updated `Input` and `Select` custom components in `DiagnosticsCenter.tsx` to use `React.useId()` to generate and link unique IDs using `id` and `htmlFor`.
2. Added `id` and `htmlFor` to form elements in `LoginPage.tsx`.
3. Added `aria-busy` attributes to async action buttons across `DiagnosticsCenter.tsx`, `LoginPage.tsx`, and `TacticalAlerts.tsx`.
4. Added `aria-hidden="true"` to decorative icons (especially those inside buttons and inputs).
5. Added `aria-label` to the icon-only password visibility toggle.
**Learning:** When building or modifying custom form field wrappers, always ensure that `id` and `htmlFor` properties are linked. This is a foundational accessibility requirement for screen readers. Similarly, any element displaying a visual loading state should simultaneously communicate that state via `aria-busy`.
**Watch for:** Other custom form components across the application that might be missing proper label associations, or new async buttons added without `aria-busy` and proper icon hiding.
