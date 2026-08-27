## 2024-05-24 — Streamlit App and Duplicated ML Paths
**Complexity found:** A completely isolated Streamlit web application (`integrated_diagnostics/app.py`), duplicate Jupyter notebooks, raw datasets, and PDF artifacts residing in a separate directory (`integrated_diagnostics`), alongside ML `.sav` models that the backend actually depends on.
**Why it existed:** It was likely an initial prototype for disease prediction built by data scientists before the FastAPI + React stack was implemented.
**Eliminated:** The entire `integrated_diagnostics` directory (~425 lines of Python, plus notebooks and datasets). The essential ML models were relocated to the standardized `models/clinical` directory.
**Net change:** +0 lines added, -425 lines removed (excluding Jupyter notebooks and static files), 1 orphaned app eliminated.
**Next target:** Any duplicate state management in the React frontend or overlapping background tasks in the Celery worker.
