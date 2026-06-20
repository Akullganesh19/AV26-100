## 2024-06-20 — Alert Targeting via Cross-System Join
**Systems connected:** Alerting ↔ User/Auth
**Intelligence emerged:** Selectively routing alerts to the specific health officers responsible for the affected district, respecting their personal sensitivity thresholds, rather than spamming a global channel.
**Data flows:** Alert system emits `alert.triggered` and `prediction.high_risk`. Alert handler subscribes, queries Auth system for Users assigned to `district_id`, and checks `alert_threshold`.
**Coupling approach:** Pub-Sub via lightweight in-memory `EventBus`. Alert/Prediction services don't import Auth or Notification services.
**Next connection:** Feed user engagement metrics back into the simulation scenarios (Usage ↔ Features).
