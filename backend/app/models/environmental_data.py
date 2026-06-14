from __future__ import annotations
from typing import TYPE_CHECKING
from typing import List, Optional
import uuid
from sqlalchemy import Numeric, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime, date as datetime_date

from app.core.database import Base


class EnvironmentalData(Base):
    __tablename__ = "environmental_data"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    district_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("districts.id"), nullable=False, index=True)
    date: Mapped[datetime_date] = mapped_column(Date, nullable=False, index=True)
    temperature_c: Mapped[float] = mapped_column(Numeric(5, 2))
    rainfall_mm: Mapped[float] = mapped_column(Numeric(7, 2))
    humidity_pct: Mapped[float] = mapped_column(Numeric(5, 2))
    fetched_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    district: Mapped["District"] = relationship(back_populates="environmental_data")

    __table_args__ = (
        UniqueConstraint("district_id", "date", name="uix_env_district_date"),
    )

if TYPE_CHECKING:
    from app.models.district import District
