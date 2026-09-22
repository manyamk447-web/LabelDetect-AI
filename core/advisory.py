def generate_remediation_plan(compliance_report):

    immediate_actions = []
    format_corrections = []
    best_practices = []

    # Critical violations
    for violation in compliance_report.critical_violations:

        immediate_actions.append({
            "field": "compliance",
            "action": violation,
            "penalty": "Mandatory correction required"
        })

    # Warnings
    for warning in compliance_report.warnings:

        format_corrections.append({
            "field": "format",
            "action": warning,
            "penalty": "Review recommended"
        })

    # General best practices
    best_practices = [
        {
            "field": "product label",
            "note": "Ensure all mandatory declarations remain clearly visible."
        },
        {
            "field": "text readability",
            "note": "Use clear and sufficiently readable text on the package."
        },
        {
            "field": "verification",
            "note": "Manually review low-confidence OCR results before final approval."
        }
    ]

    return {
        "immediate_actions": immediate_actions,
        "format_corrections": format_corrections,
        "best_practices": best_practices
    }