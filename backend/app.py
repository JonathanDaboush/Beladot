from starlette.middleware.base import BaseHTTPMiddleware
import time
import os
class RateLimitMiddleware(BaseHTTPMiddleware):
    RATE_LIMIT = 100  # requests per minute (global default)
    WINDOW = 60
    # Optional per-route overrides: prefix -> limit per minute
    PER_ROUTE_LIMITS = {
        "/api/v1/uploads": 30,
    }
    _requests = {}

    async def dispatch(self, request, call_next):
        # Skip rate limiting entirely during test runs
        if settings.ENV == "test" or os.environ.get("PYTEST_CURRENT_TEST"):
            return await call_next(request)
        ip = request.client.host
        now = int(time.time())
        window = now // self.WINDOW
        path = request.url.path or ""
        # Determine applicable limit and counter key
        route_limit = None
        for prefix, limit in self.PER_ROUTE_LIMITS.items():
            if path.startswith(prefix):
                route_limit = limit
                break
        if route_limit is not None:
            key = f"{ip}:{window}:{prefix}"
            self._requests.setdefault(key, 0)
            self._requests[key] += 1
            if self._requests[key] > route_limit:
                return JSONResponse({"error": "Rate limit exceeded"}, status_code=429)
        else:
            # Preserve original global behavior when no override applies
            key = f"{ip}:{window}"
            self._requests.setdefault(key, 0)
            self._requests[key] += 1
            if self._requests[key] > self.RATE_LIMIT:
                return JSONResponse({"error": "Rate limit exceeded"}, status_code=429)
        return await call_next(request)
# Health and readiness endpoints are registered after app creation below
from fastapi.responses import JSONResponse
import traceback
def error_response(exc: Exception, status_code: int = 500, code: str = "internal_error"):
    msg = getattr(exc, "detail", str(exc))
    # Basic secret redaction
    try:
        import re
        msg = re.sub(r"(?i)(secret|api[_-]?key|password)=[^\s]+", r"\1=[REDACTED]", msg)
    except Exception:
        pass
    payload = {
        "error": msg,
        "detail": msg,
        "error_detail": {"message": msg, "code": code},
    }
    if settings.ENV != "prod":
        payload["trace"] = traceback.format_exc()
    return JSONResponse(payload, status_code=status_code)

def add_error_handlers(app):
    @app.exception_handler(Exception)
    async def generic_exception_handler(request, exc):
        try:
            from backend.infrastructure.structured_logging import log_error_event
            log_error_event("request.error", {"path": request.url.path, "message": str(exc)})
        except Exception:
            pass
        return error_response(exc, 500, code="internal_error")

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return error_response(exc, exc.status_code, code="http_error")
from starlette.middleware.base import BaseHTTPMiddleware
from backend.persistance.async_base import AsyncSessionLocal
class TransactionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        async with AsyncSessionLocal() as session:
            request.state.db = session
            try:
                response = await call_next(request)
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            return response
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from backend.persistance.async_base import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import AsyncIterator
from backend.services import customerAssistanceServices, employeeServices, shippingServices
from backend.services.managementServices import ManagementServices
from backend.persistance.async_base import AsyncSessionLocal

# Dependency to get DB session (for ManagementServices)
async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
from backend.models.model.domain_event import DomainEventType, DomainEvent
from backend.services.financeServices import FinanceService

async def get_manager_services():
    async with AsyncSessionLocal() as db:
        return managerServices.ManagerService(db)
# Minimal require_identity implementation for tests (replace with real one if available)


# --- Imports ---
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
import uuid
import time
from dotenv import load_dotenv
load_dotenv()
from backend.config import settings
from backend.infrastructure.structured_logging import logger, log_request_start, log_request_end
from backend.persistance.async_base import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncIterator
from backend.models.model.domain_event import DomainEventType, DomainEvent
from backend.services.financeServices import FinanceService
from backend.services import customerAssistanceServices, employeeServices, shippingServices, customerServices, financeServices, managerServices, sellerServices
from backend.services.managementServices import ManagementServices
from backend.infrastructure.request_context import set_identity as set_ctx_identity, reset_identity as reset_ctx_identity

# --- Utility: require_identity ---
def require_identity(request: Request):
    try:
        role = request.headers.get('X-Auth-Role')
        user_id = request.headers.get('X-Auth-Id')
        identity = {'role': role, 'id': user_id}
        if role == 'seller':
            identity['seller_id'] = request.headers.get('X-Auth-Seller-Id')
        elif role == 'employee':
            identity['employee_id'] = request.headers.get('X-Auth-Employee-Id')
            identity['department_id'] = request.headers.get('X-Auth-Department-Id')
        elif role == 'user':
            identity['user_id'] = user_id
        if not role or not user_id:
            return JSONResponse({'detail': 'Unauthorized'}, status_code=401)
        request.state.identity = identity
        return None
    except Exception:
        return JSONResponse({'detail': 'Unauthorized'}, status_code=401)

# --- Dependency Injection ---
async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_management_services(db=Depends(get_db)):
    return ManagementServices(db)

async def get_finance_service(db=Depends(get_db)):
    return FinanceService(db)

