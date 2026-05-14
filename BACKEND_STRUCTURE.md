# BACKEND_STRUCTURE — EpiSense

---

## Project Layout

```
backend/
  app/
    api/
      routes/
        auth.py          → /api/auth/*
        districts.py     → /api/districts/*
        alerts.py        → /api/alerts/*
        predict.py       → /api/predict
        reports.py       → /api/reports/*
        admin.py         → /api/admin/*
        scenarios.py     → /api/scenarios/*
    core/
      config.py          → Settings (pydantic-settings BaseSettings)
      security.py        → JWT encode/decode, password hashing
      database.py        → Async SQLAlchemy engine + session
    models/              → SQLAlchemy ORM models (one file per table)
    schemas/             → Pydantic request/response schemas
    services/
      auth_service.py
      district_service.py
      alert_service.py
      prediction_service.py
      report_service.py
      ingestion_service.py
    ml/
      model.py           → Load XGBoost model, run inference
      train.py           → Training script (run once to generate model)
      shap_explainer.py  → SHAP value computation
    tasks/
      scheduler.py       → APScheduler setup
      ingest_weather.py  → Daily weather ingestion cron
      alert_checker.py   → Hourly alert threshold check
    main.py              → FastAPI app factory, router registration, lifespan
  alembic/               → Migration files
  alembic.ini
  requirements.txt
  Dockerfile
```

---

## Database Schema

### Table: `users`

```sql
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          VARCHAR(128) NOT NULL,
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(32) NOT NULL DEFAULT 'officer',  -- 'officer' | 'admin' | 'sysadmin'
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    alert_threshold INTEGER NOT NULL DEFAULT 70,
    email_alerts  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Table: `districts`

```sql
CREATE TABLE districts (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          VARCHAR(128) NOT NULL,
    state         VARCHAR(128) NOT NULL,
    state_code    CHAR(2) NOT NULL,
    latitude      NUMERIC(9,6) NOT NULL,
    longitude     NUMERIC(9,6) NOT NULL,
    population    BIGINT,
    area_km2      NUMERIC(10,2),
    population_density NUMERIC(10,2) GENERATED ALWAYS AS (population / NULLIF(area_km2, 0)) STORED,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_districts_state ON districts(state_code);
```

### Table: `raw_data`

```sql
-- Ingested weekly epidemiological records (IDSP-style synthetic data)
CREATE TABLE raw_data (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    district_id     UUID NOT NULL REFERENCES districts(id),
    disease         VARCHAR(64) NOT NULL,   -- 'dengue' | 'cholera' | 'influenza' | 'malaria'
    week_start_date DATE NOT NULL,
    confirmed_cases INTEGER NOT NULL DEFAULT 0,
    suspected_cases INTEGER NOT NULL DEFAULT 0,
    deaths          INTEGER NOT NULL DEFAULT 0,
    source          VARCHAR(64) NOT NULL DEFAULT 'IDSP_synthetic',
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (district_id, disease, week_start_date)
);
CREATE INDEX idx_raw_data_district_disease ON raw_data(district_id, disease);
CREATE INDEX idx_raw_data_date ON raw_data(week_start_date DESC);
```

### Table: `environmental_data`

```sql
-- Daily weather readings per district
CREATE TABLE environmental_data (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    district_id     UUID NOT NULL REFERENCES districts(id),
    date            DATE NOT NULL,
    temperature_c   NUMERIC(5,2),         -- avg daily temperature
    rainfall_mm     NUMERIC(7,2),         -- total daily rainfall
    humidity_pct    NUMERIC(5,2),         -- avg relative humidity
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (district_id, date)
);
CREATE INDEX idx_env_district_date ON environmental_data(district_id, date DESC);
```

### Table: `vaccination_coverage`

```sql
-- Static or periodically updated vaccination rates
CREATE TABLE vaccination_coverage (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    district_id   UUID NOT NULL REFERENCES districts(id),
    disease       VARCHAR(64) NOT NULL,
    coverage_pct  NUMERIC(5,2) NOT NULL,
    as_of_date    DATE NOT NULL,
    UNIQUE (district_id, disease, as_of_date)
);
```

### Table: `predictions`

```sql
-- Stored prediction results (one per district/disease/date)
CREATE TABLE predictions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    district_id     UUID NOT NULL REFERENCES districts(id),
    disease         VARCHAR(64) NOT NULL,
    prediction_date DATE NOT NULL,              -- The date being predicted for
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    risk_score      NUMERIC(5,2) NOT NULL,      -- 0–100
    risk_tier       VARCHAR(16) NOT NULL,        -- 'low' | 'medium' | 'high' | 'critical'
    model_version   VARCHAR(32) NOT NULL,
    feature_snapshot JSONB NOT NULL,            -- snapshot of input features used
    shap_values     JSONB,                      -- SHAP dict {feature: value}
    UNIQUE (district_id, disease, prediction_date)
);
CREATE INDEX idx_pred_district_disease ON predictions(district_id, disease);
CREATE INDEX idx_pred_date ON predictions(prediction_date DESC);
```

### Table: `alerts`

```sql
CREATE TABLE alerts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    district_id     UUID NOT NULL REFERENCES districts(id),
    disease         VARCHAR(64) NOT NULL,
    risk_score      NUMERIC(5,2) NOT NULL,
    threshold       INTEGER NOT NULL,
    prediction_id   UUID REFERENCES predictions(id),
    status          VARCHAR(32) NOT NULL DEFAULT 'active',  -- 'active' | 'acknowledged' | 'dismissed'
    triggered_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acknowledged_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMPTZ,
    UNIQUE (district_id, disease, triggered_at::DATE)   -- one alert per district/disease/day
);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_triggered ON alerts(triggered_at DESC);
```

### Table: `scenarios`

```sql
-- Saved what-if simulator scenarios
CREATE TABLE scenarios (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    district_id     UUID NOT NULL REFERENCES districts(id),
    disease         VARCHAR(64) NOT NULL,
    name            VARCHAR(128),
    adjusted_inputs JSONB NOT NULL,      -- {rainfall_mm, temperature_c, humidity_pct, vaccination_pct, case_count_7d}
    simulated_score NUMERIC(5,2),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Table: `password_reset_tokens`

```sql
CREATE TABLE password_reset_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id),
    token_hash  VARCHAR(255) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    used        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Table: `pipeline_runs`

```sql
CREATE TABLE pipeline_runs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_name VARCHAR(64) NOT NULL,
    status        VARCHAR(32) NOT NULL,   -- 'success' | 'failed' | 'running'
    rows_ingested INTEGER,
    error_log     TEXT,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at   TIMESTAMPTZ
);
```

---

## API Endpoints

Base path: `/api`

### Auth — `/api/auth`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | None | Register new user |
| POST | `/auth/login` | None | Login, returns JWT |
| POST | `/auth/forgot-password` | None | Sends reset email |
| POST | `/auth/reset-password` | None | Validates token, updates password |
| GET  | `/auth/me` | JWT | Returns current user profile |

#### POST `/auth/login` Request
```json
{ "email": "officer@health.gov", "password": "secret" }
```
#### POST `/auth/login` Response
```json
{ "access_token": "eyJ...", "token_type": "bearer", "user": { "id": "...", "name": "...", "role": "officer" } }
```

---

### Districts — `/api/districts`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/districts` | JWT | List all districts (name, state, current risk scores per disease) |
| GET | `/districts/:id` | JWT | Full district detail |
| GET | `/districts/:id/timeseries` | JWT | Historical + forecast time series for chart |
| GET | `/districts/:id/environmental` | JWT | Latest environmental data |
| GET | `/districts/:id/shap` | JWT | SHAP values for latest prediction |

#### GET `/districts` Query Params
```
?disease=dengue&time_window=14&state=KA
```
#### GET `/districts` Response
```json
{
  "districts": [
    {
      "id": "uuid",
      "name": "Bangalore Urban",
      "state": "Karnataka",
      "risk_score": 78.4,
      "risk_tier": "high",
      "prediction_date": "2026-05-14"
    }
  ]
}
```

#### GET `/districts/:id/timeseries` Response
```json
{
  "historical": [
    { "date": "2026-04-01", "risk_score": 42.1, "confirmed_cases": 12 }
  ],
  "forecast": [
    { "date": "2026-05-15", "risk_score": 81.3, "confirmed_cases": null }
  ]
}
```

---

### Predict — `/api/predict`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/predict` | JWT | Run inference with provided feature values |

