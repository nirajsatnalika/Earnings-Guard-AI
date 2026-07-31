# EarningsGuard AI Backend

FastAPI foundation for the EarningsGuard™ AI enterprise fintech SaaS application.

## Current foundation

- FastAPI with OpenAPI, Swagger UI, and ReDoc
- SQLite and SQLAlchemy 2.x session infrastructure
- `.env` configuration through `python-dotenv`
- CORS middleware and centralized logging
- Global HTTP, validation, and unexpected exception handlers
- Application lifespan startup and shutdown hooks
- System endpoints: `/`, `/health`, and `/version`

Business logic, financial calculations, EFS™, Beneish analysis, spreadsheet parsing, persistence models, and authentication are intentionally not implemented.

## Run locally

```powershell
uvicorn app.main:app --reload
```

Swagger UI is available at `/docs`; the OpenAPI document is available at `/openapi.json`.

## Structure

- `app/api` — API route modules
- `app/core` — configuration, logging, and security concerns
- `app/database` — database setup and session management
- `app/models` — persistence models
- `app/schemas` — request and response schemas
- `app/services` — application services
- `app/calculations` — financial calculation modules
- `app/ai` — AI integration modules
- `app/reports` — report generation modules
- `app/utils` — shared utilities
- `tests` — backend tests
