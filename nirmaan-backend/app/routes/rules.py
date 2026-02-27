from fastapi import APIRouter
from app.schemas.rules import RuleRequest
from app.services.rule_engine import evaluate_rules

router = APIRouter(prefix="/rules")

@router.post("/evaluate")
def evaluate(data: RuleRequest):
    return evaluate_rules(
        plot=data.plot.model_dump(),
        building=data.building.model_dump(),
        state=data.state
    )