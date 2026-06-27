## 2025-02-28 — Event-Driven Alert Notifications
**Systems connected:** Alert System ↔ Auth System (User Preferences) ↔ Notification System
**Intelligence emerged:** The Notification System now knows exactly who to alert when a disease outbreak happens. By listening for the `alert.created` event, it cross-references the alert's location and severity against User profile settings (`alert_threshold`, `email_alerts`, and geographic association) to dispatch personalized targeted warnings instead of generic logs.
**Data flows:** Alert System publishes `alert.created` to `EventBus` -> Subscriber queries `Auth` system for Users mapping to the district with threshold > risk_score -> Subscriber dispatches precise email notifications via Tasks.
**Coupling approach:** Fully decoupled via an asynchronous in-memory `EventBus`. The Alert System has zero knowledge of the User profiles or Notification System, and the `after_insert` hook fires without blocking the transaction.
**Next connection:** Connect System Errors/Logs to Analytics to track how often specific User Segments encounter degradation.
