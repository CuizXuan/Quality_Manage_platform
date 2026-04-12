from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import json
from app.database import get_db
from app.models.case import TestCase
from app.models.environment import Environment
from app.models.execution_log import ExecutionLog
from app.schemas.case import TestCaseCreate, TestCaseUpdate, TestCaseResponse, RunCaseRequest
from app.services.request_executor import RequestExecutor

router = APIRouter(prefix="/api/cases", tags=["Cases"])


@router.get("", response_model=List[TestCaseResponse])
def list_cases(
    folder: Optional[str] = Query(None),
    method: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(TestCase)
    if folder:
        query = query.filter(TestCase.folder_path == folder)
    if method:
        query = query.filter(TestCase.method == method.upper())
    if keyword:
        query = query.filter(or_(
            TestCase.name.contains(keyword),
            TestCase.url.contains(keyword),
        ))
    cases = query.order_by(TestCase.folder_path, TestCase.sort_order).offset(skip).limit(limit).all()
    return [_parse_case(c) for c in cases]


@router.post("", response_model=TestCaseResponse)
def create_case(data: TestCaseCreate, db: Session = Depends(get_db)):
    case = TestCase(
        name=data.name,
        description=data.description,
        method=data.method,
        url=data.url,
        headers=json.dumps(data.headers or {}),
        params=json.dumps(data.params or {}),
        body=data.body or "",
        body_type=data.body_type,
        auth_type=data.auth_type,
        auth_config=json.dumps(data.auth_config or {}),
        folder_path=data.folder_path,
        sort_order=data.sort_order,
        assertions=json.dumps([a.model_dump() for a in (data.assertions or [])]),
        pre_script=data.pre_script or "",
        post_script=data.post_script or "",
        timeout=data.timeout,
        follow_redirects=data.follow_redirects,
        verify_ssl=data.verify_ssl,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return _parse_case(case)


@router.get("/{case_id}", response_model=TestCaseResponse)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return _parse_case(case)


@router.put("/{case_id}", response_model=TestCaseResponse)
def update_case(case_id: int, data: TestCaseUpdate, db: Session = Depends(get_db)):
    case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    for key, value in data.model_dump().items():
        if key in ("headers", "params", "auth_config", "assertions"):
            setattr(case, key, json.dumps(value) if value else "{}")
        else:
            setattr(case, key, value)
    db.commit()
    db.refresh(case)
    return _parse_case(case)


@router.delete("/{case_id}")
def delete_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    db.delete(case)
    db.commit()
    return {"code": 0, "message": "deleted"}


@router.post("/{case_id}/duplicate", response_model=TestCaseResponse)
def duplicate_case(case_id: int, db: Session = Depends(get_db)):
    original = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Case not found")
    new_case = TestCase(
        name=f"{original.name} (copy)",
        description=original.description,
        method=original.method,
        url=original.url,
        headers=original.headers,
        params=original.params,
        body=original.body,
        body_type=original.body_type,
        auth_type=original.auth_type,
        auth_config=original.auth_config,
        folder_path=original.folder_path,
        sort_order=original.sort_order + 1,
        assertions=original.assertions,
        pre_script=original.pre_script,
        post_script=original.post_script,
        timeout=original.timeout,
        follow_redirects=original.follow_redirects,
        verify_ssl=original.verify_ssl,
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return _parse_case(new_case)


@router.post("/batch-delete")
def batch_delete_cases(ids: List[int], db: Session = Depends(get_db)):
    db.query(TestCase).filter(TestCase.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return {"code": 0, "message": f"deleted {len(ids)} cases"}


@router.post("/{case_id}/run")
async def run_case(case_id: int, body: RunCaseRequest, db: Session = Depends(get_db)):
    case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # 获取环境变量
    env_vars = {}
    env_id = body.environment_id
    if env_id:
        env = db.query(Environment).filter(Environment.id == env_id).first()
        if env:
            env_vars = json.loads(env.variables or "{}")
    else:
        # 使用默认环境
        env = db.query(Environment).filter(Environment.is_default == True).first()
        if env:
            env_id = env.id
            env_vars = json.loads(env.variables or "{}")

    case_data = _parse_case(case)

    # 执行用例
    executor = RequestExecutor()
    result = await executor.execute_case(case_data, env_vars, body.variables)

    # 保存执行记录
    log = ExecutionLog(
        case_id=case_id,
        scenario_id=None,
        scenario_step_id=None,
        execution_type="single",
        execution_id=result["execution_id"],
        request_url=case.url,
        request_method=case.method,
        request_headers=case.headers,
        request_body=case.body,
        response_status=result["response"]["status_code"],
        response_headers=json.dumps(result["response"]["headers"]),
        response_body=json.dumps(result["response"]["body"]) if isinstance(result["response"]["body"], (dict, list)) else str(result["response"]["body"]),
        response_size=result["response"]["size"],
        response_time_ms=result["response"]["time_ms"],
        status=result["status"],
        assertion_results=json.dumps(result["assertion_results"]),
        environment_id=env_id,
        triggered_by="user",
    )
    db.add(log)
    db.commit()

    return {"code": 0, "message": "success", "data": result}


def _parse_case(case: TestCase) -> dict:
    return {
        "id": case.id,
        "name": case.name,
        "description": case.description,
        "method": case.method,
        "url": case.url,
        "headers": json.loads(case.headers or "{}"),
        "params": json.loads(case.params or "{}"),
        "body": case.body,
        "body_type": case.body_type,
        "auth_type": case.auth_type,
        "auth_config": json.loads(case.auth_config or "{}"),
        "folder_path": case.folder_path,
        "sort_order": case.sort_order,
        "assertions": json.loads(case.assertions or "[]"),
        "pre_script": case.pre_script,
        "post_script": case.post_script,
        "timeout": case.timeout,
        "follow_redirects": case.follow_redirects,
        "verify_ssl": case.verify_ssl,
        "created_at": case.created_at,
        "updated_at": case.updated_at,
    }
