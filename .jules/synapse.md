## 2024-05-24 — User-Targeted Alert Routing
**Systems connected:** Auth/User Preferences ↔ Alert Notification Dispatch
**Intelligence emerged:** Alerts are no longer broadcast blindly. They are dynamically routed to health officers who are explicitly assigned to the affected district and whose personalized alert thresholds are breached, preventing alert fatigue and targeting response.
**Data flows:** User district assignments and alert thresholds flow from Auth to the Alert dispatch task during runtime to filter the recipient list.
**Coupling approach:** Enrichment Pattern. The Alert system does not import Auth logic or models. The notification task dynamically queries the `users` and `user_districts` tables using raw SQL when an alert fires, keeping the systems strictly decoupled at the code level.
**Next connection:** Correlate prediction error rates with telemetry logs to identify models degrading in specific regions.
