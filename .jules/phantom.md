## 2024-06-20 — Request Coalescing
**Gap found:** Duplicate concurrent API GET requests were independently hitting the network.
**Why it existed:** Default Axios behavior without deduplication.
**Built:** A request coalescing layer in `apiClient.get` that returns an in-flight Promise for identical concurrent requests.
**Hot path affected:** Any page or component that fetches the same data concurrently.
**Measurable improvement:** Reduces duplicate network requests on page load, lowering backend load and speeding up client render.
**Next opportunity:** Edge caching headers or background syncing for non-critical writes.
