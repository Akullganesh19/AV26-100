## 2024-05-24 — Accessible Custom Form Controls
**Found:** Simulated radio buttons using `<button>` elements and native checkboxes hidden via `display: none` (`className="hidden"`).
**Why it existed:** Developers often hide native inputs completely to apply custom styling, not realizing this removes them from the accessibility tree, breaking screen reader and keyboard access.
**Fix:** Replaced simulated radios with native `<input type="radio">` elements wrapped in `<label>`. Changed `hidden` to Tailwind's `sr-only peer` on native inputs, ensuring they are placed directly before the custom styling element. Used `peer-focus-visible` for keyboard focus states. Added `role="radiogroup"` and `aria-label` for context.
**Learning:** Never use `hidden` or `display: none` on interactive native elements. Use the `sr-only peer` pattern to maintain accessibility while allowing custom styling.
**Watch for:** Other custom-styled components (toggles, switches) that might be hiding the native input.
