## 2024-03-24 - Interactive Element Focus Indicators
**Learning:** Custom styled interactive elements (like generic buttons for options or custom checkboxes) often completely miss focus indicators, making them invisible to keyboard-only users navigating the component.
**Action:** Always add explicit focus-visible utility classes (e.g., `focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2`) and proper ARIA states (like `aria-pressed`) to interactive elements, ensuring keyboard accessibility parity with mouse interactions.
