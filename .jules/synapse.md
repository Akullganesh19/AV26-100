
## 2026-06-17 — Alert Dispatch
**Systems connected:** Alert Service ↔ Auth / User Service
**Intelligence emerged:** Health command officers now automatically receive email notifications for highly critical disease outbreak predictions that specifically affect the districts they monitor, filtered by their personal alert thresholds and preferences.
**Data flows:** Alert metadata (Risk Score, Disease, District) flows from the Alert System into an Event Bus. The new Alert Dispatch service listens to this event, queries the Auth System for users assigned to that District, cross-references their alert thresholds, and invokes the Integration System to send targeted emails.
**Coupling approach:** Event Bridge Pattern. The `AlertService` and `PredictionService` no longer import email dependencies directly; they simply emit an `alert.triggered` event with an ID to a newly created decoupled EventBus.
**Next connection:** We could integrate Monitoring (DLQ depth) ↔ Error Logs, connecting tasks stuck in dead letters directly to the exception tracking system.
