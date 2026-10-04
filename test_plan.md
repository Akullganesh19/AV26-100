1. **Implement EventBus (Phantom/Synapse Pattern):**
   - I will use `run_in_bash_session` to write `backend/app/events/__init__.py` and `backend/app/events/bus.py` using `cat << 'EOF'`.
   - The code for `bus.py` will be:
```python
import asyncio
from collections import defaultdict
from typing import Callable, Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)

    def on(self, event_name: str, listener: Callable):
        self._listeners[event_name].append(listener)
        logger.info(f"EventBus: Registered listener for event: {event_name}")

    async def emit(self, event_name: str, *args, **kwargs):
        listeners = self._listeners.get(event_name, [])
        if not listeners:
            return
        logger.info(f"EventBus: Emitting event: {event_name} to {len(listeners)} listeners")
        for listener in listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(*args, **kwargs)
                else:
                    listener(*args, **kwargs)
            except Exception as e:
                logger.error(f"EventBus: Error in event listener for {event_name}: {e}", exc_info=True)

event_bus = EventBus()
```
   - The code for `__init__.py` will be:
```python
# Event system for loosely coupled cross-system communication
from .bus import event_bus

__all__ = ["event_bus"]
```

2. **Verify EventBus Creation:**
   - Use `run_in_bash_session` to `cat` the contents of the newly created files and verify they were written correctly.

3. **Inject Event Emission in AlertService:**
   - I will use `replace_with_git_merge_diff` to modify `backend/app/services/alert_service.py`. The diff will add `from app.events import event_bus` and `await event_bus.emit('alert.triggered', new_alert)` inside `evaluate_clinical_cluster` and `evaluate_autonomous_outbreak`.
   - The diff will look like this:
```
<<<<<<< SEARCH
from app.models.alert import Alert, AlertStatus, AlertType
from app.models.audit_log import PredictionAuditLog
from app.models.prediction import Prediction
from app.core.config import settings

logger = logging.getLogger(__name__)

class AlertService:
=======
from app.models.alert import Alert, AlertStatus, AlertType
from app.models.audit_log import PredictionAuditLog
from app.models.prediction import Prediction
from app.core.config import settings
from app.events import event_bus

logger = logging.getLogger(__name__)

class AlertService:
>>>>>>> REPLACE
<<<<<<< SEARCH
                        })
                    )
                    db.add(new_alert)
                    await db.commit()
                    logger.info(f"TACTICAL ALERT: Clinical cluster detected in {district_id} ({disease})")

        except Exception as e:
=======
                        })
                    )
                    db.add(new_alert)
                    await db.commit()
                    await db.refresh(new_alert)
                    logger.info(f"TACTICAL ALERT: Clinical cluster detected in {district_id} ({disease})")
                    await event_bus.emit('alert.triggered', new_alert)

        except Exception as e:
>>>>>>> REPLACE
<<<<<<< SEARCH
                alert_type=AlertType.AUTONOMOUS,
                status=AlertStatus.TRIGGERED
            )
            db.add(new_alert)
            await db.commit()

    @staticmethod
    async def acknowledge_alert(db: AsyncSession, alert_id: str, user_id: str):
=======
                alert_type=AlertType.AUTONOMOUS,
                status=AlertStatus.TRIGGERED
            )
            db.add(new_alert)
            await db.commit()
            await db.refresh(new_alert)
            await event_bus.emit('alert.triggered', new_alert)

    @staticmethod
    async def acknowledge_alert(db: AsyncSession, alert_id: str, user_id: str):
>>>>>>> REPLACE
```

4. **Verify AlertService modifications:**
   - Use `run_in_bash_session` to read the updated file and verify the emit changes were placed correctly.

5. **Create the Connection Listener (`alert_routing.py`):**
   - I will use `run_in_bash_session` to create the module `backend/app/connections/alert_routing.py` using `cat << 'EOF'`.
   - The file will contain:
```python
import logging
import asyncio
from sqlalchemy import select, text
from app.events import event_bus
from app.models.alert import Alert
from app.models.user import User
from app.models.district import District
from app.models.user_district import user_district_association
from app.core.database import SessionLocal
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def route_alert_to_users(alert: Alert):
    """
    Listens for new tactical alerts and routes them to users assigned to the
    affected district who have email_alerts enabled and a matching risk threshold.
    """
    logger.info(f"Synapse: Evaluating routing for Alert {alert.id}")

    async with SessionLocal() as db:
        # Load the district name
        district_result = await db.execute(select(District).where(District.id == alert.district_id))
        district = district_result.scalar_one_or_none()
        district_name = district.name if district else "Unknown District"

        # Find users who monitor this district and want alerts
        query = (
            select(User)
            .join(user_district_association, User.id == user_district_association.c.user_id)
            .where(user_district_association.c.district_id == alert.district_id)
            .where(User.email_alerts == True)
            .where(User.is_active == True)
        )
        result = await db.execute(query)
        users = result.scalars().all()

        notified_count = 0
        for user in users:
            # Check user threshold against alert risk_score
            # risk_score is typically 0-1, alert_threshold is 0-100
            if (alert.risk_score * 100) >= user.alert_threshold:
                # Dispatch targeted notification
                asyncio.create_task(
                    send_alert_notification(
                        alert_id=str(alert.id),
                        district_name=district_name,
                        disease=alert.disease,
                        risk_score=float(alert.risk_score)
                    )
                )
                notified_count += 1

        logger.info(f"Synapse: Alert {alert.id} routed to {notified_count} users")

# Register the listener
event_bus.on('alert.triggered', route_alert_to_users)
```

6. **Verify Connection Listener:**
   - I will use `run_in_bash_session` to `cat` `backend/app/connections/alert_routing.py` to ensure it was created correctly.

7. **Integrate the Connection into `main.py`:**
   - I will use `replace_with_git_merge_diff` to add `import app.connections.alert_routing` to `backend/app/main.py` so the event listeners are registered at application startup.
   - The diff will look like this:
```
<<<<<<< SEARCH
from app.api.deps import get_db, limiter
from app.services.prediction_service import load_artifacts, ml_state
from app.core.scheduler import start_scheduler, stop_scheduler
from app.core.logging import setup_logging

# Initialize Structured Logging
setup_logging()
logger = logging.getLogger(__name__)
=======
from app.api.deps import get_db, limiter
from app.services.prediction_service import load_artifacts, ml_state
from app.core.scheduler import start_scheduler, stop_scheduler
from app.core.logging import setup_logging
import app.connections.alert_routing  # noqa: F401

# Initialize Structured Logging
setup_logging()
logger = logging.getLogger(__name__)
>>>>>>> REPLACE
```

8. **Verify main.py modifications:**
   - Use `run_in_bash_session` to read the updated file to confirm the connection module is imported successfully.

9. **Run all relevant tests:**
   - Use `run_in_bash_session` to execute the full backend test suite to ensure the proposed changes did not introduce regressions:
     `cd backend && pip install -r requirements.txt pytest pytest-asyncio cachetools redis email-validator cloudinary "algoliasearch<4.0" sendgrid stream-chat && DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost/episense_test" SECRET_KEY="dummy" CELERY_BROKER_URL="redis://localhost:6379/0" ALGOLIA_API_KEY="dummy" ALGOLIA_APP_ID="dummy" STREAM_API_KEY="dummy" STREAM_API_SECRET="dummy" PYTHONPATH=. python3 -m pytest tests/`

10. **Create Journal Entry (.jules/synapse.md)**
   - I will use `run_in_bash_session` to write to `.jules/synapse.md` and explicitly instruct it to follow the exact Synapse journal formatting requirements outlined in memory, using `$(date +%Y-%m-%d)` for the date.

11. **Pre-commit Steps**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

12. **Submit Changes**
   - Use the `submit` tool to push code with a formatted PR title ('🧠 Synapse: Auth ↔ Alerts') and body.
