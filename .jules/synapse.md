## 2024-10-31 — Smart Alert Routing Connection
**Systems connected:** Auth ↔ Alerts
**Intelligence emerged:** Alerts are now intelligently routed only to users assigned to the affected district who have opted in and whose personal risk threshold is met, reducing alert fatigue.
**Data flows:** Alert data (disease, risk_score, district_id) flows from the Prediction/Alert systems to the EventBus. The Auth system's user preferences (district assignments, email_alerts, alert_threshold) intercept this flow to determine notification targets, outputting filtered lists to the Notification dispatch.
**Coupling approach:** Event Bus (`EventBus`). The Alert and Prediction services simply emit an `alert.triggered` event. They do not know about users or thresholds. The `synapse_bridge` handles the DB queries and logic to connect the two.
**Next connection:** Errors ↔ Users (correlate error logs with user segments to notify users of known bugs).
