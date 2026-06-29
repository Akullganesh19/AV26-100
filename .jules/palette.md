## 2025-05-18 — Custom Form Control Accessibility
**Found:** Custom radio buttons and checkboxes were using `display: none` (`className="hidden"`) or `<button>` elements instead of native radio/checkbox inputs with visual overlays.
**Why it existed:** The original implementation prioritized visual styling and used simple click handlers mapped to state, bypassing native form mechanics.
**Fix:** Wrapped the visual elements and a native `<input>` inside a `<label>`. Used `className="sr-only peer"` on the input to keep it visually hidden but focusable by keyboard, and added `peer-focus-visible:ring-2` to the visual element. Also added `role="radiogroup"` and `role="group"` with `aria-labelledby` to associate groups of options with their descriptive headings.
**Learning:** Always use `sr-only peer` instead of `hidden` when styling custom form controls in Tailwind to preserve keyboard focusability. Form groupings need explicit ARIA labelling since visual proximity isn't parsed by screen readers.
**Watch for:** Other custom interactive components (like toggles or custom selects) that might be using `div` or `button` elements instead of native semantic inputs or missing proper ARIA roles.
