from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime


class AssertionRule(BaseModel):
    id: str
    type: str
    operator: str
    expected: Optional[Union[str, int, float]] = None
    path: Optional[str] = None
    header_name: Optional[str] = None
    enabled: bool = True


class TestCaseBase(BaseModel):
    name: str
    description: Optional[str] = ""
    method: str = "GET"
    url: str = ""
    headers: Optional[dict] = {}
    params: Optional[dict] = {}
    body: Optional[str] = ""
    body_type: str = "json"
    auth_type: str = "none"
    auth_config: Optional[dict] = {}
    folder_path: str = "/"
    sort_order: int = 0
    assertions: Optional[List[AssertionRule]] = []
    pre_script: Optional[str] = ""
    post_script: Optional[str] = ""
    timeout: int = 30
    follow_redirects: bool = True
    verify_ssl: bool = True


class TestCaseCreate(TestCaseBase):
    pass


class TestCaseUpdate(TestCaseBase):
    pass


class TestCaseResponse(TestCaseBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RunCaseRequest(BaseModel):
    environment_id: Optional[int] = None
    variables: Optional[dict] = {}
