## 2024-05-24 — Targeted Alert Delivery
**Systems connected:** Analytics/Prediction ↔ Auth/User
**Intelligence emerged:** Cross-referencing autonomous and clinical health alerts with user profiles to selectively trigger targeted alerts based on user's district assignment and alert threshold instead of a generic system-wide notification.
**Data flows:** Alert metadata (alert_id, district_id, disease, risk_score) flows from Alert/Prediction Service -> Event Bus -> Subscriber. The Subscriber queries the Auth/User database and dispatches targeted emails through the Notification Service.
**Coupling approach:** Event Bus (`app/core/events.py`). Neither `alert_service` nor `prediction_service` knows about users, they just publish an `alert.triggered` or `prediction.high_risk` event. The subscriber coordinates the systems.
**Next connection:** Errors ↔ Users (to automatically notify users when a recurring bug affects their session).
