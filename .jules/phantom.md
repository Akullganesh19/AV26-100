## 2026-10-06 — Request Coalescing

**Gap found:** Multiple components on the same page can simultaneously request the same API endpoint, resulting in duplicate network calls. React Query deduplicates internally, but direct usages of the API client (like those in initial page loads or custom hooks) could still double-fetch.
**Why it existed:** The default Axios setup provides no built-in deduplication mechanism, focusing only on single-request handling.
**Built:** Request coalescing middleware around `apiClient.get`. It maintains a Map of in-flight promises keyed by URL and query parameters. If a request for the same URL + params is issued while one is already in-flight, it returns the existing promise instead of hitting the network.
**Hot path affected:** Any data-fetching operation that happens simultaneously from different parts of the UI, especially on initial load or map/dashboard interactions.
**Measurable improvement:** Reduces the number of redundant HTTP GET requests under load. Can be measured by counting network requests in the browser DevTools when multiple components mount.
**Next opportunity:** Investigate Edge Cache Headers or stale-while-revalidate patterns for reference data like `districtData` to avoid network entirely when appropriate.
