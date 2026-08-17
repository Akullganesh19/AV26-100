## 2024-06-25 — Alert Routing
**Systems connected:** Predictions ↔ Users/Auth
**Intelligence emerged:** High-risk predictions now automatically route alerts only to the specific officers assigned to the affected district, respecting their personal alert thresholds.
**Data flows:** Predictions emit `prediction.high_risk`. Alert Routing queries `User` and `District` relationships to filter targets, then forwards to the notification system.
**Coupling approach:** Event Bus (`app.core.events`). Prediction system doesn't know about users, and user system doesn't know about predictions.
**Next connection:** Errors ↔ Users (Proactive notification of bugs to affected users).
