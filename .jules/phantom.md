## 2024-09-10 — Request Coalescing Added
**Gap found:** Multiple identical concurrent API requests were not coalesced.
**Why it existed:** The frontend simply used `axios.get` or react-query indiscriminately, missing out on deduping raw `axios` calls that could happen simultaneously (e.g. initial loads of components rendering multiple subcomponents requiring the same base data, or independent queries on dashboard).
**Built:** An axios wrapper `withRequestCoalescing` that tracks in-flight GET requests and returns the same Promise for identical concurrent requests.
**Hot path affected:** Any place making frequent or duplicated raw GET requests (like dashboards, strategic maps, tactical alerts all triggering `axios.get` independently).
**Measurable improvement:** Reduces the number of duplicate network requests made by the frontend, particularly visible in the dev tools network tab when mounting a complex layout with independent components.
**Next opportunity:** Edge-caching for static reference data (like the district boundaries map) or background pre-fetching based on cursor position.
