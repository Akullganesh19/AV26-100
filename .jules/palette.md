
## 2026-09-30 - Accessible Custom Radio Buttons
**Learning:** When creating custom radio buttons using non-input elements like <button>, screen readers require explicit ARIA roles to understand the grouping and selection state.
**Action:** Always add role="radiogroup" to the parent container and role="radio" with aria-checked state to each distinct option button.
