## 2024-07-05 — Alerts to Targeted Users via EventBus
**Systems connected:** Alerts ↔ Users (Auth/Notifications)
**Intelligence emerged:** The platform now automatically notifies only the relevant officials responsible for a given district when an alert is triggered, respecting their email preferences and customized risk thresholds, rather than dispatching identical global alerts.
**Data flows:** Alerts System emits `alert.triggered` with district, disease, and risk score. User System listens, queries the `User` database for those linked to the district (`email_alerts=True` and `alert_threshold <= risk_score`), and triggers the Notifications system for those users.
**Coupling approach:** Event Bridge Pattern. An async `EventBus` (`app/core/events.py`) decouples the systems. The `AlertService` has no direct dependency on the `User` model or notification logic; it only emits the alert event.
**Next connection:** Errors ↔ Users (to inform engineers which user segments are hitting specific error patterns).
