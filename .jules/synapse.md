## 2026-10-03 — Alert Personalization Bridge
**Systems connected:** Predictions/Alerts ↔ Auth/User Preferences
**Intelligence emerged:** Users now only receive outbreak alerts for districts they care about, and only if the risk score crosses their personal threshold. We bridge the gap between static predictions and personal user preferences.
**Data flows:** Prediction engine publishes 'prediction.high_risk' events. Intelligence bridge consumes them, queries the District/User graph, and dispatches personalized email alerts.
**Coupling approach:** Event Bus pattern. Prediction Service has zero knowledge of Users. The Bridge handles the mapping.
**Next connection:** Correlating User activity metrics with specific Scenario interactions.
