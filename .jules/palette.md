## 2026-10-27 - Custom Checkbox A11y Pattern
**Learning:** Tailwind's 'peer' utility requires the native input (using sr-only) to appear before the custom visual element in the DOM order to correctly apply focus styles via CSS sibling combinators.
**Action:** Always place native inputs first when building accessible custom form controls with Tailwind peer classes.
