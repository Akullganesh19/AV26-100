from __future__ import annotations

import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Numeric, Integer, Computed, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.raw_data import RawData
    from app.models.environmental_data import EnvironmentalData
    from app.models.vaccination_coverage import VaccinationCoverage
    from app.models.prediction import Prediction
    from app.models.alert import Alert
    from app.models.scenario import Scenario


class District(Base):
    __tablename__ = "districts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(128), nullable=False)
    state_code: Mapped[str] = mapped_column(String(2), nullable=False)
    
    latitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    
    population: Mapped[int] = mapped_column(Integer, nullable=False)
    area_km2: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Generated column for population density
    pop_density: Mapped[float] = mapped_column(
        Numeric(12, 2), 
        Computed("population / NULLIF(area_km2, 0)"), 
        index=True
    )

    # Relationships
    users: Mapped[List["User"]] = relationship(
        secondary="user_districts", back_populates="districts"
    )
    raw_data: Mapped[List["RawData"]] = relationship(back_populates="district")
    environmental_data: Mapped[List["EnvironmentalData"]] = relationship(back_populates="district")
    vaccination_coverage: Mapped[List["VaccinationCoverage"]] = relationship(back_populates="district")
    predictions: Mapped[List["Prediction"]] = relationship(back_populates="district")
    alerts: Mapped[List["Alert"]] = relationship(back_populates="district")
    scenarios: Mapped[List["Scenario"]] = relationship(back_populates="district")

    __table_args__ = (
        UniqueConstraint("name", "state", name="uix_district_name_state"),
    )

    def to_search_json(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "state": self.state,
            "state_code": self.state_code
        }
