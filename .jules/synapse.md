## 2024-05-20 — Intelligent Alert Routing
**Systems connected:** Alerts ↔ Auth/Users
**Intelligence emerged:** Localized outbreak alerts are now dynamically routed only to the subscribed health officers responsible for the affected district, respecting their personal risk thresholds.
**Data flows:** `alert.created` event flows from AlertService to the Routing Subscriber, which pulls User/District associations and thresholds from the Auth system.
**Coupling approach:** Event Bridge Pattern. AlertService only emits an event. The subscriber handles the cross-system query independently.
**Next connection:** Correlate user login frequency with clinical model utilization.
