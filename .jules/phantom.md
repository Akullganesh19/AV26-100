## 2025-01-20 — Request Coalescing
**Gap found:** Raw axios was being used without deduplicating identical simultaneous GET requests, meaning multiple components mounting simultaneously could trigger the exact same API fetch redundantly.
**Why it existed:** Native `axios` does not coalesce requests by default; React components natively fire their effect hooks independently, and standard `useQuery` setups or direct fetch calls don't deduplicate network-level calls across the app without extra config.
**Built:** Overrode the `apiClient.get` method to intercept and map in-flight requests by URL and config. If an identical request is fired while one is pending, the new caller simply awaits the existing promise instead of hitting the network again.
**Hot path affected:** Every data fetch component on page load.
**Measurable improvement:** Reduced network requests by collapsing duplicate concurrent fetches on complex dashboard views.
**Next opportunity:** Stale-while-revalidate caching with TTL for immutable reference data like config or static geojson.
