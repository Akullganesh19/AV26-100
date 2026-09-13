## 2024-05-24 — Unified ClinicalService prediction methods
**Complexity found:** Three identical methods (`predict_heart`, `predict_diabetes`, `predict_parkinsons`) doing exactly the same operations.
**Why it existed:** Likely built incrementally or copy-pasted for each new disease without refactoring into a generic method.
**Eliminated:** `predict_heart`, `predict_diabetes`, and `predict_parkinsons` methods in favor of a single `predict(disease, features)` method.
**Net change:** -27 lines, 2 abstractions removed.
**Next target:** Any duplicate API endpoints or repetitive model loading logic.