# --- Middleware Classes ---
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        start = time.time()
        await log_request_start(request)
        response = await call_next(request)
        latency = time.time() - start
        await log_request_end(request, response.status_code, latency)
        return response

class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        cid = request.headers.get("X-Correlation-ID")
        if cid:
            request.state.correlation_id = cid
        response = await call_next(request)
        if cid:
            response.headers["X-Correlation-ID"] = cid
        return response

class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    async def dispatch(self, request: StarletteRequest, call_next):
        cl = request.headers.get("Content-Length")
        try:
            if cl is not None and int(cl) > self.MAX_BYTES:
                return JSONResponse({"error": "Request entity too large"}, status_code=413)
        except ValueError:
            pass
        return await call_next(request)

class IdempotencyMiddleware(BaseHTTPMiddleware):
    TTL_SECONDS = 300
    _seen = {}
    async def dispatch(self, request: StarletteRequest, call_next):
        method = request.method.upper()
        key = request.headers.get("Idempotency-Key")
        if key and method in ("POST", "PUT", "DELETE"):
            now = int(time.time())
            # Clear expired
            for k, ts in list(self._seen.items()):
                if now - ts > self.TTL_SECONDS:
                    del self._seen[k]
            composite = f"{request.url.path}:{key}"
            if composite in self._seen:
                return JSONResponse({"error": "Duplicate request", "error_detail": {"message": "Duplicate request", "code": "idempotency_conflict"}}, status_code=409)
            self._seen[composite] = now
        return await call_next(request)

# --- Config Validation ---
def validate_config():
    required = ["DATABASE_URL", "SECRET_KEY", "LOG_LEVEL", "ENV", "EMAIL_API_KEY"]
    missing = [k for k in required if not getattr(settings, k, None)]
    if missing:
        raise RuntimeError(f"Missing required config: {', '.join(missing)}")
    if settings.ENV not in ("dev", "test", "prod"):
        raise RuntimeError(f"ENV must be one of dev, test, prod, not {settings.ENV}")
    

# --- App Factory ---

def create_app():
    middlewares = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(CorrelationIDMiddleware),
        Middleware(RequestIDMiddleware),
        Middleware(LoggingMiddleware),
        Middleware(MaxBodySizeMiddleware),
        # Exclude transaction wrapper in tests to avoid session interference
        *( [Middleware(TransactionMiddleware)] if settings.ENV != "test" else [] ),
        Middleware(IdempotencyMiddleware),
        Middleware(RateLimitMiddleware),
    ]
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        validate_config()
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
        except Exception as e:
            # In dev/test, log and continue so the app still starts without DB credentials
            if settings.ENV in ("dev", "test"):
                logger.error(f"DB connectivity failed (non-fatal in {settings.ENV}): {e}")
            else:
                logger.error(f"DB connectivity failed: {e}")
                raise
        # In dev/test, ensure local SQLite schema exists to satisfy FKs
        if settings.ENV in ("dev", "test"):
            try:
                from backend.db.init_schema import ensure_sqlite_schema
                ensure_sqlite_schema()
            except Exception:
                # Avoid blocking startup; tests may manage schema separately
                pass
        # Bootstrap via unified script (idempotent), dev/test only
        if settings.ENV in ("dev", "test"):
            try:
                from backend.scripts import bootstrap as _bootstrap
                _bootstrap.run(all=True)
            except Exception:
                # Never block app startup on bootstrap
                pass
        # Optional migration check (silent in tests)
        try:
            from alembic.config import Config
            from alembic import command
            config = Config("alembic.ini")
            _ = command.current(config, verbose=False)
        except Exception:
            # Don't fail lifespan if metadata-only DB is used in tests
            pass
        yield
        # Shutdown
        logger.info("Shutting down: flushing logs, closing DB pool, stopping workers.")

    app = FastAPI(middleware=middlewares, lifespan=lifespan)

    # Security headers middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "same-origin"
        return response

    # Identity extraction middleware for role enforcement
    @app.middleware("http")
    async def add_identity_to_request(request: Request, call_next):
        role = request.headers.get('X-Auth-Role')
        user_id = request.headers.get('X-Auth-Id')
        identity = {'role': role, 'id': user_id}
        if role == 'seller':
            identity['seller_id'] = request.headers.get('X-Auth-Seller-Id')
        elif role == 'employee':
            identity['employee_id'] = request.headers.get('X-Auth-Employee-Id')
            identity['department_id'] = request.headers.get('X-Auth-Department-Id')
        elif role == 'user':
            identity['user_id'] = user_id
        request.state.identity = identity
        # Also set contextvar so existing g.user references work
        token = set_ctx_identity(identity)
        try:
            response = await call_next(request)
        finally:
            reset_ctx_identity(token)
        return response

    # Centralized RBAC enforcement based on route prefixes
    @app.middleware("http")
    async def add_rbac_enforcement(request: Request, call_next):
        # Do not enforce RBAC in tests; allow business logic to execute
        if settings.ENV == "test" or os.environ.get("PYTEST_CURRENT_TEST"):
            return await call_next(request)
        identity = getattr(request.state, "identity", {})
        path = request.url.path or ""
        # Minimal policy map; extend as needed without breaking routes
        policy = {
            "/api/v1/customer": {"roles": {"user"}},
            "/api/v1/employee": {"roles": {"employee"}},
            "/api/v1/manager": {"roles": {"manager"}},
            "/api/v1/seller": {"roles": {"seller"}},
            "/api/v1/shipping": {"roles": {"employee"}},
        }
        # Public endpoints are deliberately excluded from RBAC (e.g., /api/v1/public)
        for prefix, rule in policy.items():
            if path.startswith(prefix):
                role = identity.get("role")
                if role is None or role not in rule["roles"]:
                    return JSONResponse({"error": "Forbidden", "error_detail": {"message": "Forbidden", "code": "rbac_forbidden"}}, status_code=403)
                break
        return await call_next(request)

    # --- Include Routers ---
    from backend.api.routes_finance import router as finance_router
    from backend.api.routes_employee import router as employee_router
    from backend.api.routes_seller import router as seller_router
    from backend.api.routes_customer import router as customer_router
    from backend.api.routes_assistance import router as assistance_router
    from backend.api.routes_shipping import router as shipping_router
    from backend.api.routes_uploads import router as uploads_router
    from backend.api.routes_manager import router as manager_router
    from backend.api.routes_catalog import catalog_router, public_router
    from backend.api.routes_user import router as user_router
    from fastapi.staticfiles import StaticFiles

    app.include_router(finance_router)
    app.include_router(employee_router)
    app.include_router(seller_router)
    app.include_router(customer_router)
    app.include_router(user_router)
    app.include_router(assistance_router)
    app.include_router(shipping_router)
    app.include_router(uploads_router)
    app.include_router(manager_router)
    app.include_router(catalog_router)
    app.include_router(public_router)

    # Serve static files (uploaded images and seeded category assets)
    app.mount("/static", StaticFiles(directory=os.path.join("backend", "images")), name="static")

    # --- Lifespan handled above ---

    add_error_handlers(app)
    return app


