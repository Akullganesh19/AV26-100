import uuid
from sqlalchemy import String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

from app.core.database import Base

class PredictionAuditLog(Base):
    __tablename__ = "prediction_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    district_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("districts.id"), nullable=True, index=True)
    endpoint: Mapped[str] = mapped_column(String(64), nullable=False) # e.g., "clinical/heart"
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False) # SHA256 of anonymized inputs
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    model_version: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="SUCCESS")
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    
    # Optional: store metadata like deployment_id or hardware_tag
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
