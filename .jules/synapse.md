## 2025-05-18 — Alert Target Synchronization
**Systems connected:** Alerts ↔ Users
**Intelligence emerged:** When a new high-risk epidemiological alert or clinical cluster is detected, the system now automatically finds and notifies only the relevant health officers assigned to that specific district, respecting their personal alert threshold settings and email preferences.
**Data flows:** Alerts System publishes `alert.created` events → Event Bus routes to Notification Dispatch → Dispatch queries User System (joining Users to Districts) → Personalized notifications are sent via Email.
**Coupling approach:** An asynchronous Event Bus (`backend/app/core/events.py`) keeps the systems decoupled. The `AlertService` emits generic events, and `handle_alert_created` in the dispatch layer handles the inter-system logic. Neither system directly imports or depends on the other.
**Next connection:** Errors ↔ Users (to notify affected users when they hit a known bug)