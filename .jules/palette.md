## 2024-10-21 - Accessible Custom Checkboxes
**Learning:** Custom checkboxes styled with Tailwind using hidden on the native input remove the element from the accessibility tree, breaking screen readers and keyboard navigation.
**Action:** Use sr-only peer instead of hidden, place the input before the custom visual element in the DOM, and apply peer-focus-visible classes to ensure focus visibility.
