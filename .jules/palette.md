## 2024-05-30 — Accessible Forms and Icon Buttons
**Found:** Missing `htmlFor` on labels, missing `aria-label` on icon-only buttons, and missing disabled visual states on form submission buttons.
**Why it existed:** Quick scaffolding of custom UI components (`Input`, `Select`) and icon buttons without incorporating complete accessibility attributes.
**Fix:** Added `React.useId()` to dynamically link `<label>` and `<input>`, added `aria-label` to sidebar and password visibility toggles, and added `disabled:opacity-50 disabled:cursor-not-allowed aria-busy` to submit buttons.
**Learning:** Custom UI wrappers often miss basic HTML associations. Always ensure inputs have associated labels for screen readers.
**Watch for:** Other custom input components or naked Lucide icons inside buttons without `aria-label`.
