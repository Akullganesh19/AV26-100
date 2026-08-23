## 2024-05-25 — Hover-Prefetch on Strategic Map
**Product understood as:** An epidemiological platform for monitoring regional health sectors.
**Prediction invented:** Anticipating which district a user will inspect next by observing their mouse movements (hover) over the geospatial map, and prefetching its full detailed data and predictions before they even click.
**Data used:** The standard Leaflet `mouseover` event signaling intent to click.
**Impact:** Instantaneous loading when jumping from the strategic map to detailed district diagnostics. The data is already in cache.
**Next opportunity:** Prefetching specific disease metrics based on what disease the user most frequently filters by.
