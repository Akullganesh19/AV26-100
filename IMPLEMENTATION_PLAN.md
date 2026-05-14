# IMPLEMENTATION_PLAN — EpiSense

24-hour build plan. Steps are sequential within each phase. Phases can overlap between team members.

Assume a 2-person team: Person A (Backend/ML), Person B (Frontend).

---

## Hour 0–1: Project Setup (Both)

### Step 1.1 — Repository Init
```bash
mkdir episense && cd episense
git init
mkdir frontend backend
```

### Step 1.2 — Backend Scaffold (Person A)
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn sqlalchemy asyncpg alembic pydantic[email] pydantic-settings \
  python-jose passlib[bcrypt] httpx apscheduler xgboost pandas numpy shap \
  scikit-learn mlflow reportlab fastapi-mail python-multipart
pip freeze > requirements.txt
```

Create `app/main.py` with bare FastAPI app, health check endpoint `GET /api/health`.

### Step 1.3 — Frontend Scaffold (Person B)
```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install react-router-dom@6.23.1 zustand@4.5.2 @tanstack/react-query@5.40.0 \
  axios@1.7.2 recharts@2.12.7 react-simple-maps@3.0.0 \
  react-hook-form@7.52.0 zod@3.23.8 date-fns@3.6.0 lucide-react@0.390.0 sonner@1.5.0
npx tailwindcss init -p
```

Install shadcn/ui: `npx shadcn-ui@latest init` — choose Slate base, CSS variables yes.

Add Inter font to `index.html`.

### Step 1.4 — Docker Compose
Create `docker-compose.yml` with `db`, `backend`, `frontend`, `mlflow` services.
Create `backend/Dockerfile` and `frontend/Dockerfile`.

### Step 1.5 — Database Up
```bash
docker compose up db -d
```
Verify connection. Run `alembic init alembic`.

---

## Hour 1–3: Database + Auth (Person A)

### Step 2.1 — SQLAlchemy Models
Create `app/models/` files for all 9 tables from BACKEND_STRUCTURE.md.
One file per table: `user.py`, `district.py`, `raw_data.py`, `environmental_data.py`, `vaccination_coverage.py`, `prediction.py`, `alert.py`, `scenario.py`, `pipeline_run.py`.

### Step 2.2 — Alembic Migration
```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```
Verify all tables created in psql.

### Step 2.3 — Seed Data
Write `scripts/seed.py`:
- Insert 50 districts (10 per state: Karnataka, Tamil Nadu, Maharashtra, Rajasthan, West Bengal) with lat/lon.
- Insert 2 years of synthetic weekly case counts for all 4 diseases (random, with seasonal spikes).
- Insert 60 days of synthetic environmental data.
- Insert vaccination coverage records.
Run: `python scripts/seed.py`

### Step 2.4 — Auth Endpoints
Implement `app/api/routes/auth.py`:
- `POST /auth/register` — hash password, insert user, return 201.
- `POST /auth/login` — verify password, return JWT.
- `GET /auth/me` — decode JWT, return user.
- `POST /auth/forgot-password` — generate token, (log to console for hackathon, skip SMTP).
- `POST /auth/reset-password` — validate token, update hash.

Write `app/core/security.py`: `create_access_token()`, `verify_token()`, `hash_password()`, `verify_password()`.
Write `get_current_user` FastAPI dependency.

Test with curl or Bruno: register → login → `/auth/me`.

---

## Hour 3–5: ML Model (Person A continues)

### Step 3.1 — Feature Engineering
Write `app/ml/features.py`:
- `build_feature_row(district_id, disease, as_of_date, db)` — async function.
- Queries raw_data for 7-day rolling case count.
- Queries environmental_data for 7-day average weather.
- Returns `dict` matching the 9 features in BACKEND_STRUCTURE.md.

### Step 3.2 — Training Script
Write `app/ml/train.py`:
- Load all seed data into a pandas DataFrame.
- Engineer features for each (district, disease, week) combination.
- Create synthetic ground-truth risk scores (rule-based formula: weighted sum of case growth rate, rainfall, temperature deviation, vaccination gap). This is your training label.
- Train `XGBRegressor` (risk_score) and `XGBClassifier` (risk_tier).
- Fit `StandardScaler`.
- Fit `shap.TreeExplainer`.
- Save all artifacts to `app/ml/artifacts/` with `model.save_model()` and `pickle.dump()`.
- Log run to MLflow.

Run: `python -m app.ml.train`. Verify artifacts exist.

### Step 3.3 — Inference Service
Write `app/services/prediction_service.py`:
- `predict(district_id, disease, db, override_features=None)` → `PredictionResult`.
- Loads models once at startup (module-level singleton).
- Calls `build_feature_row()` or uses `override_features` if provided.
- Runs regressor + classifier.
- Runs SHAP.
- Upserts into `predictions` table.
- Returns score + tier + shap dict.

### Step 3.4 — Predict Endpoint
`POST /api/predict` — calls `prediction_service.predict()` with override features.

### Step 3.5 — Run Predictions for All Districts
Write `app/tasks/refresh_predictions.py` — loops all (district, disease) pairs, calls `predict()`, stores results.
Run once manually to populate predictions table for demo.

---

## Hour 3–6: Frontend Auth + Layout (Person B)

### Step 4.1 — Routing Setup
`src/App.tsx`: configure React Router with all routes from APP_FLOW.md.
Create placeholder page components for each route.
Implement route guard: `<ProtectedRoute>` component that checks Zustand auth store.

### Step 4.2 — Auth Store
`src/store/authStore.ts`: Zustand store with `user`, `token`, `login()`, `logout()`.
`login()` calls `POST /api/auth/login`, stores JWT in `localStorage`, sets user in store.

### Step 4.3 — Login Page
`src/pages/Login.tsx`: form with React Hook Form + Zod validation.
On success: call `authStore.login()`, navigate to `/dashboard`.

### Step 4.4 — Navbar + Layout
`src/components/Navbar.tsx`: logo, nav links, alert bell (static count for now), profile dropdown.
`src/components/Layout.tsx`: wraps all protected pages with Navbar.

### Step 4.5 — Axios Interceptor
`src/api/client.ts`: Axios instance with `baseURL = import.meta.env.VITE_API_BASE_URL`.
Request interceptor: attach `Authorization: Bearer <token>` from `authStore`.
Response interceptor: on 401 → clear auth store, redirect to `/login`.

---

## Hour 6–10: Dashboard + Map (Person B)

### Step 5.1 — Districts API Hook
`src/api/districts.ts`: `getDistricts(disease, timeWindow, state)` → calls `GET /api/districts`.
`src/hooks/useDistricts.ts`: TanStack Query `useQuery` wrapper.

### Step 5.2 — Choropleth Map
Download India districts TopoJSON from `https://raw.githubusercontent.com/geohacker/india/master/district/india_district.geojson` → place in `public/data/`.
`src/components/Map/ChoroplethMap.tsx`: `react-simple-maps` + `d3-scale`.
Props: `districts: DistrictWithRisk[]`, `onDistrictClick: (id: string) => void`.
Colour scale: `scaleQuantize` 0–100 → 5 stops.
Tooltip on hover.

### Step 5.3 — Dashboard Sidebar
`src/components/Dashboard/TopRiskSidebar.tsx`: sorted list of top 10 districts.
`src/components/Dashboard/FilterBar.tsx`: disease toggle, time window toggle, state dropdown.

### Step 5.4 — Dashboard Page Assembly
`src/pages/Dashboard.tsx`: layout = Navbar + FilterBar + Map + Sidebar.
Wire filters to `useDistricts` query params. Map re-renders on filter change.

### Step 5.5 — Districts Endpoint (Backend)
`app/api/routes/districts.py`:
- `GET /districts`: joins `districts` + latest `predictions` for given disease/date range. Returns list with risk_score.
- `GET /districts/:id`: full district with environmental data.
- `GET /districts/:id/timeseries`: historical raw_data + predictions joined.
- `GET /districts/:id/shap`: latest prediction's `shap_values` JSONB.
- `GET /districts/:id/environmental`: latest 7 rows from `environmental_data`.

---

## Hour 10–14: District Detail + Charts (Both)

### Step 6.1 — Time-Series Chart Component (Person B)
`src/components/Charts/TimeSeriesChart.tsx`: Recharts `ComposedChart`.
Historical bars + predicted line + forecast ReferenceArea shading.
Responsive, custom tooltip.

### Step 6.2 — SHAP Bar Chart (Person B)
`src/components/Charts/ShapChart.tsx`: horizontal `BarChart`, positive/negative fill.

### Step 6.3 — Environmental Cards (Person B)
`src/components/District/EnvironmentalPanel.tsx`: 5 `DataCard` components.

### Step 6.4 — District Page Assembly (Person B)
`src/pages/District.tsx`: breadcrumb, risk badge, alert banner (conditional), tabbed sections.
Wire all API calls via hooks.

### Step 6.5 — Alert Engine (Person A)
`app/tasks/alert_checker.py`:
- Query latest predictions where `risk_score > threshold`.
- Check if alert already exists for (district, disease, today) → skip if so.
- INSERT new alert rows.
- For each new alert: if `user.email_alerts = TRUE` → dispatch email (log to console for hackathon).

Write APScheduler setup in `app/tasks/scheduler.py`. Register alert_checker every 30 min.
Start scheduler in FastAPI `lifespan` context manager.

### Step 6.6 — Alerts Endpoints (Person A)
`app/api/routes/alerts.py`: all 4 endpoints with filtering, pagination.

---

## Hour 14–17: Simulator + Alerts Page (Both)

