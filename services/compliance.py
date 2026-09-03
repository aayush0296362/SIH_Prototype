"""
LMSCAN Compliance Engine

Checks extracted package declarations against
the required inspection fields.
"""


REQUIRED_FIELDS = {
    "product_name": "Product Name",
    "mrp": "MRP",
    "net_quantity": "Net Quantity",
    "manufacturer": "Manufacturer",
    "manufacturing_date": "Manufacturing Date",
    "expiry_date": "Expiry Date",
    "best_before": "Best Before",
    "consumer_care": "Consumer Care",
    "country_of_origin": "Country of Origin",
    "batch_number": "Batch Number",
}


def check_compliance(declarations):
    """
    Check extracted package declarations.

    Returns a structured compliance result.
    """

    findings = []
    missing_fields = []

    for field, label in REQUIRED_FIELDS.items():

        value = declarations.get(field)

        if value:
            findings.append({
                "field": field,
                "label": label,
                "status": "detected",
                "value": value,
                "message": f"{label} detected."
            })

        else:
            missing_fields.append(field)

            findings.append({
                "field": field,
                "label": label,
                "status": "missing",
                "value": None,
                "message": f"{label} was not detected."
            })

    if not missing_fields:
        status = "pass"

    else:
        status = "review"

    return {
        "status": status,
        "findings": findings,
        "missing_fields": missing_fields,
        "total_fields": len(REQUIRED_FIELDS),
        "detected_fields": (
            len(REQUIRED_FIELDS) - len(missing_fields)
        ),
    }