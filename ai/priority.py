def calculate_priority(
    value_score: float,
    feasibility_score: float,
    risk_score: float,
    confidence_score: float
):
    """
    Calculate AI opportunity priority.

    Scores are expected between 1 and 10.
    Higher value, feasibility and confidence increase priority.
    Higher risk decreases priority.
    """

    priority_score = (
        (value_score * 0.35)
        + (feasibility_score * 0.25)
        + (confidence_score * 0.25)
        + ((10 - risk_score) * 0.15)
    )

    priority_score = round(priority_score, 2)

    if priority_score >= 7.5:
        priority_level = "High"

    elif priority_score >= 5:
        priority_level = "Medium"

    else:
        priority_level = "Low"

    return {
        "value_score": value_score,
        "feasibility_score": feasibility_score,
        "risk_score": risk_score,
        "confidence_score": confidence_score,
        "priority_score": priority_score,
        "priority_level": priority_level
    }