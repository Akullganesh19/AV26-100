## 2023-10-24 — Request Coalescing
**Gap found:** Uncoalesced API calls via `apiClient.get` allowed duplicate simultaneous requests.
**Why it existed:** Simple Axios instantiation without interceptors handling deduplication.
**Built:** Wrapped `apiClient.get` to share Promises for identical concurrent requests using a Map.
**Hot path affected:** Initial page loads where multiple components fetch the same reference data.
**Measurable improvement:** Reduced redundant network calls; observable via console debug logs and network tab.
**Next opportunity:** Edge Cache Headers or Stale-while-revalidate for static config data.
