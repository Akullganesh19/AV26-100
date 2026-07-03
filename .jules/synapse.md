## 2024-05-24 — Alert Personalization Bridge
**Systems connected:** Alerts ↔ Auth (Users)
**Intelligence emerged:** Dynamically route critical medical/epidemiological alerts only to officers assigned to the affected district who have configured a threat tolerance at or below the alert's severity score. Prevents alert fatigue and ensures the right people are paged.
**Data flows:** Alert system emits an event (`alert.triggered`) with threat data -> Auth system intercepts the event, queries the user-district cross-reference table and personal thresholds -> Notification system dispatches personalized emails.
**Coupling approach:** Asynchronous, in-memory `EventBus`. The alert generation logic (`PredictionService`, `AlertService`) has zero dependency on or knowledge of the `User` models or routing logic. The subscriber handles the correlation in a background task.
**Next connection:** Errors ↔ Users (to proactively notify users when they hit known bugs).
