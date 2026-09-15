## 2024-05-24 — Targeted Alert Routing
**Systems connected:** Alerts ↔ Auth (Users)
**Intelligence emerged:** Alerts are now routed only to the specific officers responsible for the affected district and who meet the risk threshold, rather than broadcasting blindly.
**Data flows:** Alert risk score & district name flow to User mapping to find matching personnel.
**Coupling approach:** Loosely coupled at the notification dispatch layer (tasks/alerts.py) using raw SQL `text()` queries. Neither core AlertService nor Auth routes import each other directly.
**Next connection:** Analytics ↔ User Behavior