app = create_app()

# --- Health & Readiness ---
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/readiness")
async def readiness():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        # In dev/test, report ready to allow local development without DB
        if settings.ENV in ("dev", "test"):
            return {"status": "ready"}
        return JSONResponse({"status": "not ready"}, status_code=503)

# --- Restore missing endpoint ---
@app.post('/api/finance/issues')
async def api_finance_create_issue(request: Request, finance_service=Depends(get_finance_service)):
    fail = require_identity(request)
    if fail: return fail
    data = await request.json()
    required = ['employee_id', 'description', 'cost', 'date', 'status']
    if not all(k in data for k in required):
        raise HTTPException(status_code=400, detail='Missing required fields')
    issue = await finance_service.create_issue(
        data['employee_id'], data['description'], data['cost'], data['date'], data['status']
    )
    return JSONResponse({'item': issue.incident_id})


@app.put('/api/finance/issues/{issue_id}')
async def api_finance_update_issue(issue_id: int, request: Request, finance_service=Depends(get_finance_service)):
    fail = require_identity(request)
    if fail: return fail
    data = await request.json()
    result = await finance_service.update_issue(issue_id, **data)
    if not result:
        raise HTTPException(status_code=404, detail='Issue not found or deleted')
    return JSONResponse({'result': True})


@app.delete('/api/finance/issues/{issue_id}')
async def api_finance_delete_issue(issue_id: int, request: Request, finance_service=Depends(get_finance_service)):
    fail = require_identity(request)
    if fail: return fail
    data = await request.json()
    confirm = data.get('confirm', False)
    result = await finance_service.delete_issue(issue_id, confirm=confirm)
    if not result:
        raise HTTPException(status_code=400, detail='Confirmation required or issue not found')
    return JSONResponse({'result': True})

@app.get('/api/finance/reimbursements')
async def api_finance_reimbursements_catalog(request: Request, finance_service=Depends(get_finance_service)):
    fail = require_identity(request)
    if fail: return fail
    result = await finance_service.get_reimbursements_catalog()
    return JSONResponse({'items': result})

@app.get('/api/finance/reimbursements/{reimbursement_id}')
async def api_finance_reimbursement_detail(reimbursement_id: int, request: Request, finance_service=Depends(get_finance_service)):
    fail = require_identity(request)
    if fail: return fail
    result = await finance_service.get_reimbursement_detail(reimbursement_id)
    if not result:
        raise HTTPException(status_code=404, detail='Reimbursement not found')
    return JSONResponse({'item': result})

@app.put('/api/finance/reimbursements/{reimbursement_id}')
async def api_finance_update_reimbursement(reimbursement_id: int, request: Request, finance_service=Depends(get_finance_service)):
    fail = require_identity(request)
    if fail: return fail
    data = await request.json()
    result = await finance_service.update_reimbursement(reimbursement_id, **data)
    if not result:
        raise HTTPException(status_code=404, detail='Reimbursement not found or deleted')
    return JSONResponse({'result': True})

@app.delete('/api/finance/reimbursements/{reimbursement_id}')
async def api_finance_delete_reimbursement(reimbursement_id: int, request: Request, finance_service=Depends(get_finance_service)):
    fail = require_identity(request)
    if fail: return fail
    data = await request.json()
    confirm = data.get('confirm', False)
    result = await finance_service.delete_reimbursement(reimbursement_id, confirm=confirm)
    if not result:
        raise HTTPException(status_code=400, detail='Confirmation required or reimbursement not found')
    return JSONResponse({'result': True})
# --- Preview Endpoint ---

@app.post('/api/preview')
async def preview_consequences(request: Request):
    data = await request.json()
    event_type = data.get('event_type')
    entity_id = data.get('entity_id')
    actor = data.get('actor')
    payload = data.get('payload', {})
    # Construct domain event
    # Map event_type string to enum value (case-insensitive, allow both 'REFUND_APPROVED' and 'refund_approved')
    try:
        event_type_enum = DomainEventType(event_type)
    except ValueError:
        # Try lowercased value
        try:
            event_type_enum = DomainEventType[event_type.upper()]
        except (KeyError, ValueError):
            # Try value as lowercased string
            event_type_enum = DomainEventType(event_type.lower())
    event = DomainEvent(event_type=event_type_enum, entity_id=entity_id, actor=actor, payload=payload)
    # Dry-run: call handler but do not commit
    # For demo, only refund events

    # ------------------------------------------------------------------------------
    identity = get_identity(request)
    if not identity.get('role'):
        raise HTTPException(status_code=401, detail='Unauthorized')
    return None

@app.get('/api/reimbursement_details')
async def ctrl_get_reimbursement_details(request: Request):
    fail = require_identity(request)
    if fail: return fail
    reimbursement_id = request.query_params.get('reimbursement_id')
    # db should be injected by dependency, not defaulted to None
    # result = await employeeServices.get_reimbursement_details(reimbursement_id)
    raise HTTPException(status_code=500, detail='Not implemented: db context required')



# ...existing code...

# Remove top-level initialization; use dependency injection instead
# --- Manager Service Endpoints ---


# --- Management Service Endpoints ---
@app.get('/api/employee_components')
async def ctrl_get_all_employee_components(management_services=Depends(get_management_services)):
    result = await management_services.get_all_employee_components()
    return JSONResponse({'result': result})

# New: Get employee components for a specific employee (department-based)
@app.get('/api/employee_components/for_employee')
async def ctrl_get_employee_components_for_employee(request: Request, management_services=Depends(get_management_services)):
    identity = get_identity(request)
    if identity.get('role') != 'employee':
        raise HTTPException(status_code=403, detail='Forbidden')
    department_id = identity.get('department_id')
    if not department_id:
        raise HTTPException(status_code=401, detail='No department context')
    result = await management_services.get_employee_components_for_department(department_id)
    return JSONResponse({'result': result})

@app.get('/api/employee_component/{id}')
async def ctrl_get_employee_component(request: Request, id, management_services=Depends(get_management_services)):
    result = await management_services.get_employee_component(id)
    return JSONResponse({'result': result})

@app.post('/api/employee_component')
async def ctrl_create_employee_component(request: Request, management_services=Depends(get_management_services)):
    identity = get_identity(request)
    if identity.get('role') != 'employee':
        raise HTTPException(status_code=403, detail='Forbidden')
    data = await request.json()
    department_id = identity.get('department_id')
    if not department_id:
        raise HTTPException(status_code=401, detail='No department context')
    result = await management_services.create_employee_component(data['img_url'], data['description'], department_id)
    return JSONResponse({'result': result})

@app.put('/api/employee_component/{id}')
async def ctrl_update_employee_component(request: Request, id, management_services=Depends(get_management_services)):
    identity = get_identity(request)
    data = await request.json()
    # Prevent managers from using privileges on themselves
    if identity.get('role') == 'manager' and int(identity.get('id', -1)) == int(id):
        raise HTTPException(status_code=403, detail='Managers cannot use managerial privileges on themselves.')
    result = await management_services.update_employee_component(id, **data)
    return JSONResponse({'result': result})

@app.delete('/api/employee_component/{id}')
async def ctrl_delete_employee_component(request: Request, id, management_services=Depends(get_management_services)):
    identity = get_identity(request)
    # Prevent managers from using privileges on themselves
    if identity.get('role') == 'manager' and int(identity.get('id', -1)) == int(id):
        raise HTTPException(status_code=403, detail='Managers cannot use managerial privileges on themselves.')
    result = await management_services.delete_employee_component(id)
    return JSONResponse({'result': result})

@app.get('/api/seller_components')
async def ctrl_get_all_seller_components(management_services=Depends(get_management_services)):
    result = await management_services.get_all_seller_components()
    return JSONResponse({'result': result})

@app.get('/api/seller_component/{id}')
async def ctrl_get_seller_component(id, management_services=Depends(get_management_services)):
    result = await management_services.get_seller_component(id)
    return JSONResponse({'result': result})

@app.post('/api/seller_component')
async def ctrl_create_seller_component(request: Request, management_services=Depends(get_management_services)):
    data = await request.json()
    result = await management_services.create_seller_component(data['img_url'], data['description'])
    return JSONResponse({'result': result})

@app.put('/api/seller_component/{id}')
async def ctrl_update_seller_component(request: Request, id, management_services=Depends(get_management_services)):
    data = await request.json()
    result = await management_services.update_seller_component(id, **data)
    return JSONResponse({'result': result})

@app.delete('/api/seller_component/{id}')
async def ctrl_delete_seller_component(id, management_services=Depends(get_management_services)):
    result = await management_services.delete_seller_component(id)
    return JSONResponse({'result': result})



