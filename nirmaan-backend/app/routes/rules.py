from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.rules import RuleRequest
from app.services.rule_engine import evaluate_rules
from app.models.design import Design
from app.models.rule import Rule
import uuid

router = APIRouter(prefix="/rules")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/evaluate")
def evaluate(data: RuleRequest, db: Session = Depends(get_db)):

    # Create Design record first
    new_design = Design(
        project_version_id=None,
        total_floors=data.building.floors,
        built_up_area=data.plot.length * data.plot.width,
        status="DRAFT"
    )

    db.add(new_design)
    db.commit()
    db.refresh(new_design)

    # Evaluate rules using this design_id
    result = evaluate_rules(
        db=db,
        plot=data.plot.model_dump(),
        building=data.building.model_dump(),
        state=data.state,
        design_id=new_design.id
    )

    return result


@router.get("/")
def get_rules(db: Session = Depends(get_db)):
    return db.query(Rule).all()


@router.post("/")
def create_rule(data: dict, db: Session = Depends(get_db)):
    rule = Rule(**data)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.put("/{rule_id}")
def update_rule(rule_id: int, data: dict, db: Session = Depends(get_db)):
    rule = db.query(Rule).filter(Rule.id == rule_id).first()

    for key, value in data.items():
        setattr(rule, key, value)

    db.commit()
    return rule


@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(Rule).filter(Rule.id == rule_id).first()

    db.delete(rule)
    db.commit()

    return {"message": "deleted"}