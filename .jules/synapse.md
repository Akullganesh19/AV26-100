## 2026-06-28 — Alerts ↔ Users
**Systems connected:** Alerts ↔ Users
**Intelligence emerged:** Proactive notification of health officials based on their risk tolerance and assigned district when an autonomous outbreak or clinical cluster occurs.
**Data flows:** Triggered alert events flow to an event bus. Subscribers fetch the user assignments for that district and email users whose alert_threshold is surpassed by the alert's risk_score.
**Coupling approach:** Extremely loose. The Alert model merely fires an event via `EventBus` on the SQLAlchemy `after_insert` hook. A standalone subscriber listens to this event, queries the user/district relationships, and invokes the integration service, keeping Alert and User modules completely isolated from one another.
**Next connection:** Errors ↔ Users (to proactively notify users when they encounter a known system bug).
