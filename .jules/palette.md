## 2026-08-26 — Accessible Custom UI Components
**Found:** Custom UI sliders, radio buttons, and checkboxes built with `<div>` or `<button>` elements were completely inaccessible to keyboard users and lacked semantic ARIA attributes for screen readers. Furthermore, reusable form elements lacked ID linkage to their labels.
**Why it existed:** Developers prioritized the visual aesthetic of custom components (like pseudo-checkboxes and custom buttons acting as radios) without wiring up the underlying semantic HTML or accessibility primitives.
**Fix:** Added `role="radiogroup"`, `role="radio"`, and `aria-checked` to custom radio buttons. Replaced `hidden` checkboxes with `.sr-only` inputs coupled with Tailwind `.peer` classes to maintain focus rings natively. Added dynamic `React.useId()` linkage between form labels and inputs.
**Learning:** Always check how custom "click-to-toggle" components behave when tabbing. If a `<button>` behaves like a radio, it needs ARIA roles. If a custom checkbox is used, visually hide the native input but keep it in the accessibility tree to manage focus automatically.
**Watch for:** Other areas in the application where custom tabs, toggles, or list items might be missing proper keyboard event handling or ARIA roles.
## 2026-08-26 — Database Test URL Generation
**Found:** Backend tests failed on CI due to `InvalidCatalogNameError: database "episense_test_test" does not exist`.
**Why it existed:** The `conftest.py` script naively appended `_test` to `DATABASE_URL` (i.e. `str(settings.DATABASE_URL) + "_test"`) without checking if the URL was already suffixed. On CI, the environment variables natively set `DATABASE_URL=.../episense_test`, which resulted in the invalid database string `episense_test_test`.
**Fix:** Modified `conftest.py` to conditionally append `_test` only if the database URL does not already end with `_test`.
**Learning:** Always validate state before augmenting test resources. Naive string concatenations break CI configurations that already provide pre-isolated environments.
**Watch for:** Other areas in the testing configuration where environment variables are overridden locally without checking their initial CI state.
