## 2026-10-03 — [Eliminate Legacy integrated_diagnostics Directory]
**Complexity found:** An entire unmaintained standalone Streamlit application directory (`integrated_diagnostics`) containing duplicate model files, `.ipynb` notebooks, CSV datasets, and a sprawling `app.py` UI script.
**Why it existed:** Historically, this likely started as a standalone machine learning prototype or proof of concept that got bundled into the repo. The backend API (`clinical_service.py`) was reaching across boundaries into `../integrated_diagnostics/Saved_Models` to load `.sav` files.
**Eliminated:** The entire `integrated_diagnostics` directory. The essential `.sav` model files were moved directly into `backend/app/clinical_models`. The backend configuration was updated to reflect this local path.
**Net change:** Eliminated ~425 lines of legacy Streamlit UI code (`app.py`), removed multiple duplicate datasets/Jupyter notebooks, collapsed an unnecessary architectural boundary.
**Next target:** Evaluate and simplify the `PredictionAuditLog` system and `AlertService` background task trigger chains, which seem overly complex for a single tactical screening endpoint.
