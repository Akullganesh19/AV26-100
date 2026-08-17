## 2025-03-09 — Batch Prediction Cache
**Gap found:** Prediction batching naively re-computed inferences on every call even when a valid prediction record was already persisted in the database for the same day and model version.
**Why it existed:** The batch processing wrapped the `predict_single` function in `asyncio.gather` for concurrency, ignoring the database cache on read paths entirely, resulting in heavy database writes and repeated ML inference.
**Built:** A read-only cache lookup in `predict_batch` using a bulk SQL query. Existing predictions are fetched in one DB call, and only missing predictions fall back to the heavy computation tasks.
**Hot path affected:** District listing endpoint (`/api/v1/districts`), which loads on every dashboard refresh.
**Measurable improvement:** Reduces N heavy CPU-bound machine learning inferences and database write conflicts to a single efficient SQL select query for all previously computed districts, improving dashboard load times.
**Next opportunity:** Background pre-computation of predictions.
