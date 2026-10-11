## 2024-10-12 — Targeted Outbreak Notifications
**Systems connected:** Predictions/Alerts ↔ Auth/Users
**Intelligence emerged:** The system now selectively alerts health officials who are specifically assigned to the affected district and whose personal risk threshold is exceeded, preventing alert fatigue.
**Data flows:** Predictions system publishes 'prediction.high_risk'. Notification system queries User system for district assignments and thresholds, then dispatches targeted alerts.
**Coupling approach:** Event Bridge Pattern. Systems do not import each other. `EventBus` passes primitive values.
**Next connection:** Errors ↔ Users (to proactively notify users when they hit known bugs).
