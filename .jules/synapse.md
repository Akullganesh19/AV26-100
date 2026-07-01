## 2025-02-20 — Alerts ↔ Users (Event Bridge)
**Systems connected:** Alert System ↔ User Notifications (SendGrid Integration)
**Intelligence emerged:** The system now automatically routes high-priority tactical outbreak and clinical cluster alerts to users subscribed to those specific districts via email, closing the loop between background threat detection and human responders.
**Data flows:** Alert data (disease, district, risk score, alert type) flows from the background Alert Service through an Event Bridge to the User Notification subscriber, which queries for relevant users and dispatches emails.
**Coupling approach:** Event Bus loosely couples the systems using a Publish/Subscribe pattern (`alert.created` event). The AlertService has zero knowledge of the User model or the Email integration.
**Next connection:** Errors ↔ Users (Surface error incidence rates to affected users automatically).
