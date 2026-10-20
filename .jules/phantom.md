## 2025-10-20 — Request Coalescing Added
**Gap found:** Multiple components (Dashboard, Alerts, Map) often independently fetch the same endpoint simultaneously on page load without deduplication.
**Why it existed:** Quick scaffolding of React Query + raw Axios calls with no global network deduplication layer.
**Built:** An invisible Axios interceptor/wrapper that coalesces identical in-flight GET requests, mapping them to the same Promise.
**Hot path affected:** Every single data fetch operation in the app on initial render or refetch.
**Measurable improvement:** Reduces duplicate network calls by mapping concurrent identical requests to a single Promise. Identifiable via console debug "[Phantom] Coalescing request for: <url>".
**Next opportunity:** Investigate Edge Caching headers or background sync for non-critical writes.
