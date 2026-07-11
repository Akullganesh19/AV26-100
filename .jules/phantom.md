## 2024-11-20 — Request Coalescing
**Gap found:** The frontend application dispatched redundant, duplicate identical GET requests simultaneously across multiple unlinked components that fetch the same data endpoints on load.
**Why it existed:** Components were using raw `axios` instances independently, unaware of in-flight identical operations.
**Built:** Request coalescing inside the core API client (`frontend/src/api/client.ts`), capturing identical requests and returning the original promise.
**Hot path affected:** Initial dashboard rendering and data refetch intervals when multiple unlinked components request the same global data points or alerts.
**Measurable improvement:** Significantly reduced database load by ensuring maximum of 1 request per endpoint at a time for identical GET requests, preventing redundant concurrent operations.
**Next opportunity:** Expand request deduplication to batched requests or intelligent prefetching strategies for active simulations.
