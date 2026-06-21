## 2025-06-21 — Backend Test DB Flakiness

**Failure point found:** GitHub actions CI runner was complaining that `database "episense_test_test" does not exist`.
**Why it existed:** The `TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"` line in `tests/conftest.py` appended `_test` blindly. If a `.env` file explicitly supplied a DATABASE_URL ending in `_test` already, the appended `_test` created an invalid double suffix `_test_test` that wasn't created in setup steps.
**Recovery built:** Enforced an idempotent check so `_test` is only appended `if not TEST_DATABASE_URL.endswith("_test")`.
**Blast radius before:** Complete CI failure preventing all backend tests from succeeding on any PR if `.env` configurations leaked `_test` URLs or re-ran tests.
**Blast radius after:** None. Local and CI DB URLs appropriately target `_test` automatically.
**Logging/alerting:** N/A
**Remaining failure points:** Ensuring that `Base.metadata.create_all` captures all models via direct imports before creation, which is already correctly observed.
