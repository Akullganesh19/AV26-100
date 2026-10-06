## 2026-10-06 — Targeted Alerting Neural Pathway
**Systems connected:** Users & Auth ↔ Alerts & Notifications
**Intelligence emerged:** Dynamic routing of mission alerts. Instead of spamming all officers, alerts are surgically dispatched only to users assigned to the affected district whose personal `alert_threshold` permits it.
**Data flows:** Alert Engine → District ID + Risk Score → User Directory → Filter by Threshold → Notification Dispatch.
**Coupling approach:** Loosely coupled event-bridge style background task `dispatch_targeted_alerts` attached to the alert emission points. Alert generation itself is not blocked by user directory lookups.
**Next connection:** Correlating environmental anomaly data with clinical prediction variance to flag Out of Distribution feature drifts.
