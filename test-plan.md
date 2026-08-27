1. **Fix ARIA labeling on slider**:
   Add `aria-label` attribute to the `input[type="range"]` in `frontend/src/components/CalculatorSection.tsx` to make it accessible to screen readers, per memory guidance.
   Also add focus styles to the slider input.
   - Use `replace_with_git_merge_diff` with blocks.
2. **Fix accessible semantic on pseudo-radio buttons (Service Type & Timeline)**:
   Add `role="radiogroup"` to the container, and `role="radio"`, `aria-checked`, and focus styles to the pseudo-radio button elements in `CalculatorSection.tsx` so they are keyboard accessible and semantically correct.
   - Use `replace_with_git_merge_diff`.
3. **Fix accessible checkboxes (Add-ons)**:
   Change `className="hidden"` on the custom checkboxes in `CalculatorSection.tsx` to `className="sr-only peer"`, move the input *before* the custom styling div, and add `peer-focus-visible:ring-2` to the visual div to ensure keyboard navigation visibility, per memory guidance.
   - Use `replace_with_git_merge_diff`.
4. **Verify changes**:
   Run `cd frontend && pnpm run build` to verify syntax and ensure no breaking regressions were introduced.
5. **Complete pre-commit steps**:
   Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
6. **Submit PR**:
   Create a PR with Palette-specific title and body format.
