## 2024-05-24 — Navigational Prefetching
**Product understood as:** An epidemiological dashboard used by health officers to monitor outbreaks.
**Prediction invented:** Anticipating navigation intent. When a user hovers or focuses on a sidebar navigation link (like Map or Alerts), the system proactively fetches the required data in the background before the click occurs.
**Data used:** Hover and focus events on navigational `Link` components as intent signals.
**Impact:** Nears-instantaneous perceived loading times for primary application views, as data is pre-warmed in the React Query cache during the ~100-300ms gap between intent and action.
**Next opportunity:** Prefetching specific district details on the map before the user clicks a region.
