"""
LMSCAN Compliance Engine

Evaluates extracted package declarations and creates
evidence-based compliance findings.

Important:
OCR not detecting a declaration does not automatically mean
the package is legally non-compliant. Such fields are marked
for human/inspector review.
"""


REQUIRED_FIELDS = {
    "product_name": {
        "label": "Product Name",
        "required": True
    },
    "mrp": {
        "label": "MRP",
        "required": True
    },
    "net_quantity": {
        "label": "Net Quantity",
        "required": True
    },
    "manufacturer": {
        "label": "Manufacturer / Packer",
        "required": True
    },
    "manufacturing_date": {
        "label": "Manufacturing / Packing Date",
        "required": True
    },
    "expiry_date": {
        "label": "Expiry Date",
        "required": False
    },
    "best_before": {
        "label": "Best Before",
        "required": False
    },
    "consumer_care": {
        "label": "Consumer Care",
        "required": True
    },
    "country_of_origin": {
        "label": "Country of Origin",
        "required": False
    },
    "batch_number": {
        "label": "Batch Number",
        "required": True
    },
}


def check_compliance(declarations):
    """
    Check extracted package declarations.

    Returns an evidence-based compliance result.

    Status meanings:

    detected:
        Declaration was found in OCR evidence.

    review:
        Declaration could not be verified from the
        submitted OCR evidence.

    pass:
        All required declarations were detected.

    review:
        One or more required declarations need
        human/inspector verification.
    """

    findings = []
    review_fields = []
    detected_fields = 0

    for field, config in REQUIRED_FIELDS.items():

        label = config["label"]
        required = config["required"]

        value = declarations.get(field)

        if value:
            detected_fields += 1

            findings.append({
                "field": field,
                "label": label,
                "status": "detected",
                "value": value,
                "required": required,
                "message": f"{label} detected in the provided evidence."
            })

        else:

            # Only required fields affect the inspection status.
            if required:
                review_fields.append(field)

                message = (
                    f"{label} could not be verified from "
                    "the provided evidence and requires review."
                )

            else:
                message = (
                    f"{label} was not detected in the provided "
                    "evidence. This declaration may be "
                    "product-specific or require further review."
                )

            findings.append({
                "field": field,
                "label": label,
                "status": "review",
                "value": None,
                "required": required,
                "message": message
            })

    # Final inspection status
    if not review_fields:
        status = "pass"
    else:
        status = "review"

    return {
        "status": status,

        "findings": findings,

        # Keeping this name preserves compatibility
        # with the existing Streamlit UI.
        "missing_fields": review_fields,

        "review_fields": review_fields,

        "total_fields": len(REQUIRED_FIELDS),

        "detected_fields": detected_fields,

        "review_count": len(review_fields)
    }