## 2024-05-20 — Alerts ↔ Auth Notification Routing
**Systems connected:** Alerts ↔ Auth/Users
**Intelligence emerged:** Dynamic routing of mission alerts to specific officers based on their assigned districts, alert threshold settings, and email preferences.
**Data flows:** Alert system broadcasts an 'alert.triggered' event via the EventBus containing district and risk score. The subscriber pulls officer preferences from Auth/Users to dispatch personalized notifications.
**Coupling approach:** Event Bridge Pattern using an EventBus. The AlertService has no knowledge of Users, and Users do not depend on Alerts.
**Next connection:** Auth ↔ Analytics to track login frequency against feature engagement.
