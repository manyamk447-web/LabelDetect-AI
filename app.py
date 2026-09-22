import streamlit as st
from PIL import Image
import numpy as np
import re
import json
from io import BytesIO


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="AI Product Label Compliance Checker",
    page_icon="📦",
    layout="wide"
)


# =========================================================
# OCR
# =========================================================

@st.cache_resource
def get_ocr():

    from paddleocr import PaddleOCR

    return PaddleOCR(
        lang="en",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        enable_mkldnn=False
    )


def run_ocr(image):

    ocr = get_ocr()

    img = np.asarray(
        image.convert("RGB"),
        dtype=np.uint8
    )

    result = ocr.predict(img)

    texts = []
    scores = []

    for res in result:

        data = None

        try:
            data = res.json
        except Exception:
            pass

        if callable(data):

            try:
                data = data()

            except Exception:
                pass

        if isinstance(data, str):

            try:
                data = json.loads(data)

            except Exception:
                data = None

        if isinstance(data, dict):

            if "res" in data:
                data = data["res"]

            detected_texts = data.get(
                "rec_texts",
                []
            )

            detected_scores = data.get(
                "rec_scores",
                []
            )

            for i, text in enumerate(
                detected_texts
            ):

                text = str(text).strip()

                if not text:
                    continue

                confidence = 0.0

                if i < len(detected_scores):

                    try:
                        confidence = float(
                            detected_scores[i]
                        )

                    except Exception:
                        confidence = 0.0

                if confidence >= 0.30:

                    texts.append(text)
                    scores.append(confidence)

    return texts, scores


# =========================================================
# LEGAL METROLOGY DECLARATIONS
# =========================================================

# These are based on the mandatory declarations described
# by the Department of Consumer Affairs under Rule 6.

RULE_FIELDS = {

    "Manufacturer / Packer / Importer":
        [
            r"(?:manufactured|mfd|manufactured|packed|packer|imported|importer)"
            r"\s*(?:by|from)?\s*[:\-]?\s*(.+)"
        ],

    "Common / Generic Name":
        [
            r"(?:product\s*name|commodity|item|product)"
            r"\s*[:\-]\s*(.+)"
        ],

    "Net Quantity":
        [
            r"net\s*(?:quantity|qty|weight|wt|content)"
            r"\s*[:\-]?\s*(.+)"
        ],

    "Manufacture / Pack / Import Date":
        [
            r"(?:manufactured|mfg|manufacturing|packed|packing|pkd|imported)"
            r"(?:\s*date)?\s*[:\-]?\s*(.+)"
        ],

    "MRP":
        [
            r"(?:mrp|maximum\s*retail\s*price)"
            r"\s*[:\-]?\s*(.+)"
        ],

    "Consumer Care":
        [
            r"(?:consumer\s*care|customer\s*care|helpline|toll\s*free)"
            r"\s*[:\-]?\s*(.+)"
        ],

    "Country of Origin":
        [
            r"(?:country\s*of\s*origin|made\s*in)"
            r"\s*[:\-]?\s*(.+)"
        ],

    "Best Before / Use By":
        [
            r"(?:best\s*before|use\s*by|expiry|expires)"
            r"\s*[:\-]?\s*(.+)"
        ],

    "Dimensions":
        [
            r"(?:dimension|dimensions|size)"
            r"\s*[:\-]?\s*(.+)"
        ],

    "Unit Sale Price":
        [
            r"(?:unit\s*sale\s*price|unit\s*price)"
            r"\s*[:\-]?\s*(.+)"
        ]
}


def extract_rule_fields(lines):

    extracted = {}

    for field in RULE_FIELDS:

        extracted[field] = "Not detected"

    for line in lines:

        clean_line = line.strip()

        if not clean_line:
            continue

        for field, patterns in RULE_FIELDS.items():

            if extracted[field] != "Not detected":
                continue

            for pattern in patterns:

                match = re.search(
                    pattern,
                    clean_line,
                    re.IGNORECASE
                )

                if match:

                    value = match.group(
                        match.lastindex
                    ).strip()

                    if value:
                        extracted[field] = value

                    break

    return extracted


