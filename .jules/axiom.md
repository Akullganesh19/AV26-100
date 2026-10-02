## 2026-10-02 — Legacy integrated_diagnostics Streamlit app
**Complexity found:** A completely separate Streamlit application with its own frontend and logic for clinical diagnostics.
**Why it existed:** Likely a legacy prototype built before the main React frontend and FastAPI backend were implemented.
**Eliminated:** The entire integrated_diagnostics directory, migrating only the .sav models to backend/app/clinical_models.
**Net change:** Deleted over 400 lines of app code, multiple Jupyter notebooks, datasets, and redundant requirement files.
**Next target:** Unnecessary abstractions in backend services or Redux/Zustand stores in frontend.
