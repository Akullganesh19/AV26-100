## 2024-05-24 — User-Targeted Threshold Alerts
**Systems connected:** Auth/User ↔ Alerts/Notifications
**Intelligence emerged:** Notifications are now targeted based on user preferences (email_alerts) and their individual alert thresholds for specific districts.
**Data flows:** Alert generation checks the User database to find relevant personnel instead of just broadcasting.
**Coupling approach:** The alerts module independently queries the User/District association when an alert is triggered.
**Next connection:** Errors ↔ Users
