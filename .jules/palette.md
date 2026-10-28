## 2024-10-28 — Accessible Custom Inputs
**Found:** Custom checkboxes in `CalculatorSection` used `className="hidden"` on the native input, removing them from the accessibility tree.
**Why it existed:** Developers often hide native inputs completely when building custom-styled alternatives, forgetting that `hidden` or `display: none` destroys keyboard and screen reader access.
**Fix:** Replaced `className="hidden"` with Tailwind's `sr-only peer` on the native input, and added `peer-focus-visible:ring-2` to the custom styling container to restore visual focus indicators.
**Learning:** Never use `hidden` on native form elements backing custom components. Always use `sr-only` paired with `peer` to maintain both semantics and style.
**Watch for:** Other custom checkboxes, radio buttons, or file inputs across the application that might be hiding the native element.
