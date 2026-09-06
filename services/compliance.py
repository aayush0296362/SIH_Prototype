"""LMSCAN context-aware compliance engine.

Extraction answers: "What evidence did we read?"
Rules answer: "Which declarations should be checked for this package?"
The engine never invents missing label data.
"""

from services.rules import get_rules

# Kept for backward compatibility with the current Streamlit UI.
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

ALIASES = {
    "generic_name": "product_name",
    "fssai_license": "fssai_license_number",
    "licence_number": "fssai_license_number",
    "license_number": "fssai_license_number",
}


def _value(declarations, field):
    if not declarations:
        return None
    value = declarations.get(field)
    if value:
        return value
    for alias, target in ALIASES.items():
        if target == field and declarations.get(alias):
            return declarations.get(alias)
    return None


def _infer_context(declarations):
    text = " ".join(str(x) for x in (declarations or {}).get("raw_text", [])).lower()
    country = _value(declarations, "country_of_origin")
    manufacturer = str(_value(declarations, "manufacturer") or "").lower()

    imported_markers = ("imported", "country of origin", "made in", "packed in")
    is_imported = bool(country) or any(marker in text for marker in imported_markers)
    is_food = any(word in text for word in (
        "ingredient", "ingredients", "fssai", "nutrition", "net weight", "food",
        "dal", "rice", "flour", "masoor", "pulse", "spice",
    )) or bool(_value(declarations, "fssai_license_number"))

    return {
        "is_food": is_food,
        "is_imported": is_imported,
        "unit_sale_price_applicable": False,
        "veg_nonveg_applicable": is_food,
        "allergen_trigger": False,
        "additive_trigger": False,
        "instruction_trigger": False,
        "manufacturer_text": manufacturer,
    }


def _applicable(rule, context):
    a = rule.applicability
    if a == "always":
        return True
    if a == "food":
        return bool(context["is_food"])
    if a == "imported":
        return bool(context["is_imported"])
    if a == "unit_sale_price":
        return bool(context["unit_sale_price_applicable"])
    if a == "veg_nonveg":
        return bool(context["veg_nonveg_applicable"])
    if a == "allergen_trigger":
        return bool(context["allergen_trigger"])
    if a == "additive_trigger":
        return bool(context["additive_trigger"])
    if a == "instruction_trigger":
        return bool(context["instruction_trigger"])
    return False


def _status_for_rule(rule, declarations, context):
    if not _applicable(rule, context):
        return "not_applicable", None, "Rule not applicable to this package/context."

    value = _value(declarations, rule.evidence_field) if rule.evidence_field else None
    if value:
        return "detected", value, f"{rule.requirement} detected."

    # The MVP intentionally avoids auto-failing conditional requirements whose
    # trigger cannot be established from the current deterministic extractor.
    if rule.applicability in {"allergen_trigger", "additive_trigger", "instruction_trigger"}:
        return "unclear", None, f"{rule.requirement} could not be established from current evidence."

    return "missing", None, f"{rule.requirement} was not detected."


def _legacy_findings(declarations):
    findings = []
    missing_fields = []
    for field, label in REQUIRED_FIELDS.items():
        value = _value(declarations, field)
        if value:
            findings.append({"field": field, "label": label, "status": "detected", "value": value,
                             "message": f"{label} detected."})
        else:
            missing_fields.append(field)
            findings.append({"field": field, "label": label, "status": "missing", "value": None,
                             "message": f"{label} was not detected."})
    return findings, missing_fields


def check_compliance(declarations):
    context = _infer_context(declarations)
    rule_findings = []

    for rule in get_rules():
        status, value, message = _status_for_rule(rule, declarations, context)
        rule_findings.append({
            "rule_id": rule.rule_id,
            "authority": rule.authority,
            "requirement": rule.requirement,
            "field": rule.evidence_field,
            "severity": rule.severity,
            "applicability": rule.applicability,
            "status": status,
            "value": value,
            "message": message,
            "source": rule.source,
        })

    applicable = [x for x in rule_findings if x["status"] != "not_applicable"]
    detected = [x for x in applicable if x["status"] == "detected"]
    missing = [x for x in applicable if x["status"] == "missing"]
    unclear = [x for x in applicable if x["status"] == "unclear"]

    # Compliance percentage measures satisfied applicable rules only.
    compliance_percent = round((len(detected) / len(applicable)) * 100, 1) if applicable else 100.0

    if missing:
        status = "review"
    elif unclear:
        status = "review"
    else:
        status = "pass"

    # Preserve the current 10-field app contract as well.
    legacy_findings, legacy_missing = _legacy_findings(declarations)

    return {
        "status": status,
        "findings": legacy_findings,
        "missing_fields": legacy_missing,
        "total_fields": len(REQUIRED_FIELDS),
        "detected_fields": len(REQUIRED_FIELDS) - len(legacy_missing),
        "rules": rule_findings,
        "total_rules": len(rule_findings),
        "applicable_rules": len(applicable),
        "detected_rules": len(detected),
        "missing_rules": len(missing),
        "unclear_rules": len(unclear),
        "compliance_percent": compliance_percent,
        "context": context,
    }
