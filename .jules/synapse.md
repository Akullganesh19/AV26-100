## 2024-05-18 — Alert Target Routing
**Systems connected:** Alerts ↔ Users
**Intelligence emerged:** Proactive, personalized email notifications based on a user's explicitly subscribed districts and their customized risk threshold, preventing alert fatigue.
**Data flows:** When an `Alert` is triggered, its ID flows to the User system. The User system queries for officers monitoring that specific `District` who have `email_alerts` enabled and a threshold below the alert's `risk_score`, then dispatches targeted emails.
**Coupling approach:** Event Bridge Pattern. The Alert service simply publishes an `alert.triggered` event to the `EventBus`. The User/Notification listener subscribes to this event and independently orchestrates the query and email dispatch.
**Next connection:** Analytics ↔ Auth (User engagement with reports).
