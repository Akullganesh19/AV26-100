## 2024-05-30 — Targeted Alert Notifications
**Systems connected:** Alerts ↔ Auth (Users)
**Intelligence emerged:** Alerts are now intelligently routed to specific health officials responsible for the affected district, rather than broadcasting generic alerts. Users only receive alerts that meet their personalized `alert_threshold` and if they have opted into `email_alerts`.
**Data flows:** `AlertService` creates an alert and emits an `alert.triggered` event to the `EventBus`. The `notification_dispatcher` listens to this event, queries the database for active users linked to the alert's `district_id`, checks their individual threshold/preference settings, and conditionally routes the notification.
**Coupling approach:** Event Bridge pattern using a lightweight, central `EventBus`. Neither the Alerts system nor the Auth system imports or knows about each other. The `notification_dispatcher` acts as the decoupled bridge.
**Next connection:** Predict feature flags from User usage tier.