# =========================================================
# RULE APPLICABILITY
# =========================================================

def check_compliance(
    fields,
    imported,
    perishable,
    dimensions_relevant
):

    results = []

    # -----------------------------------------------------
    # Always checked declarations
    # -----------------------------------------------------

    always_required = [
        "Manufacturer / Packer / Importer",
        "Common / Generic Name",
        "Net Quantity",
        "Manufacture / Pack / Import Date",
        "MRP",
        "Consumer Care",
        "Unit Sale Price"
    ]

    for field in always_required:

        if fields[field] == "Not detected":

            results.append({
                "field": field,
                "status": "FAIL",
                "reason": "Mandatory declaration not detected.",
                "action": f"Add or verify {field} on the retail package."
            })

        else:

            results.append({
                "field": field,
                "status": "PASS",
                "reason": "Declaration detected by OCR.",
                "action": "Human reviewer should verify the declaration."
            })


    # -----------------------------------------------------
    # Country of Origin
    # -----------------------------------------------------

    if imported:

        if fields["Country of Origin"] == "Not detected":

            results.append({
                "field": "Country of Origin",
                "status": "FAIL",
                "reason": "Imported product selected but country of origin was not detected.",
                "action": "Add/verify country of origin."
            })

        else:

            results.append({
                "field": "Country of Origin",
                "status": "PASS",
                "reason": "Country of origin detected.",
                "action": "Human reviewer should verify it."
            })

    else:

        results.append({
            "field": "Country of Origin",
            "status": "N/A",
            "reason": "Product marked as domestic/not imported.",
            "action": "No country-of-origin check applied."
        })


    # -----------------------------------------------------
    # Best Before / Use By
    # -----------------------------------------------------

    if perishable:

        if fields["Best Before / Use By"] == "Not detected":

            results.append({
                "field": "Best Before / Use By",
                "status": "FAIL",
                "reason": "Product selected as one that may become unfit for consumption.",
                "action": "Add/verify best-before or use-by declaration."
            })

        else:

            results.append({
                "field": "Best Before / Use By",
                "status": "PASS",
                "reason": "Date declaration detected.",
                "action": "Human reviewer should verify it."
            })

    else:

        results.append({
            "field": "Best Before / Use By",
            "status": "N/A",
            "reason": "Product not marked as requiring this conditional declaration.",
            "action": "No best-before/use-by check applied."
        })


    # -----------------------------------------------------
    # Dimensions
    # -----------------------------------------------------

    if dimensions_relevant:

        if fields["Dimensions"] == "Not detected":

            results.append({
                "field": "Dimensions",
                "status": "FAIL",
                "reason": "Dimensions marked as relevant but not detected.",
                "action": "Add/verify applicable dimensions."
            })

        else:

            results.append({
                "field": "Dimensions",
                "status": "PASS",
                "reason": "Dimensions detected.",
                "action": "Human reviewer should verify them."
            })

    else:

        results.append({
            "field": "Dimensions",
            "status": "N/A",
            "reason": "Dimensions marked as not relevant.",
            "action": "No dimensions check applied."
        })


    return results


# =========================================================
# SCORE
# =========================================================

def calculate_score(results):

    applicable = [
        r for r in results
        if r["status"] != "N/A"
    ]

    if not applicable:
        return 0

    passed = [
        r for r in applicable
        if r["status"] == "PASS"
    ]

    return round(
        len(passed) /
        len(applicable) *
        100,
        1
    )


# =========================================================
# AUDIT REPORT
# =========================================================

