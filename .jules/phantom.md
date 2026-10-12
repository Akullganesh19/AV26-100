## 2024-05-18 — Request Coalescing Added
**Gap found:** The frontend's `apiClient` lacked request coalescing, meaning multiple components fetching the same data on mount would trigger identical independent network requests.
**Why it existed:** The `axios` instance was simply a thin wrapper over the default fetch/XHR, with no advanced request management.
**Built:** I wrapped the `apiClient.get` method to track in-flight promises using a `Map`. If an identical GET request is made while one is already pending, it returns the existing promise instead of hitting the network again.
**Hot path affected:** Every single data-fetching operation across the frontend (specifically GET requests), especially during page load where multiple components might request the same user profile or common config.
**Measurable improvement:** Reduces redundant network overhead and server load. Verifiable via the browser's Network tab (fewer duplicate requests) and via the injected `console.debug('[Phantom] Coalesced identical request to: ...')` logs.
**Next opportunity:** Background Sync or intelligent pre-fetching for frequently visited views.
