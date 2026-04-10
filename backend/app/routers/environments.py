from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
from app.database import get_db
from app.models.environment import Environment
from app.schemas.environment import EnvironmentCreate, EnvironmentUpdate, EnvironmentResponse

router = APIRouter(prefix="/api/environments", tags=["Environments"])


@router.get("", response_model=List[EnvironmentResponse])
def list_environments(db: Session = Depends(get_db)):
    envs = db.query(Environment).order_by(Environment.sort_order).all()
    return [_parse_env(e) for e in envs]


@router.post("", response_model=EnvironmentResponse)
def create_environment(data: EnvironmentCreate, db: Session = Depends(get_db)):
    if data.is_default:
        db.query(Environment).update({Environment.is_default: False})
    env = Environment(
        name=data.name,
        description=data.description,
        variables=json.dumps(data.variables or {}),
        is_default=data.is_default,
        sort_order=data.sort_order,
    )
    db.add(env)
    db.commit()
    db.refresh(env)
    return _parse_env(env)


@router.get("/{env_id}", response_model=EnvironmentResponse)
def get_environment(env_id: int, db: Session = Depends(get_db)):
    env = db.query(Environment).filter(Environment.id == env_id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    return _parse_env(env)


@router.put("/{env_id}", response_model=EnvironmentResponse)
def update_environment(env_id: int, data: EnvironmentUpdate, db: Session = Depends(get_db)):
    env = db.query(Environment).filter(Environment.id == env_id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    if data.is_default:
        db.query(Environment).filter(Environment.id != env_id).update({Environment.is_default: False})
    for key, value in data.model_dump().items():
        if key == "variables":
            setattr(env, key, json.dumps(value) if value else "{}")
        else:
            setattr(env, key, value)
    db.commit()
    db.refresh(env)
    return _parse_env(env)


@router.delete("/{env_id}")
def delete_environment(env_id: int, db: Session = Depends(get_db)):
    env = db.query(Environment).filter(Environment.id == env_id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    db.delete(env)
    db.commit()
    return {"code": 0, "message": "deleted"}


@router.post("/{env_id}/set-default")
def set_default_environment(env_id: int, db: Session = Depends(get_db)):
    env = db.query(Environment).filter(Environment.id == env_id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    db.query(Environment).update({Environment.is_default: False})
    env.is_default = True
    db.commit()
    return {"code": 0, "message": "set as default"}


def _parse_env(env: Environment) -> dict:
    return {
        "id": env.id,
        "name": env.name,
        "description": env.description,
        "variables": json.loads(env.variables or "{}"),
        "is_default": env.is_default,
        "sort_order": env.sort_order,
        "created_at": env.created_at,
        "updated_at": env.updated_at,
    }