#### POST `/predict` Request
```json
{
  "district_id": "uuid",
  "disease": "dengue",
  "features": {
    "rainfall_mm": 120.5,
    "temperature_c": 32.0,
    "humidity_pct": 78.0,
    "case_count_7d": 45,
    "vaccination_pct": 60.0
  }
}
```
#### POST `/predict` Response
```json
{
  "risk_score": 84.2,
  "risk_tier": "critical",
  "shap_values": {
    "rainfall_mm": 12.4,
    "case_count_7d": 9.1,
    "temperature_c": 6.2,
    "humidity_pct": 3.0,
    "vaccination_pct": -5.8
  }
}
```

---

### Alerts — `/api/alerts`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/alerts` | JWT | List alerts with filters |
| GET | `/alerts/:id` | JWT | Single alert detail |
| PATCH | `/alerts/:id/ack` | JWT (officer+) | Acknowledge alert |
| PATCH | `/alerts/:id/dismiss` | JWT (officer+) | Dismiss alert |

#### GET `/alerts` Query Params
```
?status=active&disease=dengue&severity=high&unread=true&limit=5&offset=0
```

---

### Reports — `/api/reports`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/reports` | JWT | Generate PDF report (returns file) |
| GET  | `/reports/history` | JWT | List past generated reports |

#### POST `/reports` Request
```json
{ "district_id": "uuid", "disease": "dengue", "date_from": "2026-04-01", "date_to": "2026-05-14" }
```
Response: `Content-Type: application/pdf` — binary PDF stream.

---

### Scenarios — `/api/scenarios`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/scenarios` | JWT | List user's saved scenarios |
| POST | `/scenarios` | JWT | Save a scenario |
| DELETE | `/scenarios/:id` | JWT | Delete a scenario |

---

### Admin — `/api/admin` (sysadmin only)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/admin/users` | sysadmin | List all users |
| POST | `/admin/users` | sysadmin | Create/invite user |
| PATCH | `/admin/users/:id` | sysadmin | Update role or status |
| GET | `/admin/pipeline` | sysadmin | Pipeline run history |
| POST | `/admin/pipeline/:name/run` | sysadmin | Trigger manual pipeline run |
| GET | `/admin/model` | sysadmin | Model metrics |

---

## ML Model

### Input Features (in order)

| Feature | Source | Type |
|---------|--------|------|
| `case_count_7d` | raw_data (7-day rolling sum) | int |
| `case_count_prev_7d` | raw_data (prior week) | int |
| `rainfall_mm_7d` | environmental_data (7-day avg) | float |
| `temperature_c_avg` | environmental_data (7-day avg) | float |
| `humidity_pct_avg` | environmental_data (7-day avg) | float |
| `population_density` | districts | float |
| `vaccination_pct` | vaccination_coverage | float |
| `outbreak_flag_prev_year` | raw_data (historical) | int (0/1) |
| `month` | derived from prediction date | int (1–12) |

### Model Files

```
backend/ml/artifacts/
  xgb_classifier_v1.json     → risk tier classifier (4 classes)
  xgb_regressor_v1.json      → risk score regressor (0–100)
  feature_scaler.pkl         → StandardScaler fitted on training data
  shap_explainer.pkl         → SHAP TreeExplainer
  model_metadata.json        → version, trained_at, metrics
```

### Inference Flow

```python
# prediction_service.py
1. Load feature values from DB (district + last 7 days)
2. Scale with feature_scaler
3. regressor.predict() → risk_score (float 0–100)
4. classifier.predict() → risk_tier (string)
5. shap_explainer.shap_values() → {feature: contribution}
6. INSERT INTO predictions (or UPDATE on conflict)
7. Check threshold → INSERT INTO alerts if crossed
8. Return PredictionResponse
```

---

## Scheduled Tasks

| Task | Schedule | Function |
|------|----------|----------|
| Weather ingestion | Daily 02:00 IST | `ingest_weather.py` — calls OpenMeteo for all districts |
| Prediction refresh | Daily 03:00 IST | `prediction_service.run_all()` — predictions for all districts |
| Alert checker | Every 1 hour | `alert_checker.py` — checks latest predictions vs. thresholds |
| Cleanup old tokens | Daily 04:00 IST | Delete expired password_reset_tokens |