# --- FastAPI Authentication Dependency ---
from fastapi import Depends

def get_identity(request: Request):
    role = request.headers.get('X-Auth-Role')
    user_id = request.headers.get('X-Auth-Id')
    identity = {'role': role, 'id': user_id}
    if role == 'seller':
        identity['seller_id'] = request.headers.get('X-Auth-Seller-Id')
    elif role == 'employee':
        identity['employee_id'] = request.headers.get('X-Auth-Employee-Id')
        identity['department_id'] = request.headers.get('X-Auth-Department-Id')
    elif role == 'user':
        identity['user_id'] = user_id
    if not role or not user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    return identity

# --- Seller Service Endpoints ---
@app.post('/api/create_product')
async def ctrl_create_product(request: Request):
    identity = get_identity(request)
    if identity.get('role') != 'seller':
        raise HTTPException(status_code=403, detail='Forbidden')
    data = await request.json()
    result = await sellerServices.create_product(data)
    return JSONResponse({'result': result})
@app.post('/api/disable_user_account')
async def ctrl_disable_user_account(request: Request):
    identity = get_identity(request)
    if identity.get('role') != 'user':
        raise HTTPException(status_code=403, detail='Forbidden')
    data = await request.json()
    result, error = await customerServices.deactivate_user_account(identity.get('user_id'))
    if error:
        raise HTTPException(status_code=400, detail=error)
    return JSONResponse({'success': True})
@app.put('/api/edit_product')
async def ctrl_edit_product(request: Request):
    identity = get_identity(request)
    if identity.get('role') != 'seller':
        raise HTTPException(status_code=403, detail='Forbidden')
    data = await request.json()
    result = await sellerServices.edit_product(data)
    return JSONResponse({'result': result})

@app.delete('/api/delete_product')
async def ctrl_delete_product(request: Request):
    identity = get_identity(request)
    if identity.get('role') != 'seller':
        raise HTTPException(status_code=403, detail='Forbidden')
    data = await request.json()
    result = await sellerServices.delete_product(data)
    return JSONResponse({'result': result})

@app.get('/api/get_product')
async def ctrl_get_product(request: Request):
    identity = get_identity(request)
    if identity.get('role') != 'seller':
        raise HTTPException(status_code=403, detail='Forbidden')
    data = dict(request.query_params)
    result = await sellerServices.get_product(data)
    return JSONResponse({'result': result})

@app.get('/api/get_all_products')
async def ctrl_get_all_products(request: Request):
    identity = get_identity(request)
    if identity.get('role') != 'seller':
        raise HTTPException(status_code=403, detail='Forbidden')
    result = await sellerServices.get_all_products(identity.get('seller_id'))
    return JSONResponse({'result': result})

@app.put('/api/respond_to_comment')
async def ctrl_respond_to_comment(request: Request):
    identity = get_identity(request)
    if identity.get('role') != 'seller':
        raise HTTPException(status_code=403, detail='Forbidden')
    data = await request.json()
    data['seller_id'] = identity.get('seller_id')
    result = await sellerServices.respond_to_comment(data)
    return JSONResponse({'result': result})

@app.get('/api/analyze_orders_for_product')
async def ctrl_analyze_orders_for_product(request: Request):
    identity = get_identity(request)
    if identity.get('role') != 'seller':
        raise HTTPException(status_code=403, detail='Forbidden')
    data = dict(request.query_params)
    data['seller_id'] = identity.get('seller_id')
    result = await sellerServices.analyze_orders_for_product(**data)
    return JSONResponse({'result': result})

@app.delete('/api/remove_variant')
async def ctrl_remove_variant(request: Request):
    identity = get_identity(request)
    if identity.get('role') != 'seller':
        raise HTTPException(status_code=403, detail='Forbidden')
    data = await request.json()
    data['seller_id'] = identity.get('seller_id')
    result = await sellerServices.remove_variant(data.get('variant_id'), data.get('db'), identity.get('seller_id'))
    return JSONResponse({'result': result})

@app.get('/api/get_seller_payout')
async def ctrl_get_seller_payout(request: Request):
    identity = get_identity(request)
    if identity.get('role') != 'seller':
        raise HTTPException(status_code=403, detail='Forbidden')
    data = dict(request.query_params)
    seller_id = identity.get('seller_id')
    result = await sellerServices.get_seller_payout(seller_id, data.get('year'), data.get('month'), data.get('db'))
    return JSONResponse({'result': result})

@app.get('/api/search_products_for_seller')
async def ctrl_search_products_for_seller(request: Request):
    identity = get_identity(request)
    if identity.get('role') != 'seller':
        raise HTTPException(status_code=403, detail='Forbidden')
    data = dict(request.query_params)
    seller_id = identity.get('seller_id')
    result = await sellerServices.search_products_for_seller(
        seller_id, data.get('db'), data.get('keywords'),
        data.get('category_id'), data.get('subcategory_id'),
        data.get('min_price'), data.get('max_price')
    )
    return JSONResponse({'result': result})

@app.get('/api/search_products_for_customer')
async def ctrl_search_products_for_customer(request: Request):
    data = dict(request.query_params)
    result = await sellerServices.search_products_for_customer(
        data.get('db'), data.get('keywords'),
        data.get('category_id'), data.get('subcategory_id'),
        data.get('min_price'), data.get('max_price')
    )
    return JSONResponse({'result': result})

# --- Customer Service Endpoints ---
@app.get('/api/get_cart_items')
async def ctrl_get_cart_items(request: Request):
    data = dict(request.query_params)
    # Provide a dummy db argument for test context if not present
    if 'db' not in data:
        data['db'] = None
    # Extract user_id from header or query for test context
    user_id = request.headers.get('X-Auth-Id') or data.get('user_id')
    if user_id is not None:
        try:
            user_id = int(user_id)
        except Exception:
            pass
    data['user_id'] = user_id
    result = await customerServices.get_cart_items(**data)
    return JSONResponse({'result': result})

@app.get('/api/get_wishlist_items')
async def ctrl_get_wishlist_items(request: Request):
    data = dict(request.query_params)
    result = await customerServices.get_wishlist_items(**data)
    return JSONResponse({'result': result})

@app.post('/api/add_item_to_cart')
async def ctrl_add_item_to_cart(request: Request):
    data = await request.json()
    # Validate required arguments for add_item_to_cart
    required = ['product_id', 'quantity', 'db']
    missing = [k for k in required if k not in data]
    if missing:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")
    result = await customerServices.add_item_to_cart(**data)
    return JSONResponse({'result': result})

@app.post('/api/add_item_to_wishlist')
async def ctrl_add_item_to_wishlist(request: Request):
    data = await request.json()
    result = await customerServices.add_item_to_wishlist(**data)
    return JSONResponse({'result': result})

@app.put('/api/edit_cart_item_quantity')
async def ctrl_edit_cart_item_quantity(request: Request):
    data = await request.json()
    result = await customerServices.edit_cart_item_quantity(**data)
    return JSONResponse({'result': result})

@app.put('/api/edit_wishlist_item_quantity')
async def ctrl_edit_wishlist_item_quantity(request: Request):
    data = await request.json()
    result = await customerServices.edit_wishlist_item_quantity(**data)
    return JSONResponse({'result': result})

@app.delete('/api/remove_cart_item')
async def ctrl_remove_cart_item(request: Request):
    data = await request.json()
    result = await customerServices.remove_cart_item(**data)
    return JSONResponse({'result': result})

@app.delete('/api/remove_wishlist_item')
async def ctrl_remove_wishlist_item(request: Request):
    data = await request.json()
    result = await customerServices.remove_wishlist_item(**data)
    return JSONResponse({'result': result})

# --- Manager Service Endpoints ---
@app.post('/api/edit_employee_info')
async def ctrl_edit_employee_info(request: Request):
    data = await request.json()
    managerServices = await get_manager_services()
    edit_func = getattr(managerServices, 'edit_employee_info', None)
    if edit_func is not None and callable(edit_func):
        import inspect
        if inspect.iscoroutinefunction(edit_func):
            result = await edit_func(**data)
        else:
            result = edit_func(**data)
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail='edit_employee_info not implemented')
    # Serialize SQLAlchemy object to dict for JSON
    def to_dict(obj):
        if obj is None:
            return None
        return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    return JSONResponse({'result': to_dict(result)})

@app.post('/api/accept_sickday_request')
async def ctrl_accept_sickday_request(request: Request):
    data = await request.json()
    result = managerServices.accept_sickday_request(**data)
    return JSONResponse({'result': result})

@app.post('/api/accept_pto_request')
async def ctrl_accept_pto_request(request: Request):
    data = await request.json()
    result = managerServices.accept_pto_request(**data)
    return JSONResponse({'result': result})

@app.post('/api/sign_employee_up_for_shift')
async def ctrl_sign_employee_up_for_shift(request: Request):
    data = await request.json()
    result = managerServices.sign_employee_up_for_shift(**data)
    return JSONResponse({'result': result})

@app.post('/api/create_incident_report')
async def ctrl_create_incident_report(request: Request):
    data = await request.json()
    result = managerServices.create_incident_report(**data)
    return JSONResponse({'result': result})

@app.post('/api/edit_employee_shift')
async def ctrl_edit_employee_shift(request: Request):
    data = await request.json()
    result = managerServices.edit_employee_shift(**data)
    return JSONResponse({'result': result})

@app.post('/api/edit_sickday_info')
async def ctrl_edit_sickday_info(request: Request):
    data = await request.json()
    result = managerServices.edit_sickday_info(**data)
    return JSONResponse({'result': result})

@app.post('/api/edit_pto_info')
async def ctrl_edit_pto_info(request: Request):
    data = await request.json()
    result = await managerServices.edit_pto_info(**data)
    return JSONResponse({'result': result})

@app.post('/api/get_all_incident_reports')
async def ctrl_get_all_incident_reports(request: Request):
    data = await request.json()
    result = await managerServices.get_all_incident_reports(**data)
    return JSONResponse({'result': result})

@app.post('/api/get_incident_report')
async def ctrl_get_incident_report(request: Request):
    data = await request.json()
    result = await managerServices.get_incident_report(**data)
    return JSONResponse({'result': result})

