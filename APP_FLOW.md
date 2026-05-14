# APP_FLOW — EpiSense Navigation & User Paths

---

## Route Map

```
/                       → Redirect to /dashboard if logged in, else /login
/login                  → Login page
/register               → Register page
/forgot-password        → Forgot password page
/reset-password/:token  → Reset password page

/dashboard              → National choropleth dashboard (default: dengue, 14d)
/district/:id           → District detail view
/alerts                 → Alert history & management
/simulator              → What-if scenario simulator
/reports                → Report generation & download history
/admin                  → Admin panel (sysadmin only)
/admin/users            → User management
/admin/pipeline         → Data pipeline status
/admin/model            → Model metrics
/profile                → User profile & notification preferences
```

---

## Page-by-Page Flow

### `/login`
- Inputs: email, password.
- On submit: POST `/api/auth/login`.
- Success: store JWT in `localStorage`, redirect to `/dashboard`.
- Failure: inline error "Invalid credentials."
- Link: "Forgot password?" → `/forgot-password`.
- Link: "Create account" → `/register`.

### `/register`
- Inputs: name, email, password, confirm password, role (officer/admin — sysadmin not self-registerable).
- On submit: POST `/api/auth/register`.
- Success: redirect to `/login` with toast "Account created. Please log in."
- Failure: inline validation errors per field.

### `/forgot-password`
- Input: email.
- On submit: POST `/api/auth/forgot-password`.
- Always shows "If that email exists, a reset link has been sent." (no enumeration).
- Link: "Back to login."

### `/reset-password/:token`
- Inputs: new password, confirm password.
- On submit: POST `/api/auth/reset-password`.
- Success: redirect to `/login` with toast "Password reset."

---

### `/dashboard` (Protected — all roles)

**Initial State:**
- Header: logo, nav links (Dashboard, Alerts [badge], Simulator, Reports), profile avatar → dropdown (Profile, Logout).
- Left sidebar: disease filter (Dengue | Cholera | Influenza | Malaria), time window (7d | 14d | 30d), state filter (All States | dropdown).
- Main area: India choropleth map (SVG/Mapbox). Districts colour-coded by risk score.
- Right sidebar: Top 10 High-Risk Districts ranked table (district, state, risk score, trend arrow).
- Bottom bar: last data refresh timestamp.

**User Actions:**
- Click disease filter → map re-renders with updated choropleth. No page reload.
- Click time window → map and sidebar re-render.
- Click any district on map → navigate to `/district/:id`.
- Click district in right sidebar → navigate to `/district/:id`.
- Click alert bell → dropdown shows 5 latest unread alerts with timestamps.
- Click "View All Alerts" in dropdown → navigate to `/alerts`.

---

### `/district/:id` (Protected — all roles)

**Layout:**
- Breadcrumb: Dashboard / [State Name] / [District Name].
- Top: District name, State, Current Risk Score (large badge, colour coded), Risk Tier label (LOW/MEDIUM/HIGH/CRITICAL).
- Alert banner (if risk > 70): red banner with message and "Acknowledge" button.

**Tabs:**
1. **Overview**
   - Dual-axis time-series chart: predicted risk score (line, left axis) vs. confirmed cases (bar, right axis). X-axis: last 30 days + 14-day forecast (forecast region shaded).
   - Summary cards: Predicted Peak Date, Predicted Peak Score, Primary Driver.

2. **Environmental Factors**
   - Cards: Rainfall (mm), Temperature (°C), Humidity (%), Population Density (per km²), Vaccination Coverage (%).
   - Each card shows current value, 7-day trend sparkline.

3. **Model Explainability**
   - SHAP bar chart: top 8 features by contribution to current risk score.
   - Feature direction indicators (↑ increasing risk / ↓ decreasing risk).

4. **Alerts History** (district-scoped)
   - Table: Date, Threshold crossed, Status (Active/Acknowledged/Dismissed).

