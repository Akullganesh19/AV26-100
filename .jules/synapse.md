## 2024-05-24 — Alert Routing Bridge
**Systems connected:** Analytics/Predictions ↔ Auth/Users
**Intelligence emerged:** High-risk predictions are now intelligently routed only to active users assigned to the affected district whose personal alert threshold is exceeded by the prediction's risk score.
**Data flows:** Prediction risk scores and district data flow from the Analytics system to the User system to filter and notify relevant users.
**Coupling approach:** Loosely coupled using an Event Bus (`prediction.high_risk`). The `PredictionService` simply emits an event, and the `alert_routing` module listens, fetches user data, and dispatches notifications.
**Next connection:** Errors ↔ Users (Proactive error notifications for affected users).
