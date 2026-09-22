from dataclasses import dataclass, field


@dataclass
class ComplianceReport:
    overall_status: str
    compliance_score: float
    critical_violations: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    field_breakdown: dict = field(default_factory=dict)


class ComplianceEngine:

    REQUIRED_FIELDS = [
        "product_name",
        "manufacturer",
        "address",
        "net_quantity",
        "mrp",
        "packing_date",
        "consumer_care",
        "country_of_origin"
    ]

    def evaluate(self, extracted_fields):

        field_breakdown = {}
        critical_violations = []
        warnings = []

        total_score = 0

        for field_id in self.REQUIRED_FIELDS:

            field = extracted_fields.get(field_id)

            if field and field.found:

                score = 12.5
                status = "PASS"

                # Lower confidence → warning
                if field.confidence < 0.60:
                    status = "WARNING"
                    warnings.append(
                        f"{field_id.replace('_', ' ').title()} "
                        f"has low OCR confidence."
                    )
                    score = 8.0

            else:

                score = 0
                status = "FAIL"

                critical_violations.append(
                    f"Missing mandatory field: "
                    f"{field_id.replace('_', ' ').title()}"
                )

            total_score += score

            field_breakdown[field_id] = {
                "status": status,
                "score": score
            }

        compliance_score = total_score

        if critical_violations:

            overall_status = "FAIL"

        elif warnings:

            overall_status = "WARNING"

        else:

            overall_status = "PASS"

        return ComplianceReport(
            overall_status=overall_status,
            compliance_score=compliance_score,
            critical_violations=critical_violations,
            warnings=warnings,
            field_breakdown=field_breakdown
        )