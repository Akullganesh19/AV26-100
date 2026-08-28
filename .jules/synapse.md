## 2024-05-24 — Alert Routing
**Systems connected:** Alerts ↔ Users
**Intelligence emerged:** Proactive notification of health officials based on their assigned districts and personalized risk thresholds when automated alerts trigger.
**Data flows:** Alert system emits `alert.triggered`. Notification service listens, queries User system for officers assigned to the alert's district, filters by threshold, and routes personalized notifications.
**Coupling approach:** Event Bus. Alert creation and Notification routing are entirely decoupled. If notifications fail, alerts still persist.
**Next connection:** Predictive Risk ↔ Resource Allocation (Logs)
