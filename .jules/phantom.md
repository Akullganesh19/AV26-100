## 2024-05-01 — Request Coalescing
**Gap found:** No request coalescing existed. Identical API calls to the same endpoint were executed simultaneously when multiple components mounted.
**Why it existed:** Native `axios` and standard `useQuery` setups don't automatically deduplicate requests across distinct queries with slightly different keys or when bypassing query caches completely.
**Built:** Request coalescing in `frontend/src/api/client.ts` by intercepting/overriding `apiClient.get` and returning shared promises for identical in-flight requests.
**Hot path affected:** Initial dashboard load where multiple components request district and alert data.
**Measurable improvement:** Reduces redundant network requests significantly on page load; measurable via browser network tab and backend request logs.
**Next opportunity:** Investigate Edge Cache Headers or Service Worker caching for offline/stale-while-revalidate capabilities.
