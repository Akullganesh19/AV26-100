## 2024-10-17 — Prediction Alerts ↔ User Notification System
**Systems connected:** PredictionService ↔ Auth/Users
**Intelligence emerged:** Dynamic, targeted alert routing instead of generic broadcasting, respecting user-specific risk thresholds and district assignments.
**Data flows:** Risk scores from PredictionService flow to Alert Dispatch via EventBus, which then cross-references District relationships and User threshold data to emit personalized alerts.
**Coupling approach:** Event Bridge Pattern. PredictionService publishes an event via `EventBus`, and an independent subscriber maps it to Users.
**Next connection:** Errors ↔ Users (to alert users experiencing systemic errors).
