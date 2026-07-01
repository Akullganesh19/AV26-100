## 2024-05-24 — Accessible Form Controls for Custom UIs
**Found:** Custom checkboxes and radio buttons in `CalculatorSection.tsx` broke keyboard navigation and screen reader support because native inputs were hidden using `display: none` (`hidden` class).
**Why it existed:** The developer wanted to use custom visual indicators for checkboxes and radios without styling the native inputs, unaware that `hidden` removes the element from the focus order and accessibility tree.
**Fix:** Removed `hidden` and replaced with `.sr-only peer`. Kept the native input in the DOM (visually hidden but focusable) and added `peer-focus-visible` styles to the adjacent custom UI element to correctly render a focus ring. Used `aria-label` where necessary and proper grouping.
**Learning:** When building custom interactive elements, never use `hidden` on native form inputs. Always use `.sr-only` coupled with the `peer` pattern in Tailwind to maintain accessibility while allowing visual customization.
**Watch for:** Other custom forms or toggles that might have used `className="hidden"` to hide native checkboxes or radio buttons across the codebase.
