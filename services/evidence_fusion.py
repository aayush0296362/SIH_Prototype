"""
LMSCAN Evidence Fusion Layer

Combines:
    1. deterministic extraction.py
    2. OpenRouter vision semantics
    3. OCR evidence

The fusion layer is deliberately conservative.

Priority rules:
- If deterministic and AI agree, confidence increases.
- If deterministic is empty and AI has evidence-backed output, AI can fill it.
- If they disagree, do not silently overwrite the deterministic value.
  Mark the field "unclear" and preserve both candidates.
- AI confidence is NOT treated as calibrated probability.
- No legal compliance decision happens here.

The returned structure is designed to be reusable by both:
    Consumer Portal
    Inspector Portal
"""

from __future__ import annotations

from copy import deepcopy
from difflib import SequenceMatcher
from typing import Any, Dict, Iterable, List, Optional


FIELDS = [
    "product_name",
    "ingredients",
    "nutrition",
    "veg_nonveg",
    "fssai_license_number",
    "mrp",
    "net_quantity",
    "batch_number",
    "manufacturing_date",
    "expiry_date",
    "best_before",
    "manufacturer",
    "manufacturer_address",
    "consumer_care",
    "country_of_origin",
    "allergen_declaration",
    "storage_instructions",
    "directions_for_use",
]