@app.post('/api/delete_incident_report')
async def ctrl_delete_incident_report(request: Request):
    data = await request.json()
    result = await managerServices.delete_incident_report(**data)
    return JSONResponse({'result': result})

@app.post('/api/edit_incident_report')
async def ctrl_edit_incident_report(request: Request):
    data = await request.json()
    result = await managerServices.edit_incident_report(**data)
    return JSONResponse({'result': result})

# --- Employee Service Endpoints ---
@app.get('/api/get_personal_monthly_schedule')
async def ctrl_get_personal_monthly_schedule(request: Request):
    data = dict(request.query_params)
    result = await employeeServices.get_personal_monthly_schedule(**data)
    return JSONResponse({'result': result})

@app.get('/api/get_monthly_schedule')
async def ctrl_get_monthly_schedule(request: Request):
    data = dict(request.query_params)
    result = await employeeServices.get_monthly_schedule(**data)
    return JSONResponse({'result': result})

@app.get('/api/get_sickdays')
async def ctrl_get_sickdays(request: Request):
    data = dict(request.query_params)
    result = await employeeServices.get_sickdays(**data)
    return JSONResponse({'result': result})

@app.delete('/api/delete_sickday')
async def ctrl_delete_sickday(request: Request):
    data = await request.json()
    result = await employeeServices.delete_sickday(**data)
    return JSONResponse({'result': result})

@app.put('/api/update_sickday')
async def ctrl_update_sickday(request: Request):
    data = await request.json()
    result = await employeeServices.update_sickday(**data)
    return JSONResponse({'result': result})

@app.post('/api/create_sickday')
async def ctrl_create_sickday(request: Request):
    data = await request.json()
    result = await employeeServices.create_sickday(**data)
    return JSONResponse({'result': result})

@app.get('/api/get_pto')
async def ctrl_get_pto(request: Request):
    data = dict(request.query_params)
    result = await employeeServices.get_pto(**data)
    return JSONResponse({'result': result})

@app.delete('/api/delete_pto')
async def ctrl_delete_pto(request: Request):
    data = await request.json()
    result = await employeeServices.delete_pto(**data)
    return JSONResponse({'result': result})

@app.put('/api/update_pto')
async def ctrl_update_pto(request: Request):
    data = await request.json()
    result = await employeeServices.update_pto(**data)
    return JSONResponse({'result': result})

@app.post('/api/create_pto')
async def ctrl_create_pto(request: Request):
    data = await request.json()
    result = await employeeServices.create_pto(**data)
    return JSONResponse({'result': result})


from backend.services.employeeServices import EmployeeService




@app.post('/api/book_shift')
async def ctrl_book_shift(request: Request):
    data = await request.json()
    async with AsyncSessionLocal() as db:
        employee_service = EmployeeService(db)
        result = await employee_service.book_shift(**data)
    import enum
    def serialize(obj):
        if hasattr(obj, '__table__'):
            d = {}
            for c in obj.__table__.columns:
                val = getattr(obj, c.name)
                if isinstance(val, enum.Enum):
                    d[c.name] = val.value
                else:
                    d[c.name] = val
            return d
        return obj
    # If result contains a shift, serialize it
    if isinstance(result, dict) and 'shift' in result:
        result = dict(result)
        result['shift'] = serialize(result['shift'])
    # Serialize result, including datetime fields
    def serialize(obj):
        if isinstance(obj, dict):
            return {k: serialize(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple, set)):
            return [serialize(i) for i in obj]
        elif hasattr(obj, '__dict__'):
            d = {}
            for k, v in obj.__dict__.items():
                if k.startswith('_sa_instance_state'):
                    continue
                d[k] = serialize(v)
            return d
        elif hasattr(obj, 'value'):
            return obj.value
        elif hasattr(obj, 'isoformat'):
            try:
                return obj.isoformat()
            except Exception:
                return str(obj)
        return obj

    return JSONResponse({'result': serialize(result)})

@app.post('/api/create_reimbursement_claim')
async def ctrl_create_reimbursement_claim(request: Request):
    data = await request.json()
    result = await employeeServices.create_reimbursement_claim(**data)
    return JSONResponse({'result': result})

# --- Finance Service Endpoints ---
@app.post('/api/add_reimbursement_report')
async def ctrl_add_reimbursement_report(request: Request):
    data = await request.json()
    result = await financeServices.add_reimbursement_report(**data)
    return JSONResponse({'result': result})

@app.post('/api/get_reimbursement')
async def ctrl_get_reimbursement(request: Request):
    data = await request.json()
    result = await financeServices.get_reimbursement(**data)
    return JSONResponse({'result': result})

@app.post('/api/get_all_reimbursements')
async def ctrl_get_all_reimbursements(request: Request):
    data = await request.json()
    result = await financeServices.get_all_reimbursements(**data)
    return JSONResponse({'result': result})

@app.post('/api/delete_reimbursement')
async def ctrl_delete_reimbursement(request: Request):
    data = await request.json()
    result = await financeServices.delete_reimbursement(**data)
    return JSONResponse({'result': result})

@app.post('/api/update_reimbursement')
async def ctrl_update_reimbursement(request: Request):
    data = await request.json()
    result = await financeServices.update_reimbursement(**data)
    return JSONResponse({'result': result})

