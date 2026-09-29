## 2024-10-24 - Accessible Custom Radio Groups
**Learning:** When implementing custom radio button groups using non-input elements (e.g., `<button>`), they lack semantic meaning and keyboard interaction semantics for screen readers.
**Action:** Always add `role="radiogroup"` to the parent container, and `role="radio"` with the appropriate `aria-checked` state to each distinct option to ensure accessibility.
