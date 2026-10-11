## 2024-10-12 — Request Coalescing Added
**Gap found:** Multiple components on the dashboard fetch the exact same endpoints simultaneously on page load (e.g. `/districts/stats`), duplicating network traffic. Also, bare `axios` was being used, circumventing auth headers and future caching mechanisms.
**Why it existed:** Components were independently fetching data without a centralized mechanism to deduplicate identical in-flight network requests.
**Built:** Request coalescing in `apiClient.ts` that intercepts outgoing GET requests. If a request for the same URL is already in flight, subsequent calls attach to the existing Promise rather than initiating a new HTTP connection. All pages updated to use `apiClient`.
**Hot path affected:** Initial dashboard page load where multiple widgets request the same configuration/stats data simultaneously.
**Measurable improvement:** Visible reduction in duplicate network requests in browser devtools, with debug console indicating `[Phantom] Coalescing duplicate request to: ...`.
**Next opportunity:** Stale-while-revalidate caching pattern for reference data (like district lists).
