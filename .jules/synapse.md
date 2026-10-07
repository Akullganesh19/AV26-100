## 2026-10-07 — Alert Officer Routing
**Systems connected:** Alerts ↔ Users/Auth
**Intelligence emerged:** Alerts are no longer blindly broadcasted. The system now knows which health officers are assigned to the district where the alert originated, what their personal risk threshold is, and whether they prefer email notifications. Alerts are dynamically routed to the exact individuals responsible for that threat level in that region.
**Data flows:** Alerts System emits `alert.triggered` event → EventBus → Synapse Routing Layer queries Auth System (Users/Districts) → dispatches targeted Notifications.
**Coupling approach:** Event Bridge Pattern. The Alerts service simply announces that an alert was created. The Synapse connection layer (an isolated background listener) independently queries the User/District mapping to fan out the notifications. Neither core system imports the other.
**Next connection:** Errors ↔ Users (to proactively notify users when they hit known bugs).
