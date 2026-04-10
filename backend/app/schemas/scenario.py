from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ExtractRule(BaseModel):
    id: str
    name: str
    source: str
    path: Optional[str] = None
    header_name: Optional[str] = None
    cookie_name: Optional[str] = None
    pattern: Optional[str] = None
    scope: str = "scenario"
    enabled: bool = True


class ScenarioStepBase(BaseModel):
    case_id: int
    step_order: int
    extract_rules: Optional[List[ExtractRule]] = []
    skip_on_failure: bool = True
    retry_times: int = 0
    retry_interval: int = 1000
    enabled: bool = True


class ScenarioStepCreate(ScenarioStepBase):
    pass


class ScenarioStepUpdate(ScenarioStepBase):
    pass


class ScenarioStepResponse(ScenarioStepBase):
    id: int
    scenario_id: int

    class Config:
        from_attributes = True


class ScenarioBase(BaseModel):
    name: str
    description: Optional[str] = ""
    folder_path: str = "/"
    variables: Optional[dict] = {}


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioUpdate(ScenarioBase):
    pass


class ScenarioResponse(ScenarioBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    steps: Optional[List[ScenarioStepResponse]] = []

    class Config:
        from_attributes = True
