## $(date +%Y-%m-%d) - Custom Radio Button Group Accessibility
**Learning:** Custom radio button groups built with `<button>` elements need ARIA roles (`role="radiogroup"` on parent, `role="radio"` on children) and states (`aria-checked`) to be properly recognized by screen readers.
**Action:** Always add semantic roles and state indicators to custom UI components that mimic native form controls.
