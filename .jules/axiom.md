## 2025-02-12 — Integrated Diagnostics Elimination
**Complexity found:**
1. An entire standalone Streamlit application (`integrated_diagnostics/app.py` - 425 lines) existed alongside the main React frontend and FastAPI backend.
2. A rogue unused UI component `frontend/src/components/CalculatorSection.tsx` hijacked `frontend/src/App.tsx`.
3. In `backend/app/services/clinical_service.py`, there were three nearly identical predictor methods (`predict_heart`, `predict_diabetes`, `predict_parkinsons`).

**Why it existed:**
1. Historically, a separate Streamlit app was built for diagnostic tooling, likely as a prototype.
2. The UI component was a remnant of an unmerged or abandoned feature testing branch.
3. Repetitive backend logic was likely written hastily for each endpoint without abstracting.

**Eliminated:**
1. The `integrated_diagnostics` directory containing the Streamlit app.
2. `frontend/src/components/CalculatorSection.tsx` and its hijacking of `App.tsx`.
3. Consolidated the three `predict_*` methods into a single `predict` method in `ClinicalService`.

**Net change:** -670 lines deleted, 1 full separate application stack (Streamlit) removed, 1 dead UI component removed, 3 repetitive methods collapsed into 1.

**Next target:** Evaluate ML model duplication and abstraction layers in `backend/app/services/prediction_service.py`.
