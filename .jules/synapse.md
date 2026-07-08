## 2024-06-25 — Notification Targeted Targeting

**Systems connected:** Prediction Service ↔ Auth / Notifications
**Intelligence emerged:** When a high-risk outbreak is predicted, instead of firing a generic system-wide alert to a fixed channel, the system uses Auth's user data to intelligently target the exact health officers assigned to that specific district whose personal alert thresholds are met.
**Data flows:** Prediction output (district, risk_score) is published to the event bus. The subscriber reads the event, queries Auth (Users) to find who is responsible for that district and has an alert threshold below the score, and sends targeted notifications through the Notification task.
**Coupling approach:** Event Bus pattern (`app/core/events.py`). `PredictionService` publishes a `prediction.high_risk` event and does not know about users or notifications. The subscriber in `app/core/subscribers.py` handles the logic and dispatches personalized jobs via the existing `alerts.py` notification task.
**Next connection:** Feed high-risk alert acknowledgments back into ML model retraining data to prioritize true positives.
