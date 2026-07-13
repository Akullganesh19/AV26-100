## 2025-02-14 — Targeted Notification Dispatcher
**Systems connected:** Predictions & Alerts ↔ Users
**Intelligence emerged:** Proactive, targeted notifications for specific districts when risk crosses a user's defined threshold, avoiding alert fatigue.
**Data flows:** Alert metadata (alert_id, district_id, disease, risk_score) flows from prediction_service and alert_service into the targeted notification dispatcher, which evaluates user thresholds and sends alerts.
**Coupling approach:** Event Bus pattern (`event_bus.on` and `event_bus.emit`) decouple the alert generation from notification logic.
**Next connection:** Correlate user login frequency with feature usage to prioritize content for specific user roles.
