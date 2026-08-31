# TECH_STACK — EpiSense

No vague "use React" entries. Every library pinned to exact version.

---

## Frontend

| Layer | Choice | Version | Why |
|-------|--------|---------|-----|
| Framework | React | 18.2.0 | Concurrent mode, stable hooks |
| Build tool | Vite | 5.2.11 | Sub-second HMR, ESM-native |
| Language | TypeScript | 5.4.5 | Type safety for API contracts |
| Router | React Router DOM | 6.23.1 | Nested routes, loaders |
| State management | Zustand | 4.5.2 | Lightweight, no boilerplate |
| Server state / caching | TanStack Query (React Query) | 5.40.0 | Cache, refetch, loading/error states |
| HTTP client | Axios | 1.7.2 | Interceptors for JWT injection |
| Styling | Tailwind CSS | 3.4.4 | Utility-first, no runtime CSS |
| Component library | shadcn/ui | latest (June 2024 snapshot) | Accessible, unstyled base |
| Charts | Recharts | 2.12.7 | Declarative, React-native charting |
| Map | react-simple-maps | 3.0.0 | SVG-based India choropleth |
| SHAP bar chart | Recharts BarChart (same lib) | — | Re-used |
| PDF download | Browser fetch → blob | — | Trigger from `/api/reports` |
| Toast | Sonner | 1.5.0 | Simple, accessible toasts |
| Form validation | React Hook Form | 7.52.0 | Uncontrolled, performant |
| Form schema | Zod | 3.23.8 | Type-safe validation + inference |
| Date utilities | date-fns | 3.6.0 | Tree-shakeable |
| Icons | Lucide React | 0.390.0 | Consistent icon set |

### Frontend `.env`
```
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=EpiSense
```

---

## Backend

| Layer | Choice | Version | Why |
|-------|--------|---------|-----|
| Runtime | Python | 3.11.9 | Latest stable with good ML ecosystem |
| Web framework | FastAPI | 0.111.0 | Async, auto OpenAPI docs, fast |
| ASGI server | Uvicorn | 0.30.1 | Production-grade ASGI |
| ORM | SQLAlchemy | 2.0.30 | Async ORM, type-safe |
| DB migrations | Alembic | 1.13.1 | Migration versioning |
| Data validation | Pydantic | 2.7.3 | FastAPI-native, V2 speed |
| Auth | PyJWT[crypto] | 2.8.0 | JWT encode/decode |
| Password hashing | passlib[bcrypt] | 1.7.4 | bcrypt hashing |
| Email | fastapi-mail | 1.4.1 | SMTP email dispatch |
| Scheduler | APScheduler | 3.10.4 | Cron-style data ingestion |
| HTTP client (ingestion) | httpx | 0.27.0 | Async HTTP for OpenMeteo API |
| PDF generation | ReportLab | 4.2.0 | Programmatic PDF |
| ML framework | XGBoost | 2.0.3 | Gradient boosting, fast inference |
| Data processing | pandas | 2.2.2 | Tabular data manipulation |
| NumPy | numpy | 1.26.4 | Numeric arrays |
| SHAP | shap | 0.45.1 | Feature attribution for explainability |
| ML tracking | MLflow | 2.13.1 | Model versioning (local) |
| Scikit-learn | scikit-learn | 1.5.0 | Preprocessing, metrics |

### Backend `.env`
```
DATABASE_URL=postgresql+asyncpg://episense:episense@db:5432/episense
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASS=your-app-password
OPENMETEO_BASE_URL=https://api.open-meteo.com/v1
MLFLOW_TRACKING_URI=http://mlflow:5000
ALERT_THRESHOLD_DEFAULT=70
```

---

## Database

| Choice | Version | Why |
|--------|---------|-----|
| PostgreSQL | 16.3 | Robust, JSON support, free |
| asyncpg driver | 0.29.0 | Async PostgreSQL driver for SQLAlchemy 2.0 |

---

## Infrastructure / DevOps

| Tool | Version | Role |
|------|---------|------|
| Docker | 26.1.4 | Containerisation |
| Docker Compose | 2.27.1 | Multi-service orchestration |
| Nginx | 1.27.0-alpine | Reverse proxy, static file serving |
| MLflow | 2.13.1 | Model tracking server (separate container) |

### Services in `docker-compose.yml`
```
db          → postgres:16.3-alpine         port 5432
backend     → custom Python image          port 8000
frontend    → node:20-alpine build → nginx port 3000
mlflow      → python:3.11-slim mlflow      port 5000
```

---

## External APIs (Free Tier)

| API | Purpose | Auth |
|-----|---------|------|
| Open-Meteo | Temperature, rainfall, humidity per lat/lon | None (free, no key) |

---

## Node / Python Versions

- Node.js: 20.14.0 (LTS Iron)
- npm: 10.7.0
- Python: 3.11.9
- pip: 24.0

---

## Development Tools

| Tool | Version |
|------|---------|
| ESLint | 8.57.0 |
| Prettier | 3.3.2 |
| Black (Python formatter) | 24.4.2 |
| isort | 5.13.2 |
| pytest | 8.2.2 |
| pytest-asyncio | 0.23.7 |
| Postman / Bruno | latest | API testing |
