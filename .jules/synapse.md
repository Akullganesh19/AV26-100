## 2024-07-10 — Targeted User Alerts
**Systems connected:** Prediction ML ↔ User Preferences (via Notifications)
**Intelligence emerged:** The application can now deliver critical outbreak alerts only to specific users who want them, based on their jurisdiction (District) and personalized alert threshold, rather than broad generic blasts.
**Data flows:** High-risk prediction alerts flow from `PredictionService` into an `EventBus`, which a subscriber (`notify_users_of_alert`) receives. It queries the `User` and `District` tables to filter users and triggers targeted `send_alert_notification` dispatches containing the exact user emails.
**Coupling approach:** Event Bridge Pattern. The ML inference engine knows nothing about users or notifications; it just emits an event. The notification system now supports targeted emails but provides a generic fallback. The `EventBus` manages the pub/sub connection.
**Next connection:** System Analytics ↔ User Error Rates (Mapping API error rates/logs directly to user session contexts).
