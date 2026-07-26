from sqlalchemy.orm import Session
from app.models.rule import Rule
from app.models.compliance_result import ComplianceResult
from app.models.state import State
from app.models.authority import Authority
from app.models.regulation import Regulation


def evaluate_rules(db: Session, plot: dict, building: dict, state: str, design_id):
    results = []

    db.query(ComplianceResult).filter(
    ComplianceResult.design_id == design_id
).delete()

    plot_area = plot["length"] * plot["width"]

    context = {
        "plot_area": plot_area,
        "length": plot["length"],
        "width": plot["width"],
        "road_width": plot.get("roadWidth") or plot.get("road_width"),
        "floors": building["floors"],
        "far": building.get("far"),
        "coverage": building.get("coverage"),
    }

    # 1️⃣ Find State
    state_obj = db.query(State).filter(
        State.name.ilike(state),
        State.is_active == True
    ).first()

    if not state_obj:
        return {"canProceed": False, "results": []}

    # 2️⃣ Find Authority
    authority = db.query(Authority).filter(
        Authority.state_id == state_obj.id,
        Authority.is_active == True
    ).first()

    if not authority:
        return {"canProceed": False, "results": []}

    # 3️⃣ Find Regulation
    regulation = db.query(Regulation).filter(
        Regulation.authority_id == authority.id,
        Regulation.is_active == True
    ).first()

    if not regulation:
        return {"canProceed": False, "results": []}

    # 4️⃣ Fetch only rules of that regulation
    rules = db.query(Rule).filter(
        Rule.regulation_id == regulation.id,
        Rule.is_active == True
    ).all()

    for rule in rules:
        logic = rule.expression_logic
        if not logic:
            continue

        left = logic.get("left")
        operator = logic.get("operator")
        right = logic.get("right")

        actual_value = context.get(left)
        if actual_value is None:
            continue

        expected_value = right
        passed = False

        if operator == "<=":
            passed = actual_value <= expected_value
        elif operator == ">=":
            passed = actual_value >= expected_value
        elif operator == "<":
            passed = actual_value < expected_value
        elif operator == ">":
            passed = actual_value > expected_value
        elif operator == "==":
            passed = actual_value == expected_value

        status = "PASS" if passed else "FAIL"

        compliance = ComplianceResult(
            design_id=design_id,
            rule_id=rule.id,
            status=status,
            actual_value=actual_value,
            expected_value=expected_value,
            remarks=rule.title
        )

        db.add(compliance)

        results.append({
            "rule_id": rule.id,
            "title": rule.title,
            "passed": passed,
            "actual_value": actual_value,
            "expected_value": expected_value,
            "category": rule.category
        })

    db.commit()

    overall_pass = all(r["passed"] for r in results) if results else True

    return {
        "canProceed": overall_pass,
        "results": results
    }