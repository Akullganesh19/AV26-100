from __future__ import annotations

from sqlalchemy import Table, Column, ForeignKey, UniqueConstraint
from app.core.database import Base

# Association Table for Many-to-Many relationship between Users and Districts
user_district_association = Table(
    "user_districts",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("district_id", ForeignKey("districts.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("user_id", "district_id", name="uix_user_district")
)
