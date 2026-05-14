# EpiSense Intelligence Platform: Technical Manifest (v1.0)

## 🎯 1. Objective & Capabilities
EpiSense is a dual-track epidemiological intelligence platform designed for regional health mission coordination. It provides a vertical slice from clinical triage to autonomous threat detection.

*   **Clinical Triage Engine**: Real-time heart, diabetes, and Parkinson’s screening with cryptographic model integrity verification (SHA-256).
*   **Tactical Alerts**: Autonomous background monitoring and clinical cluster detection (e.g., >5 HIGH-risk events in 24h) with persistent mission sign-off.
*   **Strategic Risk Matrix**: Geospatial visualization of regional mission sectors using localized GeoJSON overlays.
*   **Scenario Lab**: A step-based snapshot playback engine for guided outbreak simulations and response calibration.

## 🧠 2. Data Provenance & ML Foundation
*   **Model Source**: Integrating standard academically trained models (UCI Heart Disease, Pima Indians Diabetes, UCI Parkinson's).
*   **Dataset Limitations**: These models are trained on Western academic datasets from the 1980s-90s. While functionally robust for system demonstration, they are **not recalibrated for Indian population demographics** or contemporary clinical variance.
*   **Mission Telemetry**: Demonstration data is driven by a synthetic seed generator primed with idempotent clinical clusters to enable organic outbreak triggers.

## 🛡️ 3. Technical Constraints & Non-Objectives
*   **Not a Diagnostic Tool**: This platform is a **demonstration of health intelligence architecture**, not a validated medical device. It should not be used for actual clinical decision-making.
*   **Architectural Scale**: The system is built as a single-node asynchronous service (FastAPI + SQLAlchemy). While fault-tolerant logic is implemented for background tasks, it is not scaled for high-concurrency national deployments without a distributed task queue (Celery/Redpanda).
*   **Security Baseline**:
    *   Auth tokens are managed via `localStorage` for development simplicity; production hardening would require `HttpOnly/Secure` cookie migration.
    *   Geospatial rendering is tile-based; performance may degrade on low-bandwidth mission networks (2G/3G).

## 🚀 4. Mission Deployment
1.  **Environment**: Configure `DATABASE_URL` and `SECRET_KEY` in `.env`.
2.  **Seeding**: Run `python backend/scripts/seed.py` to initialize mission templates and prime clinical clusters.
3.  **Command Center**: `npm run dev` (Frontend) | `uvicorn app.main:app` (Backend).

**Mission Credentials**: `officer@episense.gov` / `tactical_alpha` (Primed for Bengaluru sector demo).
