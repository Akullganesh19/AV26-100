# Medic Journal

## 🧹 Code Health Improvement: Removed unused import

- Removed the unused `TokenPayload` import from `backend/app/api/deps.py` to improve maintainability and clean up the namespace.

## 🧹 Code Health Improvement: Fixed test DB setup for CI

- Modified `backend/tests/conftest.py` to conditionally append `_test` to `TEST_DATABASE_URL` only if the database name does not already end with `_test`, fixing a CI test failure.
