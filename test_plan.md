1. **Understand System Disconnects:**
   - **System A (Alert System):** Creates alerts and stores them in `alerts` table (`backend/app/services/alert_service.py`, `backend/app/tasks/alerts.py`).
   - **System B (Users & Communication):** Contains user roles, email addresses, and `email_alerts` preference (`backend/app/models/user.py`), plus Integration Service (`backend/app/api/integrations.py`) to send emails via SendGrid (`send_health_alert_email`).

   *The intelligence gap:* High-priority alerts are created and can be viewed via the API (`/alerts`), and there is a stub `send_alert_notification` in `backend/app/tasks/alerts.py`. But alerts aren't systematically pushed as emails to the right people (e.g., users configured for `email_alerts` covering that district) when they're generated. Actually, `send_alert_notification` only logs it out or theoretically uses SendGrid for a single hardcoded integration, but it has no idea who to send it to. The `AlertService` triggers the `Tactical Alert: Clinical cluster detected`, inserts into DB, but doesn't notify users.

2. **Connection to Build:** Use the `event_bus` I just created in `backend/app/core/events.py` to fire an event when a new alert is generated.
   - A new `notification_subscriber.py` in `backend/app/core/subscribers/` will listen to `"alert.created"`.
   - When fired, it queries the DB to find users who:
     - are linked to that district (`user_district_association`)
     - have `email_alerts == True`
   - For each user, call `integration_service.send_health_alert_email`.

Let's refine this to make sure it doesn't break anything.
