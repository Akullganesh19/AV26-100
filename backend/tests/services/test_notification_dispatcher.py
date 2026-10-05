import pytest
import uuid
from unittest.mock import AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession
from app.services.notification_dispatcher import dispatch_targeted_alerts
from app.models.alert import Alert

@pytest.mark.asyncio
async def test_dispatch_targeted_alerts_mocked(mocker):
    mock_send_alert = mocker.patch("app.services.notification_dispatcher.send_alert_notification", new_callable=AsyncMock)

    mock_db = AsyncMock(spec=AsyncSession)

    class MockUser:
        def __init__(self, id):
            self.id = id

    # Mock the return value of db.execute(query).scalars().all()
    mock_scalars = mocker.MagicMock()
    mock_scalars.all.return_value = [MockUser(uuid.uuid4()), MockUser(uuid.uuid4())]

    mock_result = mocker.MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db.execute.return_value = mock_result

    alert = Alert(
        id=uuid.uuid4(),
        district_id=uuid.uuid4(),
        disease="Test Disease",
        risk_score=0.80
    )

    await dispatch_targeted_alerts(mock_db, alert, "Test District")

    assert mock_send_alert.call_count == 2
