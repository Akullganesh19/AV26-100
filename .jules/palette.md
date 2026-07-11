## 2026-07-11 — Accessible Custom Checkboxes

**Found:** Custom UI checkboxes used `display: none` (`className="hidden"`) on the underlying native `<input type="checkbox">` elements, which completely removes them from the accessibility tree and prevents keyboard users from focusing or interacting with them.

**Why it existed:** The native checkbox was hidden to allow building a fully custom visual replacement using React state (`addon.state`) and an adjacent icon div.

**Fix:** Replaced `className="hidden"` with `className="sr-only peer"` on the input, and moved the input to be the first element in the DOM relative to the custom visual container. Used Tailwind's `peer-focus-visible` utility (`peer-focus-visible:ring-2`, etc.) on the custom container to render focus rings natively when the sr-only input receives focus.

**Learning:** When building custom interactive elements like custom checkboxes or radio buttons, never use `hidden`. Use `sr-only` to visually hide but keep it accessible for focus and screen readers. Leverage the `peer` class in Tailwind to style adjacent sibling elements based on the native input's state (focus, checked, etc.).

**Watch for:** Custom toggle switches, radio buttons, or checkboxes that lack keyboard navigability.
