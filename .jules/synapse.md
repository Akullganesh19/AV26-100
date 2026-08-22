## 2025-02-27 — Alert ↔ User Notification Routing
**Systems connected:** Alerts ↔ Users
**Intelligence emerged:** The system now automatically routes clinical and autonomous alerts to the specific users assigned to the affected districts, if the alert's risk score exceeds their personalized threshold.
**Data flows:** Alerts (from `alert_service`) → `event_bus` (`alert.triggered`) → `alert_routing` → Filters by `User.districts` and `User.alert_threshold` → Notification System (`send_alert_notification`).
**Coupling approach:** Loosely coupled via `EventBus`. The `AlertService` just emits an `alert.triggered` event. The `alert_routing` intelligence layer listens to it and handles the cross-referencing with the `User` system.
**Next connection:** Errors ↔ Users (Proactive notification when a user hits a known bug).
