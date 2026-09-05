## 2024-05-24 — Intelligent Alert Routing
**Systems connected:** Alerts ↔ Users
**Intelligence emerged:** Autonomous outbreak alerts now directly notify only the specific officers assigned to the affected district, filtering out noise by respecting their individual risk score alert thresholds.
**Data flows:** Alert parameters (risk score, district) flow to User preferences (district assignment, alert threshold) to generate a targeted recipient list.
**Coupling approach:** A thin routing service layer (`route_alert_to_officers`) queries the `users` and `user_districts` tables via raw SQL within a transient DB session from the background `send_alert_notification` task.
**Next connection:** Correlate user clinical screening patterns with outbreak alerts to proactively warn at-risk patient cohorts.
