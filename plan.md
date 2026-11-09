1. **Fix duplicate database suffix in `backend/tests/conftest.py` using `replace_with_git_merge_diff`**:
   - Update the `TEST_DATABASE_URL` logic to strip trailing slashes and correctly append `_test` only if it isn't already present (per memory: `url = str(settings.DATABASE_URL).rstrip("/"); TEST_DATABASE_URL = url if url.endswith("_test") else f"{url}_test"`).
2. **Verify changes in `backend/tests/conftest.py`**:
   - Run `cat backend/tests/conftest.py` to ensure the suffix check is properly implemented.
3. **Verify Git Status**:
   - Run `git status` to ensure only correct files are staged and delete `plan.md`.
4. **Test Execution**:
   - Since we are fixing the backend tests logic, and we might lack dependencies natively, we'll try to run a static check via `python3 -c "import py_compile; py_compile.compile('backend/tests/conftest.py')"`.
5. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done**:
   - Run `pre_commit_instructions` tool.
6. **Submit PR via `submit` tool**:
   - `branch_name`: `synapse-auth-alerts`
   - `commit_message`: `🧠 Synapse: Auth ↔ Alerts targeted notifications`
   - Description containing the Synapse PR template.
