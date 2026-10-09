## 2024-05-24 — Request Coalescing
**Gap found:** Identical API GET requests were not coalesced.
**Why it existed:** The Axios client was naive.
**Built:** Overrode `apiClient.get` to track and return in-flight promises, preventing duplicate simultaneous identical requests.
**Hot path affected:** Every component making simultaneous data fetches (e.g., dashboard, lists).
**Measurable improvement:** Reduced redundant network requests on initial page loads and concurrent component renders.
**Next opportunity:** Edge Cache Headers or Stale-while-revalidate caching pattern.
