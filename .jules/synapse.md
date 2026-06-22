## 2024-05-28 — Alert Threshold Notifications
**Systems connected:** Alerts ↔ Users
**Intelligence emerged:** Proactive matching of mission-critical alerts to relevant officers based on assigned districts and personal risk tolerance.
**Data flows:** Alerts.inserted -> EventBus -> Users.filtered -> Alerts.send_notification
**Coupling approach:** SQLAlchemy event listener publishes to an asynchronous EventBus. No direct imports exist between AlertService and the User models/Notification tasks.
**Next connection:** Correlate user login frequency with report generation to identify tactical engagement patterns.
