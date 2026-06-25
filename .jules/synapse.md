## 2024-06-25 — Alerts ↔ Notifications
**Systems connected:** Alerts ↔ Notifications (Users/Integration)
**Intelligence emerged:** Autonomous and tactical outbreak alerts are now proactively routed to users who oversee the affected district and have a risk threshold exceeded by the alert score.
**Data flows:** Alert metadata (district, disease, risk score) flows out from the database transaction boundary into the asynchronous event bus, which then queries user profiles to dispatch targeted emails.
**Coupling approach:** Event Bus Pattern. The `Alert` model simply publishes an `alert.triggered` event via an SQLAlchemy `after_insert` hook. An isolated subscriber function processes this event asynchronously, keeping the core alerting logic completely decoupled from user preferences and third-party integrations (SendGrid).
**Next connection:** Errors ↔ Users (Notifying users when they encounter a known system error cluster).
