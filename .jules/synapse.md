## 2024-11-04 — Alert-Auth Personalization
**Systems connected:** Alerts ↔ Auth
**Intelligence emerged:** Alerts are now selectively delivered based on a user's customized risk threshold and assigned district, rather than generically blasting everyone or solely relying on logs.
**Data flows:** Alerts emit `alert.triggered` event with district & score. Event listener reads User config & User-District mapping to filter recipients, pushing targeted emails.
**Coupling approach:** Event Bridge pattern (using `EventBus`). The Alert service simply emits an event; it doesn't know about Users. The listener fetches Auth data independently.
**Next connection:** Errors ↔ Users (to surface error occurrences on user dashboards)
