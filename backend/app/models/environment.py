from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime
from app.models.base import Base


class Environment(Base):
    __tablename__ = "environment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, default="")
    variables = Column(Text, default="{}")
    is_default = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
