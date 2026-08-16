## 2025-01-25 — TTLCache and Optimistic UI Updates
**Gap found:** Dashboard aggregates heavily from DB on every request. UI waits for server to acknowledge alerts.
**Why it existed:** MVP didn't require caching or optimistic UI.
**Built:** TTLCache for Stats endpoint, and optimistic UI updates for Alert acknowledgments.
**Hot path affected:** Dashboard Loading, Alert Acknowledgment.
**Measurable improvement:** Dashboard loads instantly from cache. Zero perceived latency on Alert acknowledgment.
**Next opportunity:** Investigate caching for district predictions list.
