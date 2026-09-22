from dataclasses import dataclass
import re


@dataclass
class ExtractedField:
    field_id: str
    extracted_value: str = ""
    confidence: float = 0.0
    found: bool = False


class LabelFieldExtractor:

    def __init__(self):
        self.field_patterns = {
            "product_name": [
                r"product\s*name\s*[:\-]?\s*(.+)",
                r"(.+)"
            ],
            "manufacturer": [
                r"manufactured\s*by\s*[:\-]?\s*(.+)",
                r"manufacturer\s*[:\-]?\s*(.+)"
            ],
            "address": [
                r"address\s*[:\-]?\s*(.+)"
            ],
            "net_quantity": [
                r"net\s*(quantity|qty)\s*[:\-]?\s*(.+)",
                r"net\s*wt\.?\s*[:\-]?\s*(.+)"
            ],
            "mrp": [
                r"mrp\s*[:\-]?\s*(.+)",
                r"maximum\s*retail\s*price\s*[:\-]?\s*(.+)"
            ],
            "packing_date": [
                r"packed\s*on\s*[:\-]?\s*(.+)",
                r"mfg\s*date\s*[:\-]?\s*(.+)",
                r"manufacturing\s*date\s*[:\-]?\s*(.+)"
            ],
            "consumer_care": [
                r"consumer\s*care\s*[:\-]?\s*(.+)",
                r"customer\s*care\s*[:\-]?\s*(.+)"
            ],
            "country_of_origin": [
                r"country\s*of\s*origin\s*[:\-]?\s*(.+)",
                r"made\s*in\s*[:\-]?\s*(.+)"
            ]
        }

    def extract_all(self, ocr_lines):

        results = {}

        for field_id in self.field_patterns:

            results[field_id] = ExtractedField(
                field_id=field_id
            )

        for line in ocr_lines:

            text = line.text.strip()

            if not text:
                continue

            text_lower = text.lower()

            for field_id, patterns in self.field_patterns.items():

                for pattern in patterns:

                    match = re.search(
                        pattern,
                        text_lower,
                        re.IGNORECASE
                    )

                    if match:

                        value = match.group(
                            match.lastindex
                        ).strip()

                        results[field_id] = ExtractedField(
                            field_id=field_id,
                            extracted_value=value,
                            confidence=line.confidence,
                            found=True
                        )

                        break

        return results