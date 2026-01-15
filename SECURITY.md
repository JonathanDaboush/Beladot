# Security Model

## Threat Model
- Assume all external input is untrusted
- No secrets in code or logs
- All uploads validated (size, type, content)
- Centralized RBAC and policy enforcement

## Authentication & Authorization
- No auth logic in routes
- No trust in frontend
- All access via centralized policy

## Secrets
- No secrets in logs or exceptions
- Ready for secret rotation

## Other
- Rate limiting (global and per-route)
- Path traversal protection
- PII redaction in logs

---

See README.md for setup and ARCHITECTURE.md for boundaries.
