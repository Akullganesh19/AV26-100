## 2026-06-17 — Webfluin Override and Streamlit App Eliminated
**Complexity found:** An entire dead marketing UI (Webfluin Studio) overlaying the frontend `App.tsx`, and a fully redundant standalone Streamlit application (`integrated_diagnostics`) duplicating existing React/FastAPI diagnostic capabilities.
**Why it existed:** Likely abandoned prototype artifacts or poorly merged external marketing code that hijacked the root routing file, alongside an early data-science Streamlit prototype that was never cleaned up after integration into the core product.
**Eliminated:** `frontend/src/components/CalculatorSection.tsx` and the entire `integrated_diagnostics` directory. Restored native React routing.
**Net change:** -1000+ lines of duplicate frontend and backend UI code, 2 entirely eliminated presentation layers. Models moved securely to the core backend repository.
**Next target:** Evaluate redundant API client utility layers or deeply nested component mapping in `StrategicMap`.
