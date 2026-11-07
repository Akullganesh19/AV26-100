## 2024-05-18 — Accessible Custom Controls
**Found:** Custom radio buttons and checkboxes (e.g., in CalculatorSection) missing native keyboard focus visibility and screen reader operability because native inputs were hidden with `display: none` or omitted entirely.
**Why it existed:** Visually-driven development where `div`s and `<button>`s were used to emulate form controls without associating underlying native inputs properly.
**Fix:** Converted interactive custom controls to use native `<input type="radio">` and `<input type="checkbox">` with Tailwind's `sr-only peer` pattern. Placed the native input immediately preceding the custom `div` styling element, adding `peer-focus-visible:ring-2` to the custom element to provide keyboard accessibility.
**Learning:** Do not use `hidden` or `display: none` on native inputs for custom styled interactive components, as it removes them from the accessibility tree. Use `sr-only peer` to hide visually while retaining function.
**Watch for:** Other areas in the application where simulated radio buttons built with `<button>` or `<div>` elements exist, replacing them with the native `sr-only peer` pattern.
