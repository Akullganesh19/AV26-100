## 2024-06-25 — Targeted Alert Notifications
**Systems connected:** Alert System ↔ Auth System
**Intelligence emerged:** Alerts are now proactively dispatched to users based on their specific district assignments and personal risk score thresholds, rather than simply logging alerts into a void or spamming all users.
**Data flows:** When an alert triggers, the `synapse_bridge` pulls the `district_id` and queries the Auth system for users associated with that district who have `email_alerts` enabled and an `alert_threshold` less than or equal to the alert's risk score. It then routes those targeted notifications directly via `send_alert_notification`.
**Coupling approach:** Event bridge pattern (fire and forget using `asyncio.create_task`). The Alert system emits the context by calling `dispatch_targeted_alerts`. Neither the core Alert models nor the Auth models needed modifications. Background tasks are tracked to prevent GC.
**Next connection:** Correlate predictive anomaly events directly with user activity logs to detect if user-reported symptoms align with predicted environmental outbreaks.
