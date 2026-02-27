def evaluate_rules(plot, building, state):
    results = []

    if state == "Goa" and building["far"] > 1.5:
        results.append({
            "type": "HARD",
            "message": "FSI exceeds Goa limit (1.5)"
        })

    if building["floors"] > 2:
        results.append({
            "type": "SOFT",
            "message": "Parking may be insufficient"
        })

    plot_area = plot["length"] * plot["width"]

    if plot_area < 300:
        results.append({
            "type": "ADVISORY",
            "message": "Small plot size"
        })

    can_proceed = not any(r["type"] == "HARD" for r in results)

    return {
        "canProceed": can_proceed,
        "results": results
    }