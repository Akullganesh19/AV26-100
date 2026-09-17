## 2024-09-17 — Legacy Streamlit App
**Complexity found:** The entire `integrated_diagnostics` directory containing a legacy Streamlit application (`app.py`), raw datasets, training notebooks, and redundant ML artifacts.
**Why it existed:** Historically, it seems this was the original prototype or standalone tool for clinical predictions before the functionality was integrated into the main FastAPI backend and React frontend.
**Eliminated:** The entire `integrated_diagnostics` directory (excluding the `Saved_Models` subdirectory which the backend still relies on, which was moved to `backend/app/models/clinical`).
**Net change:** Eliminated duplicate code and legacy web app (several hundred lines and multiple unused files).
**Next target:** Any remaining legacy duplicate code.
