## 2026-10-16 - FeatureBuilder SQL Limiting
**Learning:** Found a major N+1-like issue where `FeatureBuilder.build` was extracting the *entire* district history for a single prediction and filtering in Pandas to get `LIMIT 1`.
**Action:** Pushed `as_of_date` filtering and `LIMIT 1` down to the PostgreSQL layer to drastically reduce IO, reducing execution time from ~0.15s per query to ~0.001s.
