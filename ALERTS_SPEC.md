# EpiSense Tactical Alerts: Functional Specification (v1.0)

## 1. Objective
Enable health command officers to respond to immediate regional threats identified by the autonomous monitoring system and verified by clinical screening spikes.

## 2. Trigger Logic
An alert is generated in the `alerts` table when any of the following conditions are met:

### A. Autonomous Outbreak Trigger (Priority: High)
*   **Source**: `PredictionService.predict_all()`
*   **Condition**: A district's `risk_score` for any monitored disease exceeds the `ALERT_THRESHOLD` (default: 70).
*   **Action**: Generate a `SYSTEM_AUTO` alert for that district.

### B. Clinical Cluster Trigger (Priority: Critical)
*   **Source**: `PredictionAuditLog`
*   **Condition**: >5 individual clinical screenings in a single district return `risk_tier: HIGH` within a rolling 24-hour window.
*   **Action**: Generate a `CLINICAL_CLUSTER` alert. This signals a potential localized surge.

### C. Environmental Anomaly Trigger (Priority: Medium)
*   **Source**: `EnvironmentalData`
*   **Condition**: Extreme weather events (e.g., rainfall > 150mm in 24h) in districts with a high baseline risk for vector-borne diseases.
*   **Action**: Generate an `ENVIRONMENTAL_PROTECTION` alert.

## 3. Workflow & Persistence
*   **Persistence**: Alerts are saved to the PostgreSQL `alerts` table with a `severity` (Critical, High, Medium, Low) and `status` (Open, Acknowledged, Resolved).
*   **Persistence Strategy**: The background task `monitoring.py` runs every 4 hours to evaluate these triggers and commit new alerts.
*   **Resolution**: Officers must manually set alerts to `RESOLVED` after intervention, which archives the alert but keeps it in the audit trail.
*   **Frontend**: The "Tactical Alerts" page will use TanStack Query to poll for new alerts and provide an "Acknowledge" button to update status.