### Step 7.1 — Simulator Page (Person B)
`src/pages/Simulator.tsx`:
- District selector (searchable dropdown using `useDistricts`).
- 6 sliders with labels and current value display.
- On slider change: debounced POST `/api/predict` with overrides.
- Side-by-side: current vs. simulated risk badges.
- "Save Scenario" button.

### Step 7.2 — Alerts Page (Person B)
`src/pages/Alerts.tsx`:
- Filter bar (status, disease, severity, date range).
- Table with pagination.
- Inline acknowledge/dismiss actions.
- Bulk action toolbar.

### Step 7.3 — Alert Bell (Person B)
`src/components/Navbar.tsx`: add polling `useQuery` for `GET /api/alerts?unread=true&limit=5` every 60s.
Badge shows count. Dropdown shows latest 5.

### Step 7.4 — Scenarios Endpoints (Person A)
`app/api/routes/scenarios.py`: GET, POST, DELETE.

---

## Hour 17–20: Reports + Admin (Both)

### Step 8.1 — PDF Report Service (Person A)
`app/services/report_service.py`:
- `generate_district_report(district_id, disease, date_from, date_to, db)` → bytes.
- Uses ReportLab: header with EpiSense branding, district name, risk score big callout, trend table, top SHAP features list, recommendations paragraph (hardcoded templates by tier).
- Returns PDF bytes.

### Step 8.2 — Reports Endpoint (Person A)
`POST /api/reports`: calls report_service, returns `StreamingResponse` with `Content-Type: application/pdf`.

### Step 8.3 — Reports Page (Person B)
`src/pages/Reports.tsx`: form to trigger generation + download. Recent reports table.

### Step 8.4 — Admin Pages (Person B)
`src/pages/Admin.tsx` with 3 tabs: Users, Pipeline, Model.
Users tab: table with disable/role change actions.
Pipeline tab: table from `GET /api/admin/pipeline`.
Model tab: metrics from `GET /api/admin/model` (hardcoded from `model_metadata.json`).

### Step 8.5 — Admin Endpoints (Person A)
`app/api/routes/admin.py`: all admin endpoints. Sysadmin role guard dependency.

---

## Hour 20–22: Weather Ingestion + Polish (Both)

### Step 9.1 — Weather Ingestion Cron (Person A)
`app/tasks/ingest_weather.py`:
- For each district, call `https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,precipitation_sum,relativehumidity_2m_max&timezone=Asia/Kolkata&forecast_days=7`.
- Upsert into `environmental_data` for each date.
- Log run to `pipeline_runs`.

Trigger manually: `python -m app.tasks.ingest_weather` → verify DB populated.

### Step 9.2 — Empty + Error States (Person B)
Add `<ErrorState>` and `<EmptyState>` components.
Add skeleton loaders to map, charts, tables.

### Step 9.3 — Responsive Fixes (Person B)
Test at 768px. Sidebar collapses. Map full-width. Verify no overflow.

### Step 9.4 — Toast Notifications (Person B)
Wire Sonner toasts for: login success/failure, alert acknowledged, report downloaded, scenario saved.

---

## Hour 22–24: Integration, Testing, Demo Prep

### Step 10.1 — End-to-End Integration Test
Manual walkthrough:
- Register → Login.
- Dashboard loads with map and data.
- Click district → detail page with charts.
- Simulator: adjust rainfall slider → risk score updates.
- Alerts page: at least one active alert visible.
- Download PDF report: verify opens correctly.
- Admin panel: user list loads.

### Step 10.2 — Docker Compose Final Test
```bash
docker compose down -v
docker compose up --build
```
Verify all services start. Seed runs. Predictions populated. Frontend accessible at `localhost:3000`.

### Step 10.3 — Demo Script
Prepare 5-minute walkthrough:
1. Show dashboard map → explain choropleth.
2. Click highest-risk district → show time-series + SHAP chart.
3. Open Simulator → raise rainfall slider → show risk increase.
4. Show Alerts page → acknowledge one alert.
5. Download PDF report.
6. (Optional) Show Admin panel.

### Step 10.4 — Presentation Slide (1 slide)
Architecture diagram: React → FastAPI → PostgreSQL + XGBoost + OpenMeteo.

---

## Parallel Work Summary

| Hours | Person A (Backend/ML) | Person B (Frontend) |
|-------|----------------------|---------------------|
| 0–1 | Scaffold + Docker | Scaffold + Tailwind |
| 1–3 | DB Models + Auth | Auth UI + Layout |
| 3–6 | ML Train + Predict | Dashboard + Map |
| 6–10 | Alerts Engine | District Charts |
| 10–14 | District Endpoints | Simulator UI |
| 14–17 | Reports + Admin API | Alerts + Admin UI |
| 17–20 | Weather Ingestion | Polish + Responsive |
| 20–24 | Integration + Fix | Integration + Demo Prep |
