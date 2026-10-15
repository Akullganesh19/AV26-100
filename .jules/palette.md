## 2024-03-05 - Accessible Custom Checkboxes with Tailwind
**Learning:** When styling custom checkboxes, using className="hidden" on the input element completely removes it from the accessibility tree and prevents keyboard focus.
**Action:** Always use Tailwind's sr-only class to hide the actual input visually while keeping it accessible to screen readers and keyboard navigation. Then, use the peer class on the input and peer-focus-visible on the adjacent custom visual element to render a focus ring.
