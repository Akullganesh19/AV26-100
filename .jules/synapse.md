## 2024-11-01 — Targeted Alert Routing
**Systems connected:** Auth ↔ Alerts
**Intelligence emerged:** Alerts can now be routed proactively to specific users who care about specific districts, rather than relying on users to check dashboards or using a global threshold.
**Data flows:** Auth (user threshold and district associations) informs Alerts (where to route the notification).
**Coupling approach:** A lightweight async EventBus decoupled the systems. Alerts emits "alert.triggered", and a listener queries Auth data to route it.
**Next connection:** Errors ↔ Auth (to track which users encounter the most pipeline failures).
