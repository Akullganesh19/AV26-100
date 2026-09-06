## 2024-05-30 — Targeted Alert Notifications
**Systems connected:** Alerts ↔ Auth/Users
**Intelligence emerged:** Notifications are now intelligently routed only to officers assigned to the affected district whose personal `alert_threshold` is exceeded by the risk score.
**Data flows:** `AlertService` emits an `alert.triggered` event to a decoupled Event Bus. A Synapse listener queries Auth/User data for the district and thresholds to fan out precise notifications.
**Coupling approach:** Event Bridge Pattern. The `AlertService` has zero knowledge of `User` models or routing logic, it just emits a system event. The Auth system is undisturbed.
**Next connection:** Correlate user login frequency with their interaction on the tactical alerts page.
