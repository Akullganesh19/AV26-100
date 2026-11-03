## 2026-06-16 — Eliminated Standalone Streamlit Diagnostics Module

**Complexity found:** A completely separate standalone Streamlit application (`integrated_diagnostics`) serving the exact same clinical diagnostics (heart, diabetes, parkinsons) using the exact same models that are already integrated natively into the FastAPI backend and React frontend.
**Why it existed:** Likely an early prototype or an academic artifact that was committed to the repository and never removed after the functionality was migrated to the core platform stack (`backend/app/services/clinical_service.py` and `frontend/src/pages/DiagnosticsCenter.tsx`).
**Eliminated:** The entire `integrated_diagnostics` directory (425 lines of duplicate Streamlit code, Jupyter notebooks, redundant CSV datasets, and duplicate model `.sav` files).
**Net change:** Eliminated 4128 lines across 16 files, removed a shadow backend.
**Next target:** Next session should audit state management (Zustand) versus URL params for redundancy, or duplicate model fetching logic.
