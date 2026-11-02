## 2024-05-24 — [Accessible Interactive Controls]
**Found:** Simulated radio buttons (`<button>`) and hidden checkboxes (`<input className="hidden">`) that lacked keyboard accessibility and screen reader support.
**Why it existed:** Developers often hide native inputs completely to apply custom styling, breaking accessibility.
**Fix:** Converted simulated controls to native inputs wrapped in `<label>`. Used Tailwind's `sr-only peer` class on the input and `peer-focus-visible` on the adjacent custom styling element.
**Learning:** When styling interactive elements, never use `display: none` or `hidden` on the native input. Use the visually-hidden `sr-only peer` pattern to maintain accessibility while allowing custom styles on sibling elements.
**Watch for:** Other forms or custom selection components using `div` or `button` elements as simulated inputs without ARIA roles.
