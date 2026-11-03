## 2024-06-25 — Dynamic Alert Routing Intelligence
**Systems connected:** Auth/User System ↔ Alert/Monitoring System
**Intelligence emerged:** Tactical alerts are now dynamically routed only to users responsible for the affected district, whose personal risk thresholds are breached, and who have opted into email alerts.
**Data flows:** Alert threshold, district assignment, and email preferences flow from the User system into the Alert system's notification task to dynamically filter recipients.
**Coupling approach:** Loosely coupled via `AlertRoutingIntelligence` which queries the database within the alert task, avoiding direct dependencies between the core auth logic and alert generation logic.
**Next connection:** Correlate predictive model metrics with actual user actions (e.g. how often high-risk alerts lead to users acknowledging them).
