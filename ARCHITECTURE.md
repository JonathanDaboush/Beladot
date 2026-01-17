# Architecture

## Layered Boundaries

- **api/**: API routes only (no business logic)
- **services/**: Business logic only (no DB or HTTP)
- **repositories/**: DB access only (no business logic)
- **models/**: ORM models only
- **schemas/**: Pydantic schemas only
- **infrastructure/**: Email, storage, external APIs

## Responsibilities
- Each layer has a single responsibility and explicit dependencies.
- No cross-layer violations.

## Data Flow
- Request → api/ → services/ → repositories/ → models/
- Response → schemas/ → api/

## Example
- All DB access via repositories
- All business rules in services
- All input/output validation in schemas

---

See README.md for setup and SECURITY.md for security model.

## Guardrails

- **Repositories**: Do not use `.query()` on `AsyncSession`. Use `select()` + `execute()` and `scalars()`.
- **Async Sessions**: Obtain sessions from `backend.persistance.async_base.AsyncSessionLocal` only.
- **Imports**: Use `from sqlalchemy import select` (SQLAlchemy v2 style). Avoid `sqlalchemy.future`.
- **Schemas**: In Pydantic v2, avoid `constr(...)` in type hints. Prefer `Optional[str]` with `Field(min_length=..., max_length=...)`.
- **Separation**: Domain models are pure dataclasses; ORM models live under `backend/persistance`.
