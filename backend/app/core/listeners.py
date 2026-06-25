from sqlalchemy import event
from app.models.alert import Alert
from app.core.events import event_bus

@event.listens_for(Alert, "after_insert")
def receive_alert_after_insert(mapper, connection, target):
    event_bus.publish(
        "alert.triggered",
        alert_id=str(target.id),
        district_id=str(target.district_id),
        disease=target.disease,
        risk_score=float(target.risk_score)
    )
