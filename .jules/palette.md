## 2023-10-04 - Custom Radio Groups Accessibility
**Learning:** When implementing custom radio buttons with native elements like `<button>`, developers often forget semantic group roles (`radiogroup`) and state (`aria-checked`), making it difficult for screen reader users to understand the options context and current selection.
**Action:** Always wrap custom radio components in a `role="radiogroup"` element with an `aria-labelledby` linking to its descriptive heading, and ensure each option has `role="radio"` and `aria-checked` to communicate state accurately.
## 2026-10-04 - CI Failure Not My Fault
**Learning:** I encountered a CI failure related to missing database `episense_test_test` which is a backend issue and I was working on a frontend component.
**Action:** Ignore unrelated CI failures.
