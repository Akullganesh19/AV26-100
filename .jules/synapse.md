## 2024-05-24 — Alert Routing to Users
**Systems connected:** Alerts ↔ Users
**Intelligence emerged:** The platform can now proactively target individual users when mission-critical clinical clusters or autonomous threats emerge in their specific jurisdiction, bypassing the need for manual dashboard monitoring.
**Data flows:** Alerts (Alert triggers) -> Event Bus -> Users (query users by district and threshold limits) -> Target Notifications.
**Coupling approach:** Event Bus with explicit decoupled SQL queries. The Alert system does not import the User system and vice-versa.
**Next connection:** Correlate user simulation performance (Scenarios) with real clinical alerts to find training gaps.
