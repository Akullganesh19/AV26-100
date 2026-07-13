
## 2026-07-13 — [Form Accessibility Improvements]
**Found:** Missing `id` to `htmlFor` bindings, `aria-busy` missing on submit buttons, `aria-hidden` missing on inline icons, and checkboxes using `display: none` (`hidden`).
**Why it existed:** Quick scaffolding of components without taking full keyboard/screen reader UX into consideration. Forms were built rapidly with visual focus over semantic focus.
**Fix:** Connected labels using `useId`, added `aria-busy` states to async buttons, added `aria-hidden="true"` to decorative icons, and replaced `hidden` with `sr-only peer` coupled with `peer-focus-visible` for custom checkboxes.
**Learning:** Always preserve focusability on visually hidden native inputs (`sr-only`) and provide visible focus rings.
**Watch for:** Other custom elements using `hidden` instead of `sr-only`.
