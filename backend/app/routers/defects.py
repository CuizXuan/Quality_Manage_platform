from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
import os
import shutil
from app.database import get_db
from app.models import Defect, DefectAttachment, DefectComment, ExecutionLog

router = APIRouter(prefix="/api/defects", tags=["缺陷管理"])

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "defect_attachments")
os.makedirs(DATA_DIR, exist_ok=True)


class DefectCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    severity: Optional[str] = "medium"
    priority: Optional[str] = "medium"
    status: Optional[str] = "open"
    defect_type: Optional[str] = "functional"
    assignee: Optional[str] = ""
    reporter: str
    execution_log_id: Optional[int] = None
    case_id: Optional[int] = None
    scenario_id: Optional[int] = None
    environment: Optional[str] = ""
    steps_to_reproduce: Optional[str] = ""
    expected_result: Optional[str] = ""
    actual_result: Optional[str] = ""


class DefectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    defect_type: Optional[str] = None
    assignee: Optional[str] = None
    resolution: Optional[str] = None
    external_id: Optional[str] = None
    external_url: Optional[str] = None


class DefectCommentCreate(BaseModel):
    content: str
    author: str


@router.get("")
def list_defects(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    assignee: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Defect)
    if status:
        query = query.filter(Defect.status == status)
    if severity:
        query = query.filter(Defect.severity == severity)
    if assignee:
        query = query.filter(Defect.assignee == assignee)
    if keyword:
        query = query.filter(Defect.title.contains(keyword) | Defect.description.contains(keyword))

    defects = query.order_by(Defect.updated_at.desc()).all()
    return {"code": 0, "data": defects}


@router.post("")
def create_defect(data: DefectCreate, db: Session = Depends(get_db)):
    defect = Defect(**data.model_dump())
    db.add(defect)
    db.commit()
    db.refresh(defect)
    return {"code": 0, "data": defect}


@router.get("/{defect_id}")
def get_defect(defect_id: int, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=404, detail="缺陷不存在")
    comments = db.query(DefectComment).filter(DefectComment.defect_id == defect_id).order_by(DefectComment.created_at).all()
    attachments = db.query(DefectAttachment).filter(DefectAttachment.defect_id == defect_id).all()
    result = {
        "defect": defect,
        "comments": comments,
        "attachments": attachments,
    }
    return {"code": 0, "data": result}


@router.put("/{defect_id}")
def update_defect(defect_id: int, data: DefectUpdate, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=404, detail="缺陷不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        if k == "resolved_at" and v and defect.status != "resolved":
            defect.resolved_at = datetime.now()
        setattr(defect, k, v)
    defect.updated_at = datetime.now()
    db.commit()
    db.refresh(defect)
    return {"code": 0, "data": defect}


@router.delete("/{defect_id}")
def delete_defect(defect_id: int, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=404, detail="缺陷不存在")
    db.query(DefectComment).filter(DefectComment.defect_id == defect_id).delete()
    db.query(DefectAttachment).filter(DefectAttachment.defect_id == defect_id).delete()
    db.delete(defect)
    db.commit()
    return {"code": 0, "message": "删除成功"}


@router.post("/{defect_id}/comments")
def add_comment(defect_id: int, data: DefectCommentCreate, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=404, detail="缺陷不存在")
    comment = DefectComment(**data.model_dump(), defect_id=defect_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {"code": 0, "data": comment}


@router.post("/{defect_id}/attachments")
async def upload_attachment(defect_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=404, detail="缺陷不存在")

    fname = f"{defect_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    fpath = os.path.join(DATA_DIR, fname)
    with open(fpath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    att = DefectAttachment(
        defect_id=defect_id,
        file_name=file.filename,
        file_path=fpath,
        file_size=os.path.getsize(fpath),
        file_type=file.content_type or "",
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    return {"code": 0, "data": att}


@router.post("/from-execution")
def create_from_execution(data: dict, db: Session = Depends(get_db)):
    """从执行记录一键创建缺陷"""
    log_id = data.get("execution_log_id")
    log = db.query(ExecutionLog).filter(ExecutionLog.id == log_id).first() if log_id else None

    title = data.get("title", "[API] 接口执行异常")
    severity = data.get("severity", "medium")
    priority = data.get("priority", "medium")
    reporter = data.get("reporter", "system")
    assignee = data.get("assignee", "")

    defect = Defect(
        title=title,
        description=data.get("description", ""),
        severity=severity,
        priority=priority,
        reporter=reporter,
        assignee=assignee,
        execution_log_id=log_id,
        case_id=log.case_id if log else None,
        environment=data.get("environment", ""),
        steps_to_reproduce=data.get("steps_to_reproduce", ""),
        expected_result=data.get("expected_result", ""),
        actual_result=data.get("actual_result", ""),
    )
    db.add(defect)
    db.commit()
    db.refresh(defect)
    return {"code": 0, "data": defect}


@router.get("/stats/summary")
def defect_stats(db: Session = Depends(get_db)):
    """缺陷统计看板"""
    total = db.query(Defect).count()
    by_status = {}
    by_severity = {}
    for d in db.query(Defect).all():
        by_status[d.status] = by_status.get(d.status, 0) + 1
        by_severity[d.severity] = by_severity.get(d.severity, 0) + 1
    return {"code": 0, "data": {
        "total": total,
        "by_status": by_status,
        "by_severity": by_severity,
    }}
