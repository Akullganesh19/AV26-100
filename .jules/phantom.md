## 2025-05-24 — Optimistic Updates & Predictive Prefetching
**Gap found:** Alerts waited for server confirmation before UI updated (feeling sluggish), and map hover interactions did not pre-warm the cache for district details.
**Why it existed:** Default useMutation invalidates on success without onMutate rollback logic; tooltips were static HTML bindings without React interaction handling.
**Built:** Added React Query optimistic update pipeline for immediate UI response, and attached Leaflet mouseover listeners to prefetch district detail payloads with a 5-minute staleTime.
**Hot path affected:** Acknowledging mission threats in Tactical Alerts, and hovering regions in Strategic Map.
**Measurable improvement:** Zero latency perceived on alert acknowledgment; eliminated full round-trip delay when initiating clinical triage from the map.
**Next opportunity:** Edge caching headers on the backend for static metadata endpoints.
