from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

# Legacy-only union; do not use in async code paths
DBSession = Union[Session, AsyncSession]

# Async-only alias for strict typing in async repos/services
AsyncDBSession = AsyncSession
