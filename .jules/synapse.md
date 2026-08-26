## 2024-07-25 — Alert Threshold ↔ Users Connection
**Systems connected:** Alerts ↔ Auth/Users
**Intelligence emerged:** Proactive, targeted dispatch of outbreak warnings to relevant users based on personalized alert thresholds and regional jurisdiction.
**Data flows:** Alerts System emits events -> Users System queries affected personnel -> Notification System dispatches.
**Coupling approach:** Event Bus (`alert.triggered`) ensures Alerts System doesn't import User models directly.
**Next connection:** Errors ↔ Usage Analytics to understand impact of failures.
