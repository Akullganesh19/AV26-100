## 2024-07-04 — Autonomous Risk Alert Targeting
**Systems connected:** Prediction (Analytics) ↔ Users (Auth) ↔ Alerts (Notification)
**Intelligence emerged:** The platform now sends targeted, personalized high-risk outbreak alerts strictly to the specific health officials responsible for that district, provided the risk exceeds their personal threshold and they have opted in. Previously, alerts were generic and untargeted ("Jurisdiction Monitor").
**Data flows:** Prediction emits `prediction.high_risk` event with `district_id`. The Subscriber layer catches it, queries the User system via the `user_districts` relationship to find active officials matching the threshold criteria, and dispatches individual notifications to the Alert system.
**Coupling approach:** Event Bus pattern (`EventBus`). The Prediction Service (`PredictionService`) simply emits an event and knows nothing about the User system or how alerts are dispatched. The subscriber logic handles the orchestration independently.
**Next connection:** Correlate user login/session activity with alert acknowledgement times to predict system engagement or measure alert fatigue.
