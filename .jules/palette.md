## 2026-10-02 - Added ARIA Roles to Custom Radio Groups
**Learning:** Custom UI radio group selections (like buttons behaving as radios) are not accessible to screen readers by default. They require `role="radiogroup"` on the container and `role="radio"` on each button with a dynamic `aria-checked` state reflecting selection.
**Action:** Always add `role="radiogroup"` and `aria-labelledby` on the parent container and `role="radio"`, `aria-checked` on the options for custom radio button-like structures.
