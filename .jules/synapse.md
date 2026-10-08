## 2026-10-08 — Targeted Alert Dispatching
**Systems connected:** Alerts ↔ Auth (Users)
**Intelligence emerged:** Alerts are now dynamically routed only to officers responsible for the affected district who have a risk threshold matching the severity of the threat.
**Data flows:** Alerts domain emits `alert.triggered` with district and severity. Auth domain listens, maps the district to active users, filters by user threshold, and dispatches targeted notifications.
**Coupling approach:** Event Bridge Pattern (`EventBus`). Alert creation is entirely decoupled from user querying and notification logic.
**Next connection:** Errors ↔ Users (to alert users when they hit known bugs).
