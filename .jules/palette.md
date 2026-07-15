## 2026-07-15 — [Reusable Component Accessibility]
**Found:** Missing `id` and `htmlFor` props on dynamic form components (`Input`, `Select`). Missing explicit `aria-hidden` and `aria-label` properties on icon-only buttons.
**Why it existed:** Abstracting components over-optimizes for visual structure and often drops boilerplate a11y properties if not explicitly forced, particularly when standard HTML bindings rely on unique IDs.
**Fix:** Modified `Input` and `Select` components to utilize React's `useId()` hook to guarantee that all dynamically rendered form elements remain correctly linked for screen readers. Added `aria-label`, `aria-hidden="true"`, and `aria-busy={loading}` for relevant interactive components.
**Learning:** Whenever building custom interactive elements or wrappers, immediately integrate `useId()` for labeling and manage ARIA states (like `aria-busy` or `aria-label`) dynamically to maintain core a11y out-of-the-box.
**Watch for:** Other form components nested inside specialized feature layers, and `onClick` handlers attached directly to `div`s instead of native `button` elements, requiring manual focus management.
