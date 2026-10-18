## 2024-05-10 — Request Coalescing
**Gap found:** The API client lacked request coalescing, allowing multiple components to simultaneously fetch the same resource from the server.
**Why it existed:** The default Axios setup performs independent requests for every component that triggers a fetch, leading to duplicated network traffic.
**Built:** A transparent request deduplicator intercepting `apiClient.get`. It stores in-flight requests in a Map and returns the existing promise for identical concurrent requests.
**Hot path affected:** Any dashboard or data-rich page where multiple components rely on the same endpoint (e.g., user profiles or config data).
**Measurable improvement:** Significantly reduced redundant network requests and reduced latency on page load. Proven via `console.debug` logs.
**Next opportunity:** Implement a stale-while-revalidate caching mechanism to serve immediate data while silently updating in the background.
