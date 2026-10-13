## 2023-10-25 — Targeted Alert Notifications
**Systems connected:** Auth (Users) ↔ Alerts (Predictions)
**Intelligence emerged:** Alerts are now routed dynamically to specific officers based on their assigned districts and personal risk thresholds, eliminating generic broadcast spam.
**Data flows:** Alerts system emits `alert.triggered` with district risk details. The Auth system (via a subscriber) reads user profiles, matches districts/thresholds, and dispatches personalized notifications.
**Coupling approach:** Event Bridge Pattern. Introduced `EventBus` (`app/core/events.py`). `PredictionService` emits the event; `subscribers.py` handles the auth-data join, ensuring loose coupling and no direct cross-system imports.
**Next connection:** Correlate user login frequency with feature usage.