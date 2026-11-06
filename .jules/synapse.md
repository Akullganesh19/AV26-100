## 2024-06-25 — Targeted Officer Notifications
**Systems connected:** Analytics (Prediction/Alert Service) ↔ Users (Auth)
**Intelligence emerged:** Tactical alerts are now specifically routed to officers assigned to the affected district whose personal alert threshold is breached, rather than spamming a generic "Jurisdiction Monitor".
**Data flows:** Alerts emit `alert.triggered` event (System A) -> Notification Subscriber joins `District` and `User` to filter based on `email_alerts` and `alert_threshold` (System B).
**Coupling approach:** Event Bus pattern (`app.core.events`). Neither PredictionService nor AlertService knows about User settings.
**Next connection:** System logs ↔ Performance monitoring to detect slowly degrading models before they trigger errors.
