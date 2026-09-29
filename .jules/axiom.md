## 2026-09-29 — Legacy Streamlit App (`integrated_diagnostics`)
**Complexity found:** An entire standalone Streamlit application (425 lines) existing alongside the primary React frontend and FastAPI backend.
**Why it existed:** Likely built as a quick initial prototype for clinical model validation before the unified platform (EpiSense) was fully architected.
**Eliminated:** The entire `integrated_diagnostics/` directory, moving only the `.sav` models into the backend (`backend/app/clinical_models/`).
**Net change:** -425 lines of Python, 1 complete duplicate abstraction layer (UI/API) eliminated.
**Next target:** Evaluate redundant state management or unused API wrappers in the frontend.
