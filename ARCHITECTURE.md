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
