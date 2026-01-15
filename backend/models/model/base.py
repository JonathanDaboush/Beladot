
import datetime
import pytz
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
	id: int

	@declared_attr
	def __tablename__(cls):
		return cls.__name__.lower()

	created_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(pytz.UTC), nullable=False)
	updated_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(pytz.UTC), onupdate=lambda: datetime.datetime.now(pytz.UTC), nullable=False)
	is_deleted = Column(Boolean, default=False, nullable=False)

	def __repr__(self):
		# Only show non-sensitive fields
		safe_fields = {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in {"password", "secret_key"}}
		return f"<{self.__class__.__name__} {safe_fields}>"

