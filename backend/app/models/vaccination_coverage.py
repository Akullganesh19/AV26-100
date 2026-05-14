import uuid
from sqlalchemy import String, Numeric, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date

from app.core.database import Base


class VaccinationCoverage(Base):
    __tablename__ = "vaccination_coverage"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    district_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("districts.id"), nullable=False, index=True)
    disease: Mapped[str] = mapped_column(String(64), nullable=False)
    coverage_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    district: Mapped["District"] = relationship(back_populates="vaccination_coverage")

    __table_args__ = (
        UniqueConstraint("district_id", "disease", "as_of_date", name="uix_vacc_district_disease_date"),
    )
