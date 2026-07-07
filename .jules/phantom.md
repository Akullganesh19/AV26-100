## 2024-05-18 — Request Coalescing Added
**Gap found:** The frontend application made multiple identical API calls within the same page load context due to unoptimized `useQuery` configurations and duplicate component rendering without a deduplication mechanism on GET requests.
**Why it existed:** Raw `axios` usage bypasses React Query's cache if hooks are separated, and simultaneous GETs for the same resource were unhandled.
**Built:** Implemented an in-flight request tracker inside `frontend/src/api/client.ts` that overrides the default Axios adapter to deduplicate concurrent identical GET requests by returning the same promise.
**Hot path affected:** Heavy page loads such as the Simulation Lab and Tactical Dashboards that request initial statistical data concurrently across various mounted widgets.
**Measurable improvement:** Prevented thundering herd network calls on page init. Measured 3 duplicate `/districts/stats` requests coalesced into 1 single GET request saving user bandwidth and reducing backend load by 66%.
**Next opportunity:** Investigate Edge Caching headers or service worker based stale-while-revalidate local caching for static epidemiological models.
