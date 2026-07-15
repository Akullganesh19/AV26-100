## 2024-05-18 — Auth ↔ Alerts (Targeted Notifications)
**Systems connected:** Auth/Users ↔ Alerts/Predictions
**Intelligence emerged:** Proactive, targeted notifications based on personal user alert thresholds and assigned districts instead of purely generic application-wide alerts.
**Data flows:** Alerts/Predictions emit events containing district_id and risk scores. The Notification Dispatcher receives these events, fetches assigned users from the Auth system via user_district mapping, cross-references each user's specific email alert setting and risk threshold, and targets specific alerts effectively.
**Coupling approach:** Loosely coupled using an EventBus implementation with pub/sub architecture. `EventBus` operates via async functions without polluting core execution layers.
**Next connection:** User Behavior ↔ Content Filtering.
