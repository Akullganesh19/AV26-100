## 2024-11-20 — Intelligent Alert Routing
**Systems connected:** Auth (Users/Districts) ↔ Alerts (Notifications)
**Intelligence emerged:** Alerts are now intelligently routed only to the specific health officers responsible for the affected district, filtering out those whose personal risk thresholds are higher than the incident's score.
**Data flows:** Auth context (officer districts, active status, alert preferences, and risk thresholds) flows into the prediction service and is passed as targeted metadata to the alert notification system.
**Coupling approach:** The `synapse_bridge.py` isolates the database queries, maintaining loose coupling. `PredictionService` calls this bridge to enrich the payload sent to `send_alert_notification` in `alerts.py`. Neither the Auth nor the Alert core logic imports each other directly.
**Next connection:** Errors ↔ Users (Proactively notify users when they hit known bugs).