def create_report(
    extracted,
    compliance_results,
    verified,
    reviewer,
    decision,
    corrections,
    comments,
    score
):

    return {

        "system": "AI Product Label Compliance Verification System",

        "legal_basis": [
            "Legal Metrology Act, 2009",
            "Legal Metrology (Packaged Commodities) Rules, 2011",
            "Rule 6 mandatory declaration checks"
        ],

        "initial_ocr_result": extracted,

        "compliance_score": score,

        "compliance_findings":
            compliance_results,

        "human_in_the_loop": {

            "reviewer": reviewer,

            "decision": decision,

            "verified_information": verified,

            "corrections": corrections,

            "comments": comments
        },

        "final_status": decision,

        "disclaimer":
            "This is an automated screening and audit-support tool. "
            "Final legal compliance determination should be made by "
            "the responsible manufacturer/packer/importer or competent "
            "Legal Metrology authority, considering the applicable "
            "commodity-specific provisions and exemptions."
    }


# =========================================================
# UI
# =========================================================

st.title(
    "📦 AI Product Label Compliance Verification System"
)

st.write(
    "Upload a retail product label. The system uses OCR to "
    "read information from the uploaded image, checks selected "
    "Legal Metrology declarations, and sends uncertain or "
    "missing information to a human reviewer."
)


uploaded_file = st.file_uploader(
    "Upload Product Label",
    type=["png", "jpg", "jpeg"]
)


# =========================================================
# EVERYTHING BELOW ONLY RUNS AFTER IMAGE UPLOAD
# =========================================================

