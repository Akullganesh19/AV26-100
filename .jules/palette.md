## 2024-05-18 — Accessibility improvements for form hygiene
**Found:** Missing `id` / `htmlFor` label bindings, `aria-describedby` mappings for error states, and unlabelled icon buttons across `LoginPage` and `DiagnosticsCenter`.
**Why it existed:** The forms were built purely visually. Custom `<Input>` and `<Select>` components didn't generate internal unique IDs, preventing label association. Error messages were rendered conditionally but not linked to the inputs for screen reader announcement.
**Fix:**
- Used React's `useId()` hook to auto-generate unique IDs in reusable `<Input>` and `<Select>` functional components.
- Added explicit `htmlFor` and `id` bindings to custom forms (`LoginPage`, Parkinson's array).
- Wired `aria-invalid` and `aria-describedby` to the error states.
- Added `aria-label` to the password visibility icon toggle.
- Added `aria-busy` to submit buttons during loading state.
**Learning:** This codebase uses custom input abstractions and static arrays for form generation without native React `useId()`. Future additions using these abstractions should inject or generate proper IDs automatically.
**Watch for:** Other custom input components (like date pickers or metric tables) that might lack semantic label association.
