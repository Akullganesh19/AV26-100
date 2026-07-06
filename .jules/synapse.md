## 2024-05-16 — Targeted Prediction Alerts
**Systems connected:** Predictions ↔ Users/Notifications
**Intelligence emerged:** The system now intelligently routes critical autonomous outbreak alerts only to specific human officers who are formally assigned to the affected district, have explicitly enabled alerts, and whose personal risk tolerance threshold has been breached by the prediction, rather than broadcasting generic alerts.
**Data flows:** When the Prediction Service generates a high-risk prediction, it publishes a `prediction.high_risk` event containing the `district_id` and `risk_score`. The User system listens, queries the Auth/User database for eligible officers matching that district and threshold, and dispatches the alert via the Notification system.
**Coupling approach:** Event Bridge Pattern. The Prediction Service uses a lightweight `EventBus` to publish the event without importing or knowing anything about the User, District, or Notification systems. The subscriber (`subscribers.py`) handles the cross-system orchestration.
**Next connection:** Auth ↔ Analytics (correlating login frequency with scenario simulation usage).
