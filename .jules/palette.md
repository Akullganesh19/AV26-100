## 2024-10-05 - Custom Form Controls Keyboard Navigation
**Learning:** Using `hidden` on a native `<input type="checkbox">` completely removes it from keyboard focus. Custom radio buttons built with `<button>` elements need explicit `role="radiogroup"` on their parent container and `role="radio"` with `aria-checked` on the options.
**Action:** Always use `.sr-only peer` pattern for styled native checkboxes to preserve keyboard focus, and manually apply radiogroup ARIA patterns to group custom radio buttons.
