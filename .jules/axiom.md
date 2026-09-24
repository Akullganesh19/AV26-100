## 2024-09-24 — Legacy Standalone Streamlit App
**Complexity found:** A standalone Streamlit application (`integrated_diagnostics`) duplicating the clinical disease prediction UI and logic that is already served by the main FastAPI backend and React frontend. It coupled model artifacts to a legacy app directory.
**Why it existed:** Historically, it was likely built as a quick prototype or separate tool before the integrated EpiSense React/FastAPI stack was developed.
**Eliminated:** The entire `integrated_diagnostics` directory (Streamlit app, notebooks, raw datasets, redundant requirements). Moved just the necessary `.sav` model artifacts into `backend/app/clinical_models/` and updated the config path.
**Net change:** Eliminated over 400 lines of redundant UI code and an entire parallel application architecture.
**Next target:** Redundant state management in the React frontend or duplicated API wrapper functions.
