from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
import enum
from typing import List, Optional
from sqlalchemy import String, Boolean, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    OFFICER = "officer"
    ANALYST = "analyst"
    VIEWER = "viewer"
    SYSADMIN = "sysadmin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    clerk_id: Mapped[Optional[str]] = mapped_column(String(128), unique=True, index=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.OFFICER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    alert_threshold: Mapped[int] = mapped_column(Integer, default=70)
    email_alerts: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    # Relationships
    districts: Mapped[List["District"]] = relationship(
        secondary="user_districts", back_populates="users"
    )
    scenarios: Mapped[List["Scenario"]] = relationship(back_populates="user")
    acknowledged_alerts: Mapped[List["Alert"]] = relationship(back_populates="acknowledged_by_user")
    password_reset_tokens: Mapped[List["PasswordResetToken"]] = relationship(back_populates="user")

if TYPE_CHECKING:
    from app.models.district import District
    from app.models.scenario import Scenario
    from app.models.alert import Alert
    from app.models.password_reset_token import PasswordResetToken
