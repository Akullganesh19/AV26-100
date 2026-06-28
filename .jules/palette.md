## 2024-08-09 — Fixed Accessibility of Calculator Radios and Checkboxes
**Found:** Custom radio buttons (Service Type, Timeline) and checkboxes (Add-ons) used `hidden` native inputs or plain `button`s without native associations, lacking keyboard focus rings (`focus-visible`). Slider lacked aria labeling.
**Why it existed:** Developers often try to hide native inputs completely using `hidden` or `display: none` to build custom UI, forgetting that this removes the element from keyboard navigation sequences entirely.
**Fix:** Changed `hidden` elements to `sr-only peer`. Used `peer-focus-visible` to render focus rings on custom interactive components. Added `aria-label` to slider.
**Learning:** This codebase uses standard Tailwind custom control patterns; to maintain keyboard a11y, always use `sr-only` coupled with the `peer` class on the native input, and trigger focus styles on the sibling custom component via `peer-focus-visible`.
**Watch for:** Other custom form controls or toggle buttons across the frontend that may use `hidden` instead of `sr-only`.
