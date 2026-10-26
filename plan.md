1. **Fix `conftest.py` Database URL generation**
   - The CI is failing because `TEST_DATABASE_URL` is generating `episense_test_test` since the CI environment provides `episense_test` in the `DATABASE_URL`.
   - Update `backend/tests/conftest.py` to correctly conditionally append `_test` using memory instructions.
2. **Verify file change**
   - Check `backend/tests/conftest.py` to ensure the change was made successfully.
3. **Execute pre-commit instructions**
   - Run pre-commit instructions to ensure everything is correct.
4. **Submit PR**
   - Call submit with the updated code.