if uploaded_file is not None:

    image = Image.open(
        uploaded_file
    ).convert("RGB")

    st.subheader(
        "📷 Uploaded Product"
    )

    st.image(
        image,
        width="stretch"
    )


    # -----------------------------------------------------
    # PRODUCT TYPE / APPLICABILITY
    # -----------------------------------------------------

    st.subheader(
        "⚙️ Product Information"
    )

    imported = st.checkbox(
        "This is an imported product"
    )

    perishable = st.checkbox(
        "This product may become unfit for human consumption"
    )

    dimensions_relevant = st.checkbox(
        "Dimensions are relevant to this commodity"
    )


    # -----------------------------------------------------
    # OCR
    # -----------------------------------------------------

    with st.spinner(
        "Reading the uploaded product label..."
    ):

        try:

            texts, scores = run_ocr(
                image
            )

        except Exception as e:

            st.error(
                f"OCR failed: {e}"
            )

            st.stop()


    if not texts:

        st.error(
            "No readable text was detected in this image."
        )

        st.info(
            "Please upload a clearer image of the product label."
        )

        st.stop()


    # -----------------------------------------------------
    # OCR OUTPUT
    # -----------------------------------------------------

    st.subheader(
        "🔎 OCR Text Detected From This Product"
    )

    for i, text in enumerate(texts):

        st.write(
            f"• {text} "
            f"(confidence: {scores[i]:.2f})"
        )


    # -----------------------------------------------------
    # EXTRACTION
    # -----------------------------------------------------

    extracted = extract_rule_fields(
        texts
    )


    st.subheader(
        "📋 Extracted Legal Metrology Information"
    )

    for field, value in extracted.items():

        if value == "Not detected":

            st.warning(
                f"⚠️ {field}: Not detected"
            )

        else:

            st.success(
                f"✅ {field}: {value}"
            )


    # -----------------------------------------------------
    # COMPLIANCE
    # -----------------------------------------------------

    compliance_results = check_compliance(
        extracted,
        imported,
        perishable,
        dimensions_relevant
    )

    score = calculate_score(
        compliance_results
    )


    st.subheader(
        "⚖️ Legal Metrology Screening"
    )

    st.metric(
        "Initial Compliance Score",
        f"{score}%"
    )


    for result in compliance_results:

        if result["status"] == "PASS":

            st.success(
                f"✅ {result['field']} — PASS\n\n"
                f"{result['reason']}"
            )

        elif result["status"] == "FAIL":

            st.error(
                f"❌ {result['field']} — FAIL\n\n"
                f"{result['reason']}\n\n"
                f"Correction: {result['action']}"
            )

        else:

            st.info(
                f"ℹ️ {result['field']} — N/A\n\n"
                f"{result['reason']}"
            )


    # =====================================================
    # HUMAN IN THE LOOP
    # =====================================================

    st.divider()

    st.header(
        "👤 Human-in-the-Loop Review"
    )

    st.write(
        "OCR results are not treated as final legal evidence. "
        "A reviewer verifies the extracted declarations and "
        "can correct OCR errors before the final report."
    )


    verified_fields = {}

    for field in extracted:

        current_value = extracted[field]

        verified_fields[field] = st.text_input(
            f"Verify: {field}",
            value=""
            if current_value == "Not detected"
            else current_value,
            key=f"verify_{field}"
        )


    st.subheader(
        "🛠️ Corrections Identified by Reviewer"
    )

    corrections = st.text_area(
        "Enter corrections required",
        placeholder=(
            "Example: OCR read MRP as Rs. 180. "
            "Correct value verified from label is Rs. 150."
        )
    )


    reviewer = st.text_input(
        "Reviewer Name"
    )


    comments = st.text_area(
        "Reviewer Comments"
    )


    decision = st.selectbox(
        "Final Human Review Decision",
        [
            "Approved",
            "Approved with Corrections",
            "Rejected - Correction Required"
        ]
    )


    # =====================================================
    # FINAL REPORT
    # =====================================================

    if st.button(
        "📄 Generate Final Compliance Report"
    ):

        final_report = create_report(
            extracted,
            compliance_results,
            verified_fields,
            reviewer,
            decision,
            corrections,
            comments,
            score
        )


        st.session_state[
            "final_report"
        ] = final_report


    # =====================================================
    # DISPLAY FINAL REPORT
    # =====================================================

    if "final_report" in st.session_state:

        report = st.session_state[
            "final_report"
        ]

        st.divider()

        st.header(
            "📄 Final Product Compliance Report"
        )


        st.subheader(
            "Product Information Verified by Human"
        )

        for field, value in report[
            "human_in_the_loop"
        ][
            "verified_information"
        ].items():

            if value.strip():

                st.write(
                    f"**{field}:** {value}"
                )

            else:

                st.warning(
                    f"**{field}:** Not provided"
                )


        st.subheader(
            "⚠️ Required Corrections"
        )

        if report[
            "human_in_the_loop"
        ]["corrections"].strip():

            st.warning(
                report[
                    "human_in_the_loop"
                ]["corrections"]
            )

        else:

            st.success(
                "No additional corrections recorded by reviewer."
            )


        st.subheader(
            "👤 Human Decision"
        )

        st.info(
            report[
                "human_in_the_loop"
            ]["decision"]
        )


        st.subheader(
            "⚖️ Rule-Based Findings"
        )

        for finding in report[
            "compliance_findings"
        ]:

            if finding["status"] == "FAIL":

                st.error(
                    f"{finding['field']}: "
                    f"{finding['reason']}"
                )

            elif finding["status"] == "PASS":

                st.success(
                    f"{finding['field']}: "
                    f"{finding['reason']}"
                )

            else:

                st.info(
                    f"{finding['field']}: "
                    f"{finding['reason']}"
                )


        # -------------------------------------------------
        # JSON
        # -------------------------------------------------

        json_report = json.dumps(
            report,
            indent=4
        )

        st.download_button(
            "⬇️ Download JSON Audit Report",
            data=json_report,
            file_name="legal_metrology_compliance_report.json",
            mime="application/json"
        )


        # -------------------------------------------------
        # CSV
        # -------------------------------------------------

        csv_lines = [
            "Field,OCR Value,Human Verified Value,Status,Correction"
        ]

        finding_map = {
            item["field"]: item
            for item in report[
                "compliance_findings"
            ]
        }

        for field in extracted:

            original = str(
                report["initial_ocr_result"][field]
            ).replace(",", " ")

            verified = str(
                report["human_in_the_loop"]["verified_information"][field]
            ).replace(",", " ")

            status = finding_map.get(
                field,
                {}
            ).get(
                "status",
                "N/A"
            )

            csv_lines.append(
                f'"{field}",'
                f'"{original}",'
                f'"{verified}",'
                f'"{status}",'
                f'"{report["human_in_the_loop"]["corrections"]}"'
            )