## 2025-02-27 — Targeted Alert Notifications
**Systems connected:** Auth/User ↔ Alerts/Notifications
**Intelligence emerged:** The platform can now dispatch critical outbreak alerts only to users associated with the impacted district and who have their alert threshold exceeded, rather than generating generic, broadcast-style alerts for "Jurisdiction Monitor".
**Data flows:** `PredictionService` and `AlertService` emit `alert.triggered` events containing `district_id` and `risk_score`. A listener in `AlertService` maps the `district_id` to matching `User` instances (from the Auth system) via the `user_districts` relationship to calculate target audiences.
**Coupling approach:** Event Bridge Pattern. A lightweight Pub/Sub `EventBus` connects the two systems. Neither `PredictionService` nor the core of `AlertService` directly import the User model for routing.
**Next connection:** Errors ↔ Users (e.g., proactive user notification upon repeated failing screens/diagnostics).
