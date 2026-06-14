from __future__ import annotations

import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.prediction import Prediction


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pipeline_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False) # running, success, failed
    
    started_at: Mapped[datetime] = mapped_column(server_default=func.now())
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    rows_ingested: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    predictions: Mapped[List["Prediction"]] = relationship(back_populates="pipeline_run")
