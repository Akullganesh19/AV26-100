## 2024-03-20 — Form Field Accessibility Wrappers
**Found:** Custom form wrappers (`Input`, `Select`) in `DiagnosticsCenter.tsx` lacked proper ID bindings between `<label>` and their corresponding inputs, breaking screen reader association.
**Why it existed:** The components relied on generic props but didn't generate unique IDs internally, making it impossible to correctly link the label to the input field using `htmlFor`.
**Fix:** Introduced React's `useId()` hook within the `Input` and `Select` components to automatically generate unique IDs and bind them to the `<label htmlFor={id}>` and `<input id={id}>`.
**Learning:** Always use `useId()` when building custom interactive wrapper components in React to ensure accessible label association without risking ID collisions across multiple instances on the same page.
**Watch for:** Other custom form controls or nested interactive elements across the application that might be missing explicit ID linking.
