## 2026-06-16 — Intent & Behavioral Prefetching
**Product understood as:** An epidemiological intelligence platform (EpiSense) showing real-time tactical and strategic screening & alerts for a specific sector.
**Prediction invented:**
  1. **Behavioral Report Prefetching**: When a user runs a diagnostic and receives a high-risk prediction, they almost always need the Tactical Report next. We now pre-generate and cache the report blob immediately on diagnosis completion.
  2. **Intent-Based Route Prefetching**: Hovering over a navigation link is a high-confidence signal for an upcoming click. We use `queryClient.prefetchQuery` on hover to preload data for the destination view (dashboard stats, map districts, tactical alerts) before the route transition occurs.
**Data used:**
  - Clinical prediction event completion signal.
  - Hover (`onMouseEnter`) intent signal on navigation UI.
**Impact:**
  - Zero perceived latency when downloading the tactical report.
  - Zero perceived network load time when navigating across critical dashboard views.
**Next opportunity:** Background-evaluating other diseases (e.g. Parkinsons) automatically if standard vitals from a Heart/Diabetes check strongly correlate with them.
