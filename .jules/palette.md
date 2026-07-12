## 2024-05-18 — Accessible Custom Form Elements

**Found:** Custom UI components (like styled checkboxes, radios, and sliders) were inaccessible to keyboard and screen reader users. Native inputs were hidden using `display: none` (`hidden`), labels lacked `htmlFor` attributes, and dynamic inputs lacked generated `id`s.

**Why it existed:** Developers often hide native inputs completely and rely purely on React state to drive custom UI visuals, prioritizing aesthetics over semantic HTML structure and keyboard focus management.

**Fix:**
- Used React's `useId()` in dynamic helper components (`Input`, `Select`) to bind `<label htmlFor>` to `<input id>`.
- Replaced Tailwind's `hidden` with `sr-only peer` on native custom checkbox inputs. This visually hides the input but keeps it focusable. Applied `peer-focus-visible` to the adjacent custom visual elements.
- Added appropriate ARIA roles (`role="radiogroup"`, `role="radio"`) and `aria-checked` states to buttons acting as custom radio inputs.
- Ensure all interactive elements have explicit `focus-visible` styles and `aria-label`s when lacking visible text.

**Learning:** When building custom interactive elements, **never** use `display: none` on the native semantic inputs. Use `sr-only peer` to preserve accessibility tree presence and keyboard focusability while styling the "peer" element to reflect state changes.

**Watch for:** Other areas where `className="hidden"` is used on inputs, or where generic `<div>` or `<button>` elements are used as form controls without proper ARIA roles and keyboard event handlers.