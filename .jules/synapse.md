## 2025-02-27 — [Predictions ↔ User Alerts]
**Systems connected:** Predictions (Epidemiological modeling) ↔ Auth (User preferences and district subscriptions)
**Intelligence emerged:** The system now automatically routes personalized, proactive, high-risk disease outbreak alerts to subscribed users based on their specific jurisdiction and custom alert threshold, instead of relying solely on generic alerts.
**Data flows:** Prediction risk scores and disease details flow from the ML pipeline to the event bus, where they are evaluated against User models (alert preferences and district assignments) to dispatch targeted notifications.
**Coupling approach:** Event Bridge Pattern. The prediction service only emits a `prediction.high_risk` event onto the centralized `event_bus` and does not import the notification routing logic. The `alert_routing` listener handles the db queries and targeted task dispatch independently.
**Next connection:** Correlate user search or viewed dashboard metrics with model confidence/uncertainty indicators to display tailored contextual tooltips.