**Actions:**
- "Download PDF Report" button → GET `/api/reports/district/:id` → PDF download.
- "Open in Simulator" button → navigate to `/simulator?district=:id` with state pre-loaded.
- Acknowledge alert button → PATCH `/api/alerts/:alertId/ack`.

---

### `/alerts` (Protected — all roles)

**Layout:**
- Filter bar: Status (All | Active | Acknowledged | Dismissed), Disease, Severity (Low | Medium | High | Critical), Date range.
- Alerts table: columns — District, State, Disease, Risk Score, Threshold, Triggered At, Status, Actions.
- Pagination: 25 per page.

**Actions per row:**
- Acknowledge → PATCH `/api/alerts/:id/ack` → row status updates inline.
- Dismiss → PATCH `/api/alerts/:id/dismiss`.
- View District → navigate to `/district/:id`.

**Bulk actions:**
- Select all visible → Acknowledge All, Dismiss All.

---

### `/simulator` (Protected — officer/sysadmin)

**Layout:**
- District selector dropdown (searchable). Pre-filled if arrived from `/district/:id`.
- Two-column layout:
  - Left: Current Values panel (read-only cards showing live values).
  - Right: Adjusted Values panel (sliders for each variable).

**Sliders:**
- Rainfall: 0–300mm, step 5.
- Temperature: 15–45°C, step 0.5.
- Humidity: 20–100%, step 1.
- Population Density: read-only (display only).
- Vaccination Coverage: 0–100%, step 1.
- Case Count (7-day rolling): 0–5000, step 10.

**On any slider change:**
- Debounced 300ms → POST `/api/predict` with adjusted values → update "Simulated Risk Score" card.
- Side-by-side: Current Risk [badge] vs. Simulated Risk [badge].
- Delta indicator: +12 points ↑ (red) or -8 points ↓ (green).

**Actions:**
- "Reset to Current" → sliders snap back to live values.
- "Save Scenario" → POST `/api/scenarios` → toast "Scenario saved."
- "View Saved Scenarios" → expand section showing saved scenario list.

---

### `/reports` (Protected — all roles)

**Layout:**
- Generate Report form:
  - District dropdown (searchable).
  - Disease type.
  - Date range.
  - "Generate" button → POST `/api/reports` → triggers generation (async, 2–5s) → download starts.
- Recent Reports table: columns — District, Disease, Generated At, Download.

---

### `/admin` (Protected — sysadmin only)

Three sub-pages via tab nav:

**`/admin/users`**
- Table: Name, Email, Role, Status (Active/Disabled), Created At, Actions.
- Actions: Disable, Change Role.
- "Invite User" button → modal with email + role → POST `/api/admin/users`.

**`/admin/pipeline`**
- Table: Pipeline Name, Last Run, Status (Success/Failed/Running), Rows Ingested, Error Log.
- "Trigger Manual Run" button per pipeline → POST `/api/admin/pipeline/:name/run`.

**`/admin/model`**
- Current model version, trained at timestamp.
- Metrics: Accuracy, AUC-ROC, F1, MAE.
- Feature importance bar chart.
- "Retrain Model" button (disabled in hackathon demo — placeholder).

---

### `/profile` (Protected — all roles)

- Edit: name, email (requires re-auth).
- Notification preferences: toggle email alerts on/off, alert threshold selector.
- Change password form.

---

## Navigation Guards

- Any `/dashboard`, `/district/*`, `/alerts`, `/simulator`, `/reports` → redirect to `/login` if no valid JWT.
- `/admin/*` → redirect to `/dashboard` if role ≠ sysadmin. Show toast "Access denied."
- `/simulator` → redirect to `/dashboard` if role = admin (read-only role restriction).

---

## Global Components

- **Navbar**: always visible when authenticated. Collapses to hamburger on < 768px.
- **Alert Bell**: unread count badge, live-polled every 60s via GET `/api/alerts?unread=true&limit=5`.
- **Toast system**: success (green), error (red), info (blue) — auto-dismiss 4s.
- **Loading states**: skeleton loaders on map, charts, tables while fetching.
- **Empty states**: illustrated empty state when no data matches filter.
