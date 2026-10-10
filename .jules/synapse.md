## 2024-10-10 — Targeted Alert Notifications
**Systems connected:** Alerts ↔ Users (Auth)
**Intelligence emerged:** Alerts can now selectively target users based on their active district associations and customized alert thresholds instead of broad generic dispatching.
**Data flows:** Alerts emit events; EventBus routes to Subscribers; Subscribers query User system to dispatch specific notifications via Tasks.
**Coupling approach:** Event Bridge Pattern. Alert service just publishes an event, unaware of the subscriber querying the database for specific users.
**Next connection:** Errors ↔ Users (to inform users when they hit known bugs).
