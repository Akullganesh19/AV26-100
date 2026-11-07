## 2024-11-20 — Alert Notification Intelligence
**Systems connected:** Alerts ↔ Users/Notifications
**Intelligence emerged:** Proactive notification. The Alert system knows when a new tactical threat or clinical cluster triggers, and the User system knows which users are registered to monitor which districts and what their custom risk thresholds are. Connecting them ensures critical events proactively reach the right people via email immediately.
**Data flows:** Alerts System emits the new alert data (district, disease, risk score). A background connection task fetches the users assigned to that district who have enabled email alerts and have an alert_threshold <= the alert's risk score. It then fires off emails via the IntegrationService.
**Coupling approach:** Event Enrichment Pattern. I'm adding a detached, fire-and-forget notification correlation task that gets scheduled automatically right after a new alert is committed. The core alert evaluation logic doesn't wait for email delivery, and if emails fail, the alert still persists safely.
**Next connection:** Errors ↔ Users (to surface errors specifically to affected user segments).
