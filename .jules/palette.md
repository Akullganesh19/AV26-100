## 2024-05-14 - Accessible Custom Form Controls
**Learning:** Hidden inputs (`className="hidden"`) drop out of the accessibility tree entirely, blocking screen readers and keyboard focus for custom interactive elements.
**Action:** Use `className="sr-only peer"` alongside `peer-focus-visible` to build custom checkboxes and radio buttons that remain perfectly accessible and keyboard-friendly while hiding the native input visually.
