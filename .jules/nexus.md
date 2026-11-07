## 2026-11-07 — District Watchlist
**Product understood as:** An epidemiological command center that monitors disease risk across all districts to direct tactical response.
**Derivation reasoning:** This product has districts, predictions, and users. Users monitor districts through the `DistrictMatrix` to view their risk. Therefore, users obviously need a way to filter the matrix to only show the districts they are responsible for (their jurisdiction) — because it's overwhelming to constantly search for specific districts among all 50 every time they log in.
**Feature built:** Added backend endpoints to watch/unwatch districts utilizing the existing `user_districts` join table. Built the `DistrictMatrix` frontend component with a "National Overview" vs "My Jurisdiction" toggle and a star button to manage watched districts.
**User impact:** Users can now curate a personalized dashboard view, eliminating noise and allowing them to focus instantly on the specific regions they govern.
**Next logical feature:** Derive notification preference settings per watched district (e.g. only alert me if MY watched district passes threshold).
