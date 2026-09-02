## YYYY-MM-DD — [Alerts to Targeted Users]
**Systems connected:** [Alerts ↔ Auth/Users]
**Intelligence emerged:** Proactive, targeted notification of officers based on user-specific thresholds and district assignments when alerts trigger, correlating raw alert data with user context.
**Data flows:** Alerts System (Triggers Alert) -> Event Bus -> Auth/User System (Retrieves affected users via threshold/district match) -> Notification Mock
**Coupling approach:** Event Bus pattern (loosely coupled). `AlertService` emits an event, and `synapse.py` listens and joins data.
**Next connection:** Errors ↔ Auth to identify users experiencing errors.
