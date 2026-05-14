# PRD — EpiSense: Disease Outbreak Prediction Platform

## Overview

EpiSense is a web-based predictive analytics platform that ingests historical health data, environmental factors, and real-time inputs to forecast disease outbreak risk at a district/region level. It surfaces alerts, trend visualizations, and public-health recommendations to health officers and administrators.

---

## Problem Statement (Verbatim from Hackathon)

> Design a predictive analytics platform using AI/ML techniques that analyzes historical health data, environmental factors, and real-time inputs to forecast potential disease outbreaks, enabling early warning and proactive public health response.

---

## Goals

- Predict outbreak risk (0–100 score) for configurable diseases across Indian states/districts.
- Provide early warning alerts (72-hour lookahead minimum) with confidence levels.
- Visualize trends on a choropleth map and time-series dashboard.
- Allow health officers to simulate "what if" scenarios by adjusting environmental variables.
- Generate a downloadable PDF risk report per district.

---

## Users

| Role | Description |
|------|-------------|
| Public Health Officer | Primary user. Monitors outbreaks, receives alerts, generates reports. |
| District Administrator | Views dashboard, exports PDF reports. Read-only. |
| System Admin | Manages data ingestion pipelines and user accounts. |

---

## Features (In Scope)

### F1 — Authentication
- Email/password login and registration.
- Role-based access: officer, admin, sysadmin.
- JWT-based session with 24-hour expiry.
- Forgot-password email flow.

### F2 — National/State Dashboard
- India choropleth map with district-level risk colour coding (green → amber → red).
- Sidebar panel: top 10 highest-risk districts ranked by current score.
- Filter by disease type (dengue, cholera, influenza, malaria).
- Filter by time window: 7d, 14d, 30d forecast.

### F3 — District Detail View
- Time-series chart: predicted risk score vs. historical confirmed cases (dual-axis).
- Environmental variables panel: rainfall (mm), temperature (°C), humidity (%), population density.
- Breakdown: which features drove the prediction (SHAP bar chart).
- Alert banner if risk score > 70.

### F4 — Alert System
- Real-time alerts when model crosses threshold (configurable: 60/70/80).
- In-app notification bell with unread count.
- Email notification dispatched on high-risk alert (> 70 default).
- Alert history table with ack/dismiss flow.

### F5 — What-If Simulator
- Sliders to manually override rainfall, temperature, population density, vaccination coverage.
- Re-runs inference on adjusted values and shows updated risk score instantly (< 2s).
- Side-by-side: current vs. simulated risk.

### F6 — ML Model Backend
- Trained XGBoost classifier (risk tier) + regressor (risk score 0–100).
- Feature set: 7-day rolling case counts, rainfall, temperature, humidity, population density, vaccination rate, outbreak history flag.
- Model versioning via MLflow (local).
- REST inference endpoint: POST `/api/predict`.

### F7 — Data Ingestion Pipeline
- Seed dataset: IDSP weekly surveillance CSV (simulated/synthetic for hackathon).
- Cron job (daily 02:00 IST): pull OpenMeteo weather API for temperature, rainfall, humidity per district.
- District population density from static JSON (Census 2011 interpolated).
- All ingested records stored in PostgreSQL `raw_data` table.

### F8 — Report Generator
- PDF report per district: risk score, trend chart, top features, recommendations.
- Generated with ReportLab. Download from district detail page.
- Optional email delivery.

### F9 — Admin Panel
- User management: create/disable accounts, assign roles.
- Data pipeline status: last run time, row count, error logs.
- Model metrics dashboard: accuracy, AUC, feature importance.

---

## Out of Scope

- Real-time IoT sensor ingestion (simulated data only for hackathon).
- Mobile native app (responsive web only).
- Genomic sequencing data integration.
- Multi-language UI (English only).
- SMS alerts.
- Hospital bed capacity integration.
- Actual live IDSP API (requires government credentials — synthetic data used).
- Billing or subscription logic.
- OAuth (Google/GitHub login).

---

## Success Metrics (Hackathon Demo)

- Dashboard loads with map in < 3 seconds.
- Prediction API responds in < 500ms.
- What-if simulator updates in < 2 seconds.
- All 4 disease types selectable with different heatmap renders.
- At least one alert fires during demo walkthrough.
- PDF report downloads successfully.

---

## Constraints

- 24-hour build window.
- Deployable locally with a single `docker-compose up`.
- No paid APIs. OpenMeteo is free.
- Seed/synthetic data must be pre-loaded — no dependency on live government APIs.
