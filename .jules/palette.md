## 2026-10-28 - Custom Form Control Keyboard Accessibility
**Learning:** When building custom checkboxes or radio buttons, using `hidden` on native inputs breaks keyboard focus. Must use `sr-only peer` on the native input placed *before* the custom visual element in DOM order to allow `peer-focus-visible` styling via CSS sibling combinators.
**Action:** Always ensure custom interactive elements maintain native keyboard focus patterns and visible focus indicators using Tailwind's `focus-visible` and `peer` utilities.
