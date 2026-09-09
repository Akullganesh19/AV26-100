## 2024-05-18 - SQLAlchemy AsyncSession limitations

**Learning:** `asyncio.gather` cannot be safely used to concurrently run database queries on the same SQLAlchemy `AsyncSession` object. The `_db_lock` implementation in the codebase suggests it's not thread-safe.

**Action:** Prefer combining queries at the database level (e.g., using multiple aggregations in a single `select`) rather than running them concurrently in Python when using the same database session.
