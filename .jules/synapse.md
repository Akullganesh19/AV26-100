## 2024-05-18 — Alert-User Targeting Connection
**Systems connected:** Alerts ↔ Users
**Intelligence emerged:** Dynamic notification routing based on user territory and personal risk tolerance. Instead of blindly logging alerts, the system knows exactly which officers cover the affected district and filters by their custom alert_threshold setting.
**Data flows:** Alert risk scores flow into the User notification system, filtered by the user's `email_alerts` and `alert_threshold` preferences.
**Coupling approach:** Event Bridge Pattern. The prediction service emits a background task with context (`district_id`, `risk_score`). The `alerts` task locally fetches `Users` without modifying `PredictionService` or `User` core logic.
**Next connection:** Errors ↔ Users (to notify users proactively if they hit a known bug)
