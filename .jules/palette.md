## 2026-10-29 - Enhanced Focus Visibility in Calculator
**Learning:** Tailwind's peer classes for focus visibility require proper HTML semantics. Hidden inputs cannot receive focus, so screen readers and keyboard users cannot interact with them properly.
**Action:** Use sr-only and peer for inputs inside labels, placing them immediately before the visual elements for styling with peer-focus-visible.
