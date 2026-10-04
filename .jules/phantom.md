## $(date +%Y-%m-%d) — Invisible Infrastructure Added (Request Coalescing)

**Gap found:** The frontend components were making multiple identical independent GET requests for the same endpoints via naive `axios.get` calls instead of utilizing the `apiClient` instance, and without any deduplication mechanisms.
**Why it existed:** Historically, each component was developed independently and fetched the data it required directly when mounting.
**Built:** I introduced request coalescing in the centralized `apiClient`. If multiple components request the same resource at the same time, the `inFlightRequests` Map returns the identical active promise to all requesters rather than initiating a redundant network call. I also refactored all independent `axios.get/post` usages across components to use this optimized `apiClient`.
**Hot path affected:** General navigation and page load, as well as scenarios where multiple components request shared stats, districts, active scenarios, or tactical alerts simultaneously.
**Measurable improvement:** Reduced the total number of simultaneous network requests for the same resources on any given route, improving time-to-glass by eliminating redundant networking overhead and reducing server load.
**Next opportunity:** Background caching with stale-while-revalidate logic to instantly render static/slow-changing entities like reference data (e.g., scenarios, environmental context).
