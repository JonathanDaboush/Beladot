from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

# Unified session type for repositories and services
DBSession = Union[AsyncSession, Session]
