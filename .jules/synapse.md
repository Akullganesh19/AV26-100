## 2024-06-30 — Alerts ↔ User Notifications (Tactical Intelligence)
**Systems connected:** Alert Generation ↔ User Management/Notifications
**Intelligence emerged:** The platform now proactively notifies authorized users in a specific district when a critical health alert is triggered, utilizing existing data from the Alert model, the District mapping, and User preference (`email_alerts`).
**Data flows:** Alert data (ID, disease, risk score) triggers an event -> The EventBus publishes it -> The subscriber queries the DB for `User`s tied to that `district_id` with `email_alerts=True` -> The `IntegrationService` dispatches emails to those users.
**Coupling approach:** Event Bridge Pattern. The `Alert` model has an SQLAlchemy `after_insert` hook that publishes an event to an in-memory `EventBus`. The models know nothing about notifications. The subscriber acts as the translation layer, executing independently.
**Next connection:** Correlate user login frequency / audit logs with prediction models to surface high-usage districts.
