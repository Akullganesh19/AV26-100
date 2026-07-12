## YYYY-MM-DD — Request Coalescing Added
**Gap found:** The frontend `apiClient` makes duplicate GET requests when multiple components render simultaneously and fetch the same endpoint (e.g., `/districts/stats`).
**Why it existed:** There was no interceptor or wrapper around `axios.get` to deduplicate in-flight requests.
**Built:** Request coalescing in `apiClient.ts` which tracks in-flight requests and returns the same Promise for identical URLs (and serialized params) to prevent duplicate network calls.
**Hot path affected:** Initial dashboard load, matrix render, and any view with heavily nested or repeated components fetching the same API resource.
**Measurable improvement:** Reduces the number of duplicate network requests on page load, speeding up initial rendering and reducing backend load.
**Next opportunity:** Implement a true caching layer with Stale-While-Revalidate semantics for mostly-static data like district reference lists.
