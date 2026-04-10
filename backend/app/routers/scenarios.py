from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
from app.database import get_db
from app.models.scenario import Scenario, ScenarioStep
from app.models.case import TestCase
from app.schemas.scenario import (
    ScenarioCreate, ScenarioUpdate, ScenarioResponse,
    ScenarioStepCreate, ScenarioStepUpdate, ScenarioStepResponse,
)

router = APIRouter(prefix="/api/scenarios", tags=["Scenarios"])


@router.get("", response_model=List[ScenarioResponse])
def list_scenarios(db: Session = Depends(get_db)):
    scenarios = db.query(Scenario).order_by(Scenario.folder_path, Scenario.id).all()
    return [_parse_scenario(s, db) for s in scenarios]


@router.post("", response_model=ScenarioResponse)
def create_scenario(data: ScenarioCreate, db: Session = Depends(get_db)):
    scenario = Scenario(
        name=data.name,
        description=data.description,
        folder_path=data.folder_path,
        variables=json.dumps(data.variables or {}),
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return _parse_scenario(scenario, db)


@router.get("/{scenario_id}", response_model=ScenarioResponse)
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return _parse_scenario(scenario, db)


@router.put("/{scenario_id}", response_model=ScenarioResponse)
def update_scenario(scenario_id: int, data: ScenarioUpdate, db: Session = Depends(get_db)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    for key, value in data.model_dump().items():
        if key == "variables":
            setattr(scenario, key, json.dumps(value) if value else "{}")
        else:
            setattr(scenario, key, value)
    db.commit()
    db.refresh(scenario)
    return _parse_scenario(scenario, db)


@router.delete("/{scenario_id}")
def delete_scenario(scenario_id: int, db: Session = Depends(get_db)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    db.delete(scenario)
    db.commit()
    return {"code": 0, "message": "deleted"}


@router.post("/{scenario_id}/steps", response_model=ScenarioStepResponse)
def add_step(scenario_id: int, data: ScenarioStepCreate, db: Session = Depends(get_db)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    step = ScenarioStep(
        scenario_id=scenario_id,
        case_id=data.case_id,
        step_order=data.step_order,
        extract_rules=json.dumps([e.model_dump() for e in (data.extract_rules or [])]),
        skip_on_failure=data.skip_on_failure,
        retry_times=data.retry_times,
        retry_interval=data.retry_interval,
        enabled=data.enabled,
    )
    db.add(step)
    db.commit()
    db.refresh(step)
    return _parse_step(step)


@router.put("/{scenario_id}/steps/{step_id}", response_model=ScenarioStepResponse)
def update_step(scenario_id: int, step_id: int, data: ScenarioStepUpdate, db: Session = Depends(get_db)):
    step = db.query(ScenarioStep).filter(ScenarioStep.id == step_id, ScenarioStep.scenario_id == scenario_id).first()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    for key, value in data.model_dump().items():
        if key == "extract_rules":
            setattr(step, key, json.dumps(value) if value else "[]")
        else:
            setattr(step, key, value)
    db.commit()
    db.refresh(step)
    return _parse_step(step)


@router.delete("/{scenario_id}/steps/{step_id}")
def delete_step(scenario_id: int, step_id: int, db: Session = Depends(get_db)):
    step = db.query(ScenarioStep).filter(ScenarioStep.id == step_id, ScenarioStep.scenario_id == scenario_id).first()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    db.delete(step)
    db.commit()
    return {"code": 0, "message": "deleted"}


@router.put("/{scenario_id}/steps/reorder")
def reorder_steps(scenario_id: int, step_ids: List[int], db: Session = Depends(get_db)):
    for order, step_id in enumerate(step_ids):
        step = db.query(ScenarioStep).filter(ScenarioStep.id == step_id, ScenarioStep.scenario_id == scenario_id).first()
        if step:
            step.step_order = order
    db.commit()
    return {"code": 0, "message": "reordered"}


def _parse_scenario(scenario: Scenario, db: Session) -> dict:
    steps = db.query(ScenarioStep).filter(ScenarioStep.scenario_id == scenario.id).order_by(ScenarioStep.step_order).all()
    return {
        "id": scenario.id,
        "name": scenario.name,
        "description": scenario.description,
        "folder_path": scenario.folder_path,
        "variables": json.loads(scenario.variables or "{}"),
        "created_at": scenario.created_at,
        "updated_at": scenario.updated_at,
        "steps": [_parse_step(s) for s in steps],
    }


def _parse_step(step: ScenarioStep) -> dict:
    return {
        "id": step.id,
        "scenario_id": step.scenario_id,
        "case_id": step.case_id,
        "step_order": step.step_order,
        "extract_rules": json.loads(step.extract_rules or "[]"),
        "skip_on_failure": step.skip_on_failure,
        "retry_times": step.retry_times,
        "retry_interval": step.retry_interval,
        "enabled": step.enabled,
    }
