## 2024-06-25 — Alert Targeting Intelligence
**Systems connected:** Alerts ↔ Auth/Users
**Intelligence emerged:** Proactive, user-specific alert targeting. Instead of all alerts going nowhere or everywhere, users only get notified about new alerts in districts they explicitly monitor (via `user_districts`), and only if the risk score crosses their personal `alert_threshold` preference.
**Data flows:** Alerts system generates an `Alert` -> `alert.created` event -> Synapse queries User preferences and `user_districts` -> Triggers targeted notifications.
**Coupling approach:** EventBus (`app/core/events.py`) pub/sub. The `Alert` model merely emits an event `after_insert`. The core routing intelligence lives in `app/synapse/alert_routing.py` where it bridges the User and Alert domains. Neither domain imports the other directly for logic.
**Next connection:** Correlate user login frequency with their configured alert thresholds to identify disengaged but highly-alerted jurisdictions.