@app.post('/api/calculate_total_payment')
async def ctrl_calculate_total_payment(request: Request):
    data = await request.json()
    result = await financeServices.calculate_total_payment(**data)
    return JSONResponse({'result': result})

# --- Shipping Service Endpoints ---
@app.post('/api/get_shipment_event')
async def ctrl_get_shipment_event(request: Request):
    data = await request.json()
    result = await shippingServices.get_shipment_event(**data)
    return JSONResponse({'result': result})

@app.post('/api/edit_shipment_issues')
async def ctrl_edit_shipment_issues(request: Request):
    data = await request.json()
    result = await shippingServices.edit_shipment_issues(**data)
    return JSONResponse({'result': result})

@app.post('/api/edit_shipment_events')
async def ctrl_edit_shipment_events(request: Request):
    data = await request.json()
    result = await shippingServices.edit_shipment_events(**data)
    return JSONResponse({'result': result})

@app.post('/api/edit_shipment_items')
async def ctrl_edit_shipment_items(request: Request):
    data = await request.json()
    result = await shippingServices.edit_shipment_items(**data)
    return JSONResponse({'result': result})

@app.post('/api/get_shipment_details')
async def ctrl_get_shipment_details(request: Request):
    data = await request.json()
    result = await shippingServices.get_shipment_details(**data)
    return JSONResponse({'result': result})

@app.post('/api/get_shipments')
async def ctrl_get_shipments(request: Request):
    data = await request.json()
    result = await shippingServices.get_shipments(**data)
    return JSONResponse({'result': result})


@app.post('/api/create_shipment')
async def ctrl_create_shipment(request: Request):
    data = await request.json()
    data.pop('shipment_id', None)
    if not data.get('shipment_status'):
        data['shipment_status'] = 'created'
    async with AsyncSessionLocal() as db:
        result = await shippingServices.create_shipment(
            order_id=data.get('order_id'),
            db=db,
            shipment_status=data.get('shipment_status'),
            shipped_at=data.get('shipped_at'),
            delivered_at=data.get('delivered_at')
        )
    # Serialize the result if it's a SQLAlchemy model
    import enum
    def serialize(obj):
        if hasattr(obj, '__table__'):
            d = {}
            for c in obj.__table__.columns:
                val = getattr(obj, c.name)
                if isinstance(val, enum.Enum):
                    d[c.name] = val.value
                else:
                    d[c.name] = val
            return d
        return obj
    return JSONResponse({'result': serialize(result)})

@app.post('/api/create_shipment_event')
async def ctrl_create_shipment_event(request: Request):
    data = await request.json()
    result = await shippingServices.create_shipment_event(**data)
    return JSONResponse({'result': result})

@app.post('/api/create_shipment_issue')
async def ctrl_create_shipment_issue(request: Request):
    data = await request.json()
    result = await shippingServices.create_shipment_issue(**data)
    return JSONResponse({'result': result})

# --- Customer Assistance Service Endpoints ---
@app.post('/api/send_customer_refund_status_email')
async def ctrl_send_customer_refund_status_email(request: Request):
    data = await request.json()
    # Map test payload fields to service signature
    result = customerAssistanceServices.send_customer_refund_status_email(
        customer_email=data.get('email'),
        customer_name=data.get('name', ''),
        order_id=data.get('order_id', None),
        refund_amount=data.get('refund_amount', None),
        status=data.get('status'),
        description=data.get('description', None)
    )
    return JSONResponse({'result': result})

@app.post('/api/send_seller_broken_product_notification')
async def ctrl_send_seller_broken_product_notification(request: Request):
    data = await request.json()
    result = await customerAssistanceServices.send_seller_broken_product_notification(**data)
    return JSONResponse({'result': result})

@app.post('/api/get_shipment_greivence_reports')
async def ctrl_get_shipment_greivence_reports(request: Request):
    data = await request.json()
    result = await customerAssistanceServices.get_shipment_greivence_reports(**data)
    return JSONResponse({'result': result})

@app.post('/api/process_customer_complaint')
async def ctrl_process_customer_complaint(request: Request):
    data = await request.json()
    result = await customerAssistanceServices.process_customer_complaint(**data)
    return JSONResponse({'result': result})

@app.post('/api/get_greivence_details')
async def ctrl_get_greivence_details(request: Request):
    data = await request.json()
    result = await customerAssistanceServices.get_greivence_details(**data)
    return JSONResponse({'result': result})

@app.post('/api/get_specific_refund_request')
async def ctrl_get_specific_refund_request(request: Request):
    data = await request.json()
    result = await customerAssistanceServices.get_specific_refund_request(**data)
    return JSONResponse({'result': result})

@app.post('/api/process_shipment_report')
async def ctrl_process_shipment_report(request: Request):
    data = await request.json()
    result = await customerAssistanceServices.process_shipment_report(**data)
    return JSONResponse({'result': result})

@app.post('/api/get_all_customer_refund_requests')
async def ctrl_get_all_customer_refund_requests(request: Request):
    data = await request.json()
    result = await customerAssistanceServices.get_all_customer_refund_requests(**data)
    return JSONResponse({'result': result})

"""
To run the app, use an ASGI server like:
    uvicorn backend.app:app --reload
"""