## 2026-09-26 — Elimination of Standalone Diagnostics App

**Complexity found:** The `integrated_diagnostics` directory containing a legacy Streamlit application, duplicated model files, Jupyter notebooks, datasets, and a separate requirements.txt. The application endpoints in `backend/app/api/routes/clinical.py` already perform the same predictions. The frontend components directly interact with these FastAPI endpoints.

**Why it existed:** Historically, it seems this was an initial, standalone data science proof-of-concept or a separate tool created before it was fully integrated into the EpiSense backend.

**Eliminated:** The entire `integrated_diagnostics` directory, consisting of `app.py`, training notebooks, CSV datasets, duplicate `.sav` models, and a certificate PDF.

**Net change:** Removed 1 standalone app, 3 notebooks, 3 datasets, duplicate dependencies, and roughly 400 lines of Python code in `app.py`. The machine learning `.sav` models were correctly moved to `backend/app/clinical_models/` and referenced via `settings.CLINICAL_MODELS_DIR`.

**Next target:** Check `frontend/src/pages/DiagnosticsCenter.tsx` for axios usage that bypasses the centralized `apiClient`.
