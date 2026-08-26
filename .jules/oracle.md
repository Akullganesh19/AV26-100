## 2024-08-26 — Predict Batch N+1 Resolution
**Bottleneck found:** N+1 query and serialization in `predict_batch` in `PredictionService`. It called `predict_single` per district which ran a separate `FeatureBuilder.build` query inside a lock.
**Fix:** Added `build_batch` to `FeatureBuilder` using a single `WHERE district_id IN (...)` query to fetch features, and refactored `predict_batch` to do vectorized machine learning transformations and predictions over a single dataframe.
**Scale impact before/after:** O(N) database queries and O(N) model prediction operations -> 1 batched database query and 1 batched model prediction.
**Next opportunity:** Investigate pagination/lazy loading on `list_districts` if the number of districts grows beyond what can be comfortably mapped and returned in a single HTTP response.