# Fields where formatting differences should usually not count as a conflict.
NORMALIZE_NUMERIC = {
    "mrp",
    "net_quantity",
    "batch_number",
    "fssai_license_number",
    "consumer_care",
}


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _norm(value: Any) -> str:
    """Normalize only for comparison; never use this as displayed evidence."""
    value = _text(value).lower()

    replacements = {
        "₹": "rs ",
        "rs.": "rs ",
        "m.r.p.": "mrp ",
        "m.r.p": "mrp ",
        "kg.": "kg",
        "kgs": "kg",
        "licence": "license",
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    return " ".join(value.split())


def _compact(value: Any) -> str:
    return "".join(ch for ch in _norm(value) if ch.isalnum())


def _similarity(a: Any, b: Any) -> float:
    aa = _norm(a)
    bb = _norm(b)

    if not aa or not bb:
        return 0.0

    if aa == bb:
        return 1.0

    # Compact comparison helps with punctuation/spacing differences.
    ca = _compact(a)
    cb = _compact(b)

    if ca and cb and ca == cb:
        return 1.0

    return SequenceMatcher(None, aa, bb).ratio()


def _is_number_like(value: Any) -> bool:
    value = _text(value)
    return any(ch.isdigit() for ch in value)


def _deterministic_quality(field: str, value: Any) -> float:
    """
    Conservative baseline quality for existing deterministic extraction.

    This is a fusion weight, not a probability and not OCR confidence.
    """
    if not value:
        return 0.0

    value = _text(value)

    quality = 0.72

    if field == "fssai_license_number":
        quality += 0.08 if len(
            "".join(ch for ch in value if ch.isdigit())
        ) >= 14 else 0.0

    if field in {"mrp", "net_quantity", "batch_number"}:
        quality += 0.05 if _is_number_like(value) else 0.0

    if field in {"product_name", "manufacturer", "manufacturer_address"}:
        quality += 0.04 if len(value.split()) >= 2 else 0.0

    if field in {"manufacturing_date", "expiry_date", "best_before"}:
        quality += 0.04 if _is_number_like(value) else 0.0

    return min(0.95, quality)


def _ai_quality(ai_field: Dict[str, Any]) -> float:
    if not isinstance(ai_field, dict):
        return 0.0

    if ai_field.get("status") != "detected":
        return 0.0

    if not ai_field.get("value"):
        return 0.0

    evidence_ids = ai_field.get("evidence_ids") or []
    evidence_count = len(evidence_ids)

    try:
        ai_conf = float(ai_field.get("confidence", 0.0))
    except (TypeError, ValueError):
        ai_conf = 0.0

    ai_conf = max(0.0, min(1.0, ai_conf))

    # AI confidence is treated as a signal, not truth.
    score = 0.45 + (0.35 * ai_conf)
    score += min(0.12, 0.04 * evidence_count)

    return min(0.94, score)


def _candidate(
    value: Any,
    source: str,
    quality: float,
    ai_field: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    item = {
        "value": _text(value),
        "source": source,
        "quality": round(quality, 4),
    }

    if ai_field:
        item["ai_confidence"] = float(ai_field.get("confidence", 0.0) or 0.0)
        item["evidence_ids"] = list(ai_field.get("evidence_ids") or [])
        item["evidence"] = list(ai_field.get("evidence") or [])
        item["reason"] = _text(ai_field.get("reason"))

    return item


def _merge_metadata(
    field: str,
    deterministic_value: Any,
    ai_field: Dict[str, Any],
    final_value: Optional[str],
    status: str,
    decision: str,
) -> Dict[str, Any]:
    ai_value = ai_field.get("value")

    evidence = list(ai_field.get("evidence") or [])
    evidence_ids = list(ai_field.get("evidence_ids") or [])

    result = {
        "field": field,
        "value": final_value,
        "status": status,
        "decision": decision,
        "deterministic_value": (
            _text(deterministic_value) if deterministic_value else None
        ),
        "ai_value": _text(ai_value) if ai_value else None,
        "confidence": 0.0,
        "source": "fusion",
        "evidence": evidence,
        "evidence_ids": evidence_ids,
        "reason": _text(ai_field.get("reason")),
    }

    return result


def fuse_field(
    field: str,
    deterministic_value: Any,
    ai_field: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Fuse one field conservatively.

    Agreement:
        same semantic value -> DETECTED / higher confidence

    AI-only:
        deterministic empty + AI detected with evidence -> DETECTED

    Conflict:
        both values exist but differ materially -> UNCLEAR
    """
    ai_field = ai_field if isinstance(ai_field, dict) else {}
    d_value = _text(deterministic_value)
    a_status = _text(ai_field.get("status")).lower()
    a_value = _text(ai_field.get("value"))

    # No deterministic value and no AI value.
    if not d_value and (not a_value or a_status == "missing"):
        result = _merge_metadata(
            field, deterministic_value, ai_field, None, "missing", "no_evidence"
        )
        result["confidence"] = 0.0
        result["reason"] = "No reliable deterministic or AI evidence."
        return result

    # Deterministic value only.
    if d_value and not a_value:
        quality = _deterministic_quality(field, d_value)
        result = _merge_metadata(
            field,
            deterministic_value,
            ai_field,
            d_value,
            "detected",
            "deterministic_only",
        )
        result["confidence"] = round(quality, 3)
        result["evidence"] = []
        result["evidence_ids"] = []
        result["reason"] = "Supported by the deterministic extraction layer."
        return result

    # AI value exists but isn't actually marked detected.
    if a_value and a_status != "detected":
        if d_value:
            quality = _deterministic_quality(field, d_value)
            result = _merge_metadata(
                field,
                deterministic_value,
                ai_field,
                d_value,
                "unclear",
                "ai_unclear_preserved_deterministic",
            )
            result["confidence"] = round(min(quality, 0.82), 3)
            result["reason"] = (
                "Deterministic evidence exists, but AI evidence is uncertain."
            )
            return result

        result = _merge_metadata(
            field, deterministic_value, ai_field, a_value, "unclear", "ai_unclear"
        )
        result["confidence"] = round(_ai_quality(ai_field) * 0.65, 3)
        return result

    # AI detected with evidence.
    if not d_value:
        quality = _ai_quality(ai_field)
        result = _merge_metadata(
            field, deterministic_value, ai_field, a_value, "detected", "ai_fill"
        )
        result["confidence"] = round(quality, 3)
        result["reason"] = (
            "Filled from AI semantic extraction with supporting OCR evidence."
        )
        return result

    # Both exist: compare semantic similarity.
    similarity = _similarity(d_value, a_value)

    # Numeric/code fields should be stricter than free text.
    threshold = 0.92 if field in NORMALIZE_NUMERIC else 0.84

    if similarity >= threshold:
        d_quality = _deterministic_quality(field, d_value)
        a_quality = _ai_quality(ai_field)

        # Keep deterministic formatting/value as the stable canonical value.
        # AI evidence is still attached to the fused result.
        final = d_value

        confidence = min(
            0.98,
            0.58
            + (0.20 * d_quality)
            + (0.17 * a_quality)
            + (0.05 * similarity),
        )

        result = _merge_metadata(
            field,
            deterministic_value,
            ai_field,
            final,
            "detected",
            "agreement",
        )
        result["confidence"] = round(confidence, 3)
        result["reason"] = (
            "Deterministic and AI semantic extraction agree on the field."
        )
        return result

    # Material disagreement: preserve both values.
    d_quality = _deterministic_quality(field, d_value)
    a_quality = _ai_quality(ai_field)

    result = _merge_metadata(
        field,
        deterministic_value,
        ai_field,
        d_value,
        "unclear",
        "conflict",
    )
    result["confidence"] = round(min(d_quality, a_quality), 3)
    result["conflict"] = True
    result["conflict_similarity"] = round(similarity, 3)
    result["alternatives"] = [
        {
            "value": d_value,
            "source": "deterministic",
            "quality": round(d_quality, 3),
        },
        {
            "value": a_value,
            "source": "openrouter",
            "quality": round(a_quality, 3),
            "evidence_ids": list(ai_field.get("evidence_ids") or []),
            "evidence": list(ai_field.get("evidence") or []),
        },
    ]
    result["reason"] = (
        "Deterministic and AI extraction disagree; human review is required."
    )
    return result


def fuse_results(
    deterministic: Optional[Dict[str, Any]],
    ai_result: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Fuse the complete package extraction into a reusable core result."""
    deterministic = deterministic or {}
    ai_result = ai_result or {}
    ai_fields = ai_result.get("fields", {})

    fields: Dict[str, Any] = {}

    for field in FIELDS:
        fields[field] = fuse_field(
            field,
            deterministic.get(field),
            ai_fields.get(field, {}),
        )

    detected = sum(
        1 for item in fields.values() if item["status"] == "detected"
    )
    unclear = sum(
        1 for item in fields.values() if item["status"] == "unclear"
    )
    missing = sum(
        1 for item in fields.values() if item["status"] == "missing"
    )

    return {
        "fields": fields,
        "detected_count": detected,
        "unclear_count": unclear,
        "missing_count": missing,
        "total_fields": len(FIELDS),
        "provider": ai_result.get("provider", "openrouter"),
        "model": ai_result.get("model"),
        "ai_errors": list(ai_result.get("errors") or []),
    }


def apply_fusion_to_legacy_result(
    deterministic: Optional[Dict[str, Any]],
    fused_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Produce a legacy-compatible declaration dictionary.

    Existing app/compliance code can keep reading:
        result["product_name"]
        result["mrp"]
        etc.

    Detailed fusion metadata remains available in:
        result["fusion"]
    """
    merged = deepcopy(deterministic or {})

    for field in FIELDS:
        item = fused_result.get("fields", {}).get(field, {})
        if item.get("status") == "detected" and item.get("value"):
            merged[field] = item["value"]

    merged["fusion"] = fused_result
    merged["fusion_fields"] = fused_result.get("fields", {})
    return merged


def fuse_package(
    deterministic: Optional[Dict[str, Any]],
    ai_result: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Convenience function returning the legacy-compatible fused result."""
    fused = fuse_results(deterministic, ai_result)
    return apply_fusion_to_legacy_result(deterministic, fused)


__all__ = [
    "FIELDS",
    "fuse_field",
    "fuse_results",
    "apply_fusion_to_legacy_result",
    "fuse_package",
]
