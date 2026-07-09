## 2025-02-18 — Alert Target Optimization
**Systems connected:** Analytics (PredictionService) ↔ Users (User, User Preferences)
**Intelligence emerged:** The platform can now route alerts directly and specifically to the users assigned to the affected district whose risk thresholds are exceeded by the alert's risk score. Previously, alerts were fired blindly.
**Data flows:** Prediction risk scores and district assignments move from the ML pipeline into the user management space.
**Coupling approach:** Event Bridge Pattern via `EventBus`. `PredictionService` emits `alert.triggered`. Subscribers listen and orchestrate user queries.
**Next connection:** Correlate user simulation history with real-world outbreak occurrences to evaluate training efficacy.
