from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EnvironmentBase(BaseModel):
    name: str
    description: Optional[str] = ""
    variables: Optional[dict] = {}
    is_default: bool = False
    sort_order: int = 0


class EnvironmentCreate(EnvironmentBase):
    pass


class EnvironmentUpdate(EnvironmentBase):
    pass


class EnvironmentResponse(EnvironmentBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
