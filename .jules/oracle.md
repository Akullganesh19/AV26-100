## 2026-07-21 — [Markov Chain Route Prefetching]
**Product understood as:** An epidemiological command center requiring fast transitions between geospatial maps, diagnostic centers, and tactical alerts.
**Prediction invented:** A Markov Chain transition matrix that tracks a user's navigation sequences in `localStorage` and prefetches data for the most probable next route before they click.
**Data used:** User's own historical route-to-route transition frequencies via `location.pathname` changes.
**Impact:** Impossibly fast perceived load times as heavy dashboard, choropleth, or alert data is fetched into React Query cache *while* the user is still reading the current page.
**Next opportunity:** Expand the Markov chain to also predict and pre-populate specific *filters* (e.g. disease type or state) used within the next predicted route.