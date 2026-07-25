## 2024-05-30 — Clinical API ↔ Alert System
**Systems connected:** Analytics (Audit Logging) ↔ Alerts (Clinical Cluster Logic)
**Intelligence emerged:** The tactical alerting system is now instantly aware of every single high-risk clinical screening that happens in the application, enabling true real-time localized threat detection.
**Data flows:** Real-time push from `clinical.py` to `alert_listeners.py` (Clinical API -> Event Bus -> Alert Service).
**Coupling approach:** The clinical routes simply fire off a `clinical.screening.high_risk` event onto a shared `EventBus`. The API does not import `AlertService` or use `BackgroundTasks`. The `AlertService` listener asynchronously reacts in a completely decoupled manner.
**Next connection:** Auth ↔ Analytics (correlate user roles/locations to specific disease reporting patterns).
