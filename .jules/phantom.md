## 2024-08-15 — Batch Prediction Caching
**Gap found:** `PredictionService.predict_batch` re-runs expensive ML inference for every district sequentially via a semaphore pool, even when the underlying data hasn't changed.
**Why it existed:** The original implementation focused on single-district predictions and used a naive loop over those for batches without checking the `Prediction` table first.
**Built:** Added an intelligent caching layer in `predict_batch`. It first performs a bulk query for existing predictions for the requested districts and date. It then only performs the heavy ML inference for the missing ones, and returns the merged result in the original order.
**Hot path affected:** The district listing endpoints (`/api/v1/districts/`) that map risk scores to the frontend matrix.
**Measurable improvement:** Significantly reduces CPU usage and latency on the district list page by avoiding N redundant ML model transformations and inferences.
**Next opportunity:** Investigate similar read-heavy caching for the `/api/v1/districts/stats` endpoint.
