## 2026-08-25 — Form Accessibility & Screen Reader Support
**Found:** Form inputs across Login and Diagnostics lacked `id`/`htmlFor` bindings, and icon-only buttons (like password toggle) lacked `aria-label`s.
**Why it existed:** Custom wrapper components (`Input`, `Select`) and raw HTML forms were built rapidly without considering the accessibility tree mapping.
**Fix:** Added explicit `htmlFor`/`id` linking to all inputs using `React.useId()` for uniqueness, added screen-reader labels to icon buttons, and converted visual labels (spans) to semantic `<label>` elements for dynamic arrays.
**Learning:** Always use `React.useId()` to generate `id`s for custom form components so labels can programmatically link to inputs without risking duplicate IDs or runtime crashes from string manipulation. Use `aria-label` on any button that only contains an icon.
**Watch for:** Other custom input wrappers or map overlay controls that might be missing semantic labeling.
