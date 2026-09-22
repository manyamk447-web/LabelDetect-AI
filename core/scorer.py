def get_score_grade(score, verdict):

    if score >= 90:
        grade = "A"
        risk_level = "Low"
        description = "The label appears substantially compliant."

    elif score >= 75:
        grade = "B"
        risk_level = "Moderate"
        description = "The label has some issues that should be reviewed."

    elif score >= 50:
        grade = "C"
        risk_level = "High"
        description = "Several compliance issues require attention."

    else:
        grade = "D"
        risk_level = "Critical"
        description = "The label has significant missing or non-compliant declarations."

    return {
        "grade": grade,
        "risk_level": risk_level,
        "description": description
    }
