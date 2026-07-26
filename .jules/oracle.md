## 2026-07-26 — Predictive Geospatial Context Prefetching

**Product understood as:** An epidemiological command center mapping disease outbreak risk scores at the district level for tactical triaging.
**Prediction invented:** Behavioral hover prefetching on the Strategic Map. Anticipates that a user hovering over a specific high-risk district is highly likely to request detailed clinical triage metrics for that area. Prefetches the `/districts/{district_id}` data into the local query cache.
**Data used:** Geospatial interaction signals (mouse hover over GeoJSON map features).
**Impact:** Eliminates the ~100-300ms network latency round-trip when the user clicks "Initiate Clinical Triage", enabling instant navigation to the detailed view.
**Next opportunity:** Predicting likely scenarios to run in the Simulation Lab based on currently active alerts and regional baselines (e.g., if a Dengue alert triggers in Kerala, pre-warm a scenario adjusting rainfall parameters for that region).
