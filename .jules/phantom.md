## 2026-10-24 — Request Coalescing Added
**Gap found:** The `apiClient.get` method in `frontend/src/api/client.ts` lacked request coalescing, meaning components fetching the same API resource simultaneously would trigger multiple identical network requests.
**Why it existed:** The original Axios client implementation was straightforward and unoptimized for concurrent component rendering fetching the same endpoints.
**Built:** An invisible deduplication layer wrapping `apiClient.get`. It intercepts GET requests and stores their Promises in a Map keyed by the serialised URI. Concurrent identical requests reuse the same Promise. The Promise is cleaned up when resolved.
**Hot path affected:** Any UI rendering flow where multiple child components fetch the same API resource simultaneously.
**Measurable improvement:** Reduces duplicate network traffic and server load. Can be measured by counting intercepted deduplicated requests using `console.debug` statements in the frontend and checking the backend access logs.
**Next opportunity:** Implement a robust caching layer with stale-while-revalidate capabilities for less frequently changing reference data.
