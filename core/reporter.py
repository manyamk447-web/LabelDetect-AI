import json
import csv
import io
from datetime import datetime


class ComplianceReporter:

    @staticmethod
    def generate_json(extracted_fields, compliance_report):

        fields = {}

        for field_id, field in extracted_fields.items():

            fields[field_id] = {
                "value": field.extracted_value,
                "confidence": field.confidence,
                "found": field.found
            }

        data = {
            "generated_at": datetime.now().isoformat(),
            "overall_status": compliance_report.overall_status,
            "compliance_score": compliance_report.compliance_score,
            "fields": fields,
            "critical_violations":
                compliance_report.critical_violations,
            "warnings":
                compliance_report.warnings
        }

        return json.dumps(
            data,
            indent=4
        )

    @staticmethod
    def generate_csv(extracted_fields, compliance_report):

        output = io.StringIO()

        writer = csv.writer(output)

        writer.writerow([
            "Field",
            "Detected Value",
            "Confidence",
            "Found",
            "Status",
            "Score"
        ])

        for field_id, field in extracted_fields.items():

            breakdown = (
                compliance_report.field_breakdown.get(
                    field_id,
                    {
                        "status": "FAIL",
                        "score": 0
                    }
                )
            )

            writer.writerow([
                field_id,
                field.extracted_value,
                field.confidence,
                field.found,
                breakdown["status"],
                breakdown["score"]
            ])

        return output.getvalue()

    @staticmethod
    def generate_pdf(
        product_name,
        fields,
        report,
        annotated_image_rgb=None
    ):

        try:

            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Table,
                TableStyle
            )
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet

        except ImportError:

            return (
                b"PDF generation requires reportlab. "
                b"Install it using: pip install reportlab"
            )

        buffer = io.BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4
        )

        styles = getSampleStyleSheet()

        elements = []

        elements.append(
            Paragraph(
                "Product Label Compliance Audit",
                styles["Title"]
            )
        )

        elements.append(
            Spacer(1, 12)
        )

        elements.append(
            Paragraph(
                f"Product: {product_name}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"Overall Status: {report.overall_status}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"Compliance Score: "
                f"{report.compliance_score:.1f}/100",
                styles["Normal"]
            )
        )

        elements.append(
            Spacer(1, 20)
        )

        table_data = [
            [
                "Field",
                "Value",
                "Confidence",
                "Status"
            ]
        ]

        for field_id, field in fields.items():

            breakdown = report.field_breakdown.get(
                field_id,
                {
                    "status": "FAIL",
                    "score": 0
                }
            )

            table_data.append([
                field_id,
                field.extracted_value or "NOT DETECTED",
                f"{field.confidence * 100:.0f}%",
                breakdown["status"]
            ])

        table = Table(table_data)

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        elements.append(table)

        elements.append(
            Spacer(1, 20)
        )

        if report.critical_violations:

            elements.append(
                Paragraph(
                    "Critical Violations",
                    styles["Heading2"]
                )
            )

            for violation in report.critical_violations:

                elements.append(
                    Paragraph(
                        f"• {violation}",
                        styles["Normal"]
                    )
                )

        if report.warnings:

            elements.append(
                Paragraph(
                    "Warnings",
                    styles["Heading2"]
                )
            )

            for warning in report.warnings:

                elements.append(
                    Paragraph(
                        f"• {warning}",
                        styles["Normal"]
                    )
                )

        document.build(elements)

        return buffer.getvalue()