## 2024-05-24 — Alert-to-User Notification Bridge
**Systems connected:** Alerts ↔ Auth/Users
**Intelligence emerged:** Alerts system now talks to Auth/Users to route notifications only to users monitoring the affected district, with email alerts enabled, and whose customized alert threshold has been breached.
**Data flows:** Alerts (Alert ID, District, Disease, Risk Score) → Auth/Users (filtering by threshold and settings) → Notification Dispatch
**Coupling approach:** Event Bus Pattern (completely loosely coupled). Neither system directly imports the other.
**Next connection:** Errors ↔ Users (to proactively notify users when they hit known bugs).
