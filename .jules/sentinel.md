## Phase 1: Orient
- Identified insecure deserialization via `joblib.load()` on disk files without integrity checks in `backend/app/services/prediction_service.py`.

## Phase 2: Hunt
- Explored how model artifacts are saved and the data flow.
- Located model generation in `backend/app/ml/train.py`, which saves `.joblib` files and writes metadata to `latest.json`.

## Phase 3: Invent
- The solution relies on computing SHA-256 hashes of the `.joblib` artifacts upon saving and placing these hashes in the `latest.json` manifest.
- When loading artifacts, verify the hashes against the manifest. If they mismatch, throw a `RuntimeError`.
- Ensure deserialization happens *from memory* (`io.BytesIO(content)`) after verification to prevent TOCTOU attacks.

## Phase 4: Build
- Added `"hashes"` to `latest.json` generation in `backend/app/ml/train.py`.
- Added integrity validation to `load_artifacts()` in `backend/app/services/prediction_service.py`.

## Phase 5: Verify
- Created a test in `backend/tests/ml/test_prediction_service.py` testing for hash mismatch.
- Set up a postgres database and environment, ran tests to ensure success.

## Phase 6: PR
- Opened PR addressing insecure deserialization vulnerability.
