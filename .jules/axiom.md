## 2024-05-18 — Legacy Streamlit Prototype & Duplicated Clinical Service Methods
**Complexity found:** An entire redundant `integrated_diagnostics/` folder containing a legacy Streamlit app, duplicate Jupyter notebooks, and datasets. Also, `predict_heart`, `predict_diabetes`, and `predict_parkinsons` endpoints and service methods had identically duplicated try/except blocks and orchestration logic.
**Why it existed:** The `integrated_diagnostics/` folder was likely an early prototype created by data scientists before the FastAPI backend was built. The service methods duplicated logic because they were built iteratively without refactoring for common patterns.
**Eliminated:** Removed the legacy `integrated_diagnostics/` folder. Moved `Saved_Models` to `backend/models/clinical`. Collapsed 3 `predict_*` service methods into 1 `predict` method. Collapsed 3 API try/except blocks into 1 `_process_diagnosis` helper.
**Net change:** -425 lines in `app.py`, -50 lines in `clinical.py` and `clinical_service.py`, removed duplicated notebooks and CSVs.
**Next target:** Identify if `PredictionAuditLog` and `Prediction` models can be combined.
