## 2024-05-18 — Alerts to Users
**Systems connected:** Alerts ↔ Users
**Intelligence emerged:** Proactive notification of high-risk users who track specific districts when outbreaks or clusters are detected in those districts.
**Data flows:** Alerts System emits 'alert.triggered' with district and risk details. Connection layer listens, cross-references with User preferences (thresholds and tracking) in the Users system, and pushes personalized notifications.
**Coupling approach:** Event Bridge pattern using an in-memory `EventBus`. `alert_service` emits events without importing user models. `synapse_connections` handles the logic bridging the two, keeping both systems isolated.
**Next connection:** Auth/User Behavior ↔ Content/Data (e.g., modifying which districts are shown on the dashboard based on user login frequency or feature usage).
