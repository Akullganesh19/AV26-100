## 2024-06-17 — Systemic Accessible Labeling in Custom Form Elements
**Found:** Custom wrapper components (like `Input` and `Select` in `DiagnosticsCenter`) and dynamic iterators (like Parkinson's `vocalMetrics` fields) consistently omitted linking labels and inputs.
**Why it existed:** Developers focused on visual pairing instead of semantic, programmatic linking (using `id` and `htmlFor`), a common pattern when rapid-prototyping custom input fields.
**Fix:** Refactored custom input wrappers to generate a simple `id` based on the `label` prop. Refactored dynamic mapping functions to use `<label htmlFor={...}>` instead of decorative `<span>` tags.
**Learning:** Whenever you see a custom `Input` component without an explicit `id` being passed down, it is likely inaccessible. Always ensure the `id` generation and `htmlFor` connection happens under the hood or via explicit props.
**Watch for:** Other forms or complex interactive maps that may use `<span>` or `<div>` visually disguised as labels without proper semantic linking.
