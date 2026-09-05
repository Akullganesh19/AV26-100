import pytest
import asyncio
from unittest.mock import patch, MagicMock
from app.services.alert_routing import route_alert_to_officers

@pytest.mark.asyncio
async def test_route_alert_to_officers():
    # Mocking db session
    mock_db = MagicMock()
    mock_result = MagicMock()
    # 4 rows: user_id, name, email, threshold
    mock_result.fetchall.return_value = [
        ("u1", "Officer 1", "o1@test.com", 50),
        ("u2", "Officer 2", "o2@test.com", 70)
    ]

    # Needs to return an awaitable
    async def mock_execute(*args, **kwargs):
        return mock_result

    mock_db.execute = mock_execute

    # Risk score 80
    result = await route_alert_to_officers(mock_db, "d1", "dengue", 80.0, "a1")

    assert len(result) == 2
    assert result[0]["email"] == "o1@test.com"
    assert result[1]["email"] == "o2@test.com"
