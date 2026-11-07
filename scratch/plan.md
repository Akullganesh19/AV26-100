1. **Re-submit In-Scope Changes**
   - The CI pipeline failed due to `python-version: '3.9'` no longer being available on `ubuntu-latest`.
   - As a strictly scoped "Bolt" persona, I am explicitly prohibited from fixing this out-of-scope infrastructure issue in `.github/workflows/ci.yml`.
   - I will use the `submit` tool to resubmit my exact in-scope code changes with a new branch name (appending `-retry`), explicitly noting in the PR description that the CI environment failure is out-of-scope and is being ignored.

2. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**

3. **Submit with proper Bolt format**
   - Use `submit` to create PR with Title: `⚡ Bolt: [batch dashboard stat queries]` and Description:
     ```
     💡 What: Batch independent scalar aggregate queries into a single database roundtrip for the dashboard stats endpoint.
     🎯 Why: The previous implementation performed 3 sequential database queries to get basic stats, causing unnecessary I/O overhead.
     📊 Impact: Reduces database roundtrips from 3 to 1, lowering connection pool contention and latency for dashboard load.
     🔬 Measurement: Check the query logs or time the `/stats` endpoint locally.

     **Note on CI failure:** The CI pipeline failure regarding Python 3.9 deprecation on ubuntu-latest is an out-of-scope infrastructure issue and has been explicitly ignored per my strict persona boundaries.
     ```
