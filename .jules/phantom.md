## 2025-05-15 — Request Coalescing Added
**Gap found:** Multiple identical simultaneous API calls across dashboard and map components.
**Why it existed:** Components fetched their data independently without a shared deduplication strategy.
**Built:** Axios client monkey-patched to keep track of in-flight requests by their URI. Concurrent identical requests now simply resolve via a single cached Promise.
**Hot path affected:** Any simultaneous renders of components like `StrategicMap`, `Dashboard`, and `TacticalAlerts` making identical requests to the backend.
**Measurable improvement:** Redundant network calls eliminated (N -> 1) per tick, reducing server load and unblocking the client JS thread.
**Next opportunity:** Background Sync caching to handle offline state and improve load speed for unchanged data.
