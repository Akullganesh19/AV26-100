## 2024-05-24 — Alert Targeting Context Bridge
**Systems connected:** Auth System (User Profiles/Jurisdictions) ↔ Alert/Notification System
**Intelligence emerged:** Alerts are no longer noisy, district-blind broadcasts. They are precision-targeted only to the specific health officers assigned to the affected district, dynamically respecting their personalized risk tolerance thresholds.
**Data flows:** When the Alert System triggers an outbreak warning, it pulls jurisdiction (District IDs) and threshold settings (alert_threshold) from the Auth System's context to filter the recipient list.
**Coupling approach:** Enrichment Pattern. The core Alert System simply asks the `IntelligenceBridge` for a list of targeted officer contacts. The Auth/User models are queried without creating hard dependencies in the core alert evaluation logic.
**Next connection:** Correlating model explainability data (SHAP values) from predictions with specific clinical screening outcomes to find hidden localized drivers.
