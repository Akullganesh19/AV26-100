## 2024-11-09 — Auth ↔ Alerts Intelligence

**Systems connected:** Auth ↔ Alerts
**Intelligence emerged:** Users now receive alerts specifically tailored to their district assignments and personalized risk threshold settings. Before this, alerts were disconnected from user preferences.
**Data flows:** Alert data (disease, district, risk score) flows to the connection layer, which fetches User data (districts, email_alerts, alert_threshold) to determine who to notify.
**Coupling approach:** Event Bridge Pattern. The `alert_service` emits `alert.triggered` using a loosely coupled `EventBus`. The `alert_routing` connection module listens for this event, queries the database, and connects the alerts to specific users. Neither system imports the other.
**Next connection:** Errors ↔ Users (to proactively notify users when they encounter a known error).