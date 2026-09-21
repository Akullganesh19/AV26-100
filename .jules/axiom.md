## 2026-09-21 — Eliminated legacy integrated_diagnostics Streamlit app
**Complexity found:** A standalone Streamlit app (`integrated_diagnostics/app.py`), along with Jupyter notebooks, CSV datasets, and duplicate model files, running parallel to the main FastAPI backend and React frontend.
**Why it existed:** It was likely the initial prototype or MVP for the clinical diagnostic models before they were integrated into the main EpiSense FastAPI backend and React `DiagnosticsCenter` frontend.
**Eliminated:** The entire `integrated_diagnostics` directory (425+ lines of Streamlit UI code, old notebooks, duplicate requirements.txt, and CSV datasets). The `.sav` model files were preserved and moved into the main backend structure.
**Net change:** -425 lines of Python Streamlit code, removed 1 complete parallel application abstraction, and deleted several MBs of unused Jupyter notebooks and datasets.
**Next target:** Any duplicate database session management or overlapping Pydantic schemas between clinical and main backend.
