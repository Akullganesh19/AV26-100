## 2023-10-24 — Alerts to Targeted Users
**Systems connected:** Alerts ↔ Auth/Users
**Intelligence emerged:** When a new outbreak alert triggers, it's not just stored or generically logged. We route it intelligently only to users configured to watch that district who have requested email alerts and whose alert_threshold is exceeded by the threat level.
**Data flows:** Alerts system emits `alert.triggered` event (containing district and risk score) → Users system catches it, queries user preferences → Notification tasks dispatched individually.
**Coupling approach:** Event Bridge Pattern (`EventBus`). Neither system imports the other.
**Next connection:** Auth ↔ Logs (correlate error rates with specific user segments).
