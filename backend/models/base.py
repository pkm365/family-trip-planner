"""
Base SQLAlchemy model with common functionality.

Provides base model class and timestamp mixin for all database models.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base, declared_attr


Base = declarative_base()


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models."""
    
    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        doc="Timestamp when record was created"
    )
    
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Timestamp when record was last updated"
    )


class BaseModel(Base, TimestampMixin):
    """Abstract base model with common fields and functionality."""
    
    __abstract__ = True
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Primary key identifier"
    )
    
    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name."""
        # Convert CamelCase to snake_case and pluralize
        name = cls.__name__
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append('_')
            result.append(char.lower())
        return ''.join(result) + 's'