## 2024-05-24 — Legacy Streamlit App and Redundant Datasets
**Complexity found:** A complete standalone Streamlit app (`integrated_diagnostics`) duplicating clinical screening logic, alongside static CSV datasets and Jupyter notebooks.
**Why it existed:** Likely an initial prototype or standalone demonstration tool that was integrated into the main application later.
**Eliminated:** The entire `integrated_diagnostics` directory, moving only the required `.sav` model artifacts to the backend.
**Net change:** -425 lines of redundant UI code, removed duplicate datasets, simplified architecture.
**Next target:** Any remaining duplicated logic between the frontend and backend validation or redundant data models.
