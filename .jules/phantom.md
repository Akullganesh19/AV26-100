## 2024-05-18 — Optimistic Updates for Alert Acknowledgement
**Gap found:** Alert acknowledgement was a synchronous-feeling operation where the UI waited for the network before updating to "ACKNOWLEDGED".
**Why it existed:** Default mutation behavior waits for the server response and invalidation before updating local cache.
**Built:** Optimistic Updates. UI updates instantly by manually updating the React Query cache, and rolls back if the server request fails.
**Hot path affected:** Tactical alert acknowledgements.
**Measurable improvement:** Reduces perceived latency of alert acknowledgement from ~100-300ms network roundtrip to 0ms (instant UI).
**Next opportunity:** Background Sync with retry queues for offline capability.
