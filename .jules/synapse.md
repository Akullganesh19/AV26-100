## 2024-05-18 — Alerts to Users
**Systems connected:** Alerts ↔ Users
**Intelligence emerged:** Users are proactively notified when alerts in their assigned districts exceed their personal, individualized alert thresholds.
**Data flows:** Alert metadata (district, disease, risk score) flows from the Alert System into the User Notification System, which combines it with Auth data (districts, alert_threshold).
**Coupling approach:** Event Bridge pattern (EventBus) ensures the AlertService does not directly import User or Notification services, keeping systems loosely coupled.
**Next connection:** Errors ↔ Users (to inform users when they hit known backend faults).
