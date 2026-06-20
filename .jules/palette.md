## $(date +%Y-%m-%d) — Custom Form Controls Accessibility Fixes

**Found:** Custom radio buttons, sliders, and toggle icons throughout `LoginPage.tsx` and `CalculatorSection.tsx` completely blocked keyboard navigation and screen readers. Specifically:
- Icon-only `<button>`s lacked `aria-label`.
- Checkboxes used `className="hidden"`, permanently removing them from the keyboard focus flow.
- Custom radio buttons lacked `role="radio"` and `aria-checked`.

**Why it existed:** Developers likely prioritized visual styling using Tailwind over semantic structure, opting to hide native inputs (`display: none`) and creating `div`/`button` proxies without wiring up the necessary ARIA attributes to bridge the gap.

**Fix:**
1. Associated all form inputs with explicit `<label htmlFor={id}>` connections.
2. Kept native inputs in the DOM for checkboxes but made them visually hidden using `sr-only peer`. Wired `peer-focus-visible` to their visual siblings to ensure keyboard navigation indicators exist.
3. Added `role="radiogroup"`, `role="radio"`, and `aria-checked` states to `<button>` elements masquerading as radio controls.
4. Added `aria-hidden="true"` to decorative Lucide icons.

**Learning:** When styling custom checkboxes or radios in this repository, never use `display: none` / `hidden`. Always use `sr-only` coupled with `peer` to preserve native focus management while allowing custom sibling styling.
**Watch for:** Other areas in the application utilizing custom toggle groups or checkboxes that might employ `className="hidden"` on the native input elements.
