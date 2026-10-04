## 2023-10-04 - Custom Radio Groups Accessibility
**Learning:** When implementing custom radio buttons with native elements like `<button>`, developers often forget semantic group roles (`radiogroup`) and state (`aria-checked`), making it difficult for screen reader users to understand the options context and current selection.
**Action:** Always wrap custom radio components in a `role="radiogroup"` element with an `aria-labelledby` linking to its descriptive heading, and ensure each option has `role="radio"` and `aria-checked` to communicate state accurately.
