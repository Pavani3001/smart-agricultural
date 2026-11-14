"""
SQLAlchemy model for the Farmer entity.

Maps to the 'farmers' table defined in init_db.sql.
Stores farmer registration and contact information.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone

from ..database import Base


class Farmer(Base):
    """
    ORM model representing a farmer in the system.

    Attributes:
        id: Auto-incrementing primary key.
        name: Full name of the farmer.
        email: Unique email address for login/contact.
        phone: Optional phone number.
        address: Optional full mailing address.
        created_at: Timestamp when the record was created (UTC).
        updated_at: Timestamp of the last update (UTC).
    """

    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        default=lambda: datetime.now(timezone.utc),
    )

    # One farmer can own many fields
    fields = relationship("Field", back_populates="farmer", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Farmer(id={self.id}, name='{self.name}', email='{self.email}')>"
