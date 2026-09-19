## 2024-05-24 — Alert Notification Bridge
**Systems connected:** Alerts ↔ Users
**Intelligence emerged:** Users proactively receive an email alert based on their assigned districts when an outbreak risk score exceeds their configured threshold.
**Data flows:** AlertService emits 'alert.triggered', Synapse Bridge intercepts it, queries users assigned to that district, and triggers emails.
**Coupling approach:** EventBus Pattern (pub/sub). AlertService doesn't import User models.
**Next connection:** Errors ↔ Users
