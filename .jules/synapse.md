## 2024-05-18 — Alerts to Users Email Subscriptions
**Systems connected:** Alerts ↔ Users (Auth)
**Intelligence emerged:** Alerts are now proactively routed to users based on their district assignment and threshold preferences, transforming passive monitoring into active notifications.
**Data flows:** Alert data (disease, risk_score) moves from the Alerts system, is correlated with user assignment data in the Auth system, and flows out to the Notifications system.
**Coupling approach:** A loosely coupled `dispatch_district_alert_emails` EventBridge uses a raw SQL `text()` query to look up user data without importing User models into the Alerts service, preserving boundary separation.
**Next connection:** Errors ↔ Users (to proactively notify users when they hit known bugs).
