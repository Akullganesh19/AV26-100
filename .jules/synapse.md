## 2026-10-05 — Targeted Alert Dispatching
**Systems connected:** Alert Generation ↔ User Notification Preferences
**Intelligence emerged:** Alerts are routed to only those users assigned to the affected district whose risk threshold matches the alert severity.
**Data flows:** New alerts trigger a query against user districts and preferences, filtering notifications.
**Coupling approach:** The `notification_dispatcher` service acts as an event listener, loosely coupled and not impacting the core alert generation logic.
**Next connection:** Link User Behaviour to Map Rendering
