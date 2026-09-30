## 2026-09-30 — Eliminated standalone integrated_diagnostics app
**Complexity found:** A standalone Streamlit application (`integrated_diagnostics`) with redundant UI code, duplicating diagnostic prediction logic already present in the FastAPI backend (`ClinicalService`).
**Why it existed:** Likely built as a standalone prototype or proof-of-concept for the clinical diagnostic ML models before they were fully integrated into the main EpiSense FastAPI and React platform.
**Eliminated:** The entire `integrated_diagnostics` directory (Streamlit UI, notebooks, duplicated static assets).
**Net change:** -425 lines of code, 1 entire frontend framework (Streamlit) removed. Models migrated to `backend/app/clinical_models/`.
**Next target:** Evaluate redundant API layers or abstracted data mappers between the DB and services.
