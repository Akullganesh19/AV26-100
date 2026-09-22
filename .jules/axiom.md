## 2024-05-18 — Standalone integrated_diagnostics App

**Complexity found:** An entire standalone Streamlit application (`integrated_diagnostics`) serving clinical models that duplicate functionality already present in the primary React frontend and FastAPI backend.

**Why it existed:** Likely an early prototype or parallel development branch for testing clinical models before they were integrated into the main `DiagnosticsCenter.tsx` and `backend/app/services/clinical_service.py` layers.

**Eliminated:** The entire `integrated_diagnostics` directory, including its standalone `app.py`, duplicate datasets, Jupyter notebooks, and redundant UI logic. We've preserved only the `.sav` model files, migrating them into the standard backend structure (`backend/app/clinical_models/`).

**Net change:** Deleted ~5,000 lines of redundant code (Streamlit app, notebooks) and several abstractions. Unified the model serving architecture under a single API.

**Next target:** Any other standalone apps, redundant ML training scripts, or scattered frontend components doing similar work.
