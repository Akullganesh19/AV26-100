## Task: Code Health Improvement
- Removed unused `from __future__ import annotations` import from `backend/app/services/prediction_service.py` to reduce namespace bloat and improve readability.
- Verified safe removal by running backend pytest suite which passed successfully.
