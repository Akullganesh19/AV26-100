## 2024-10-03 - Custom Radio Group Accessibility
**Learning:** Custom radio groups built with buttons lack semantic meaning for screen readers, preventing users from understanding their role and selection state.
**Action:** Always add `role="radiogroup"` with an `aria-label` to the container, and `role="radio"` with `aria-checked` to the individual buttons.
## 2024-10-03 - Custom Radio Group Keyboard Accessibility
**Learning:** Adding ARIA roles (`role="radio"`) to non-interactive elements without adding `tabIndex` and keyboard event handlers (`onKeyDown` for Space/Enter) creates a broken experience for assistive tech users.
**Action:** Always ensure that custom interactive elements receive focus (`tabIndex={0}`), have visible focus states (`focus-visible:ring`), and can be triggered via keyboard.
