## 2024-11-05 — Alert Dispatch ↔ User Targeting
**Systems connected:** Auth/Users ↔ Alerts/Notifications
**Intelligence emerged:** Alerts are now proactively dispatched only to health officers specifically assigned to the threatened district, who have email alerts enabled and whose configured alert threshold is met by the outbreak risk score.
**Data flows:** Alerts System queries User Context (assignments, thresholds, preferences) using the district ID and risk score.
**Coupling approach:** Enrichment Pattern. The notification task dynamically queries the database for user context before dispatching, avoiding direct coupling between the prediction engine and the user management system.
**Next connection:** User Behavior ↔ Tactical Dashboards (to prioritize diseases they interact with most).
