## YYYY-MM-DD — Eliminate redundant integrated_diagnostics module

**Complexity found:** The entire `integrated_diagnostics` module (over 400 lines of `app.py`, redundant models, its own Streamlit frontend, and separate dependencies).
**Why it existed:** It seems to have been an initial standalone prototype or a legacy module for clinical diagnostics that was later fully re-implemented and integrated into the main `backend` (FastAPI + `ClinicalService`) and `frontend` (React + `DiagnosticsCenter.tsx`).
**Eliminated:** The entire `integrated_diagnostics` folder, including its duplicate models, datasets, notebooks, and standalone Streamlit app.
**Net change:** -425 lines in `app.py`, -6 duplicate `.sav` model files, -3 CSV datasets, -3 Jupyter notebooks, -1 duplicate README, and -1 separate Requirements.txt.
**Next target:** Evaluate `ReportService` and `PDF` generation redundancy (FastAPI backend generates a PDF, maybe Streamlit did too).
