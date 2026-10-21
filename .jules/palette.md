## 2023-10-21 - Fix custom checkbox accessibility
**Learning:** Using className="hidden" on native <input> elements removes them from the accessibility tree, making custom visual checkboxes inaccessible.
**Action:** Use className="sr-only peer" on the <input> element instead, place it *before* the visual <div>, and apply peer-focus-visible classes to the visual element to ensure focus visibility and keyboard accessibility.
