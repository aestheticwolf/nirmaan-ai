from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.plot import Plot
from app.models.building import Building
from app.models.compliance_result import ComplianceResult
from app.models.rule import Rule
import os

router = APIRouter()


@router.get("/dashboard/stats")
def get_dashboard_stats():
    db: Session = SessionLocal()

    total_projects = db.query(Plot).count()
    total_buildings = db.query(Building).count()

    generated_folder = "generated"
    layout_count = 0

    if os.path.exists(generated_folder):
        layout_count = len(os.listdir(generated_folder))

    total_results = db.query(ComplianceResult).count()
    passed_results = db.query(ComplianceResult).filter(
        ComplianceResult.status == "PASS"
    ).count()

    compliance_rate = 0
    if total_results > 0:
        compliance_rate = round((passed_results / total_results) * 100, 2)

    db.close()

    return {
        "total_projects": total_projects,
        "active_projects": total_buildings,
        "layouts_generated": layout_count,
        "compliance_rate": compliance_rate
    }


@router.get("/dashboard/design/{design_id}")
def get_design_compliance(design_id: str):
    db: Session = SessionLocal()

    results = db.query(ComplianceResult).filter(
        ComplianceResult.design_id == design_id
    ).all()

    db.close()

    return [
        {
            "rule_id": r.rule_id,
            "status": r.status,
            "actual_value": r.actual_value,
            "expected_value": r.expected_value,
            "remarks": r.remarks,
            "evaluated_at": r.evaluated_at
        }
        for r in results
    ]


@router.get("/dashboard/designs")
def get_all_design_summaries():
    db: Session = SessionLocal()

    from sqlalchemy import func, case

    summary = (
        db.query(
            ComplianceResult.design_id,
            func.count(ComplianceResult.id).label("total_rules"),
            func.sum(
    case(
        (ComplianceResult.status == "PASS", 1),
        else_=0
    )
).label("passed_rules")
        )
        .group_by(ComplianceResult.design_id)
        .all()
    )

    db.close()

    results = []

    for row in summary:
        failed = row.total_rules - row.passed_rules
        overall = "PASS" if failed == 0 else "FAIL"

        results.append({
            "design_id": row.design_id,
            "total_rules": row.total_rules,
            "passed_rules": row.passed_rules,
            "failed_rules": failed,
            "overall_status": overall
        })

    return results



@router.get("/rules")
def get_all_rules():
    db: Session = SessionLocal()

    rules = db.query(Rule).filter(
        Rule.is_active == True
    ).all()

    db.close()

    return [
        {
            "id": r.id,
            "title": r.title,
            "category": r.category,
            "logic": r.expression_logic,
            "regulation_id": r.regulation_id
        }
        for r in rules
    ]

