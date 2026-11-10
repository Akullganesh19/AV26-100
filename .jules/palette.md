## 2025-02-14 — Accessible Custom Inputs Pattern

**Found:** Simulated radio buttons using `<button>` elements and checkboxes using `display: none` (`hidden`) on native `<input>` elements in `CalculatorSection.tsx`.
**Why it existed:** The developer wanted complete control over the visual styling of the radio/checkbox elements and likely found default inputs difficult to style, resorting to hiding them or omitting them entirely.
**Fix:** Converted simulated `<button>` elements to native `<input type="radio">` wrapped in `<label>`. Replaced `hidden` class with Tailwind's `sr-only peer` pattern, placing the input directly before the custom styling element, and utilized `peer-focus-visible` to restore keyboard focus states.
**Learning:** Never use `hidden` or `display: none` on native interactive elements as it removes them from the accessibility tree. Always use native inputs (`radio`, `checkbox`) to preserve built-in keyboard navigation and screen reader semantics.
**Watch for:** Other areas in the application where custom UI components might be hiding underlying native inputs or relying entirely on divs/buttons for state toggles.