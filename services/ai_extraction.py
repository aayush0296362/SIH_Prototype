"""
LMSCAN OpenRouter Vision Semantic Extraction

Hybrid design:
    package image(s) + EasyOCR evidence
                ↓
        OpenRouter vision model
                ↓
       strict structured JSON
                ↓
      evidence-backed semantics

The deterministic extractor remains the first source of truth. This module
does not decide legal compliance.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
from typing import Any, Dict, Iterable, List, Optional, Union


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

DEFAULT_MODEL = os.getenv("LMSCAN_AI_MODEL", "qwen/qwen3.5-9b")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _empty_field(status: str = "missing") -> Dict[str, Any]:
    return {
        "value": None,
        "status": status,
        "confidence": 0.0,
        "evidence_ids": [],
        "evidence": [],
        "reason": "",
        "source": "openrouter",
    }


def empty_semantic_result(model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    return {
        "provider": "openrouter",
        "model": model,
        "fields": {field: _empty_field() for field in FIELDS},
        "raw_response": None,
        "errors": [],
    }


def _normalise_ocr(
    ocr_results: Iterable[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    cleaned: List[Dict[str, Any]] = []

    for item in ocr_results or []:
        text = str(item.get("text", "")).strip()
        if not text:
            continue

        try:
            confidence = float(item.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0

        cleaned.append(
            {
                "id": len(cleaned) + 1,
                "text": text,
                "confidence": round(max(0.0, min(1.0, confidence)), 4),
                "source": str(item.get("source", "unknown")),
            }
        )

    return cleaned


def _schema() -> Dict[str, Any]:
    field_schema = {
        "type": "object",
        "properties": {
            "value": {"type": ["string", "null"]},
            "status": {
                "type": "string",
                "enum": ["detected", "missing", "unclear"],
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
            },
            "evidence_ids": {
                "type": "array",
                "items": {"type": "integer"},
            },
            "reason": {"type": "string"},
        },
        "required": [
            "value",
            "status",
            "confidence",
            "evidence_ids",
            "reason",
        ],
        "additionalProperties": False,
    }

    return {
        "type": "object",
        "properties": {
            "fields": {
                "type": "object",
                "properties": {
                    field: field_schema for field in FIELDS
                },
                "required": FIELDS,
                "additionalProperties": False,
            }
        },
        "required": ["fields"],
        "additionalProperties": False,
    }


def build_prompt(
    ocr_results: Iterable[Dict[str, Any]],
) -> str:
    evidence = _normalise_ocr(ocr_results)

    evidence_lines = []
    for item in evidence:
        evidence_lines.append(
            f'{item["id"]}. "{item["text"]}" '
            f'(OCR confidence={item["confidence"]:.3f}; '
            f'source={item["source"]})'
        )

    evidence_text = "\n".join(evidence_lines) or "(no OCR evidence)"

    return f"""
You are LMSCAN's semantic package-label extraction model.

Inspect the supplied package image(s) together with the OCR evidence.

YOUR JOB
Extract package declarations. Do NOT determine legal compliance.

EVIDENCE RULES
1. Use the visible package image and supplied OCR evidence.
2. Never invent, guess, or fill a missing declaration from world knowledge.
3. If image and OCR disagree, prefer clear visual evidence, but mark "unclear"
   when the conflict cannot be resolved confidently.
4. OCR spelling errors may be normalized when the intended text is visually
   unambiguous.
5. "missing" means no reliable evidence was found. It does not mean legally
   mandatory.
6. "unclear" means some evidence exists but it is weak, partial, or conflicting.
7. A detected or unclear value MUST cite one or more OCR evidence_ids when
   relevant OCR evidence exists.
8. Do not infer vegetarian/non-vegetarian from the product name.
9. Do not infer country of origin from a manufacturer's address.
10. Do not infer ingredients from the product name.
11. Do not treat any 14-digit number as an FSSAI licence unless the image/OCR
    context supports that association.
12. Preserve exact meaning of prices, quantities, batch codes and dates.
13. For date fields, visually distinguish APR/OCT and similar months carefully.
14. For manufacturer fields, separate company name from its address.
15. Return JSON only according to the supplied schema.

16. Manufacturer address is IMPORTANT. Inspect the text directly below or
    beside "PACKED & MARKETED BY", "MARKETED BY", "MANUFACTURED BY",
    "PACKED BY", or similar manufacturer labels. If address lines visibly
    contain locality words (e.g. sector, phase, industrial area) or a
    six-digit Indian PIN code, treat them as strong address evidence.
17. Do not require the word "address" to appear. Packaging often prints the
    address as multiple lines without an "Address:" label.
18. When manufacturer name and address are split over multiple OCR lines,
    combine the lines into one address value in normal reading order.

FIELDS
- product_name
- ingredients
- nutrition
- veg_nonveg
- fssai_license_number
- mrp
- net_quantity
- batch_number
- manufacturing_date
- expiry_date
- best_before
- manufacturer
- manufacturer_address
- consumer_care
- country_of_origin
- allergen_declaration
- storage_instructions
- directions_for_use

OCR EVIDENCE
----------------
{evidence_text}
----------------
""".strip()


def _image_data_url(
    image: Union[bytes, bytearray, memoryview, str, os.PathLike],
) -> str:
    """
    Normalize the input image through Pillow before base64 encoding.

    Some valid local JPEG files can be rejected by remote vision providers
    because of unusual JPEG metadata/encoding. Re-saving as a standard RGB
    JPEG gives the provider a clean, predictable image payload.
    """
    try:
        from io import BytesIO
        from PIL import Image

        if isinstance(image, (str, os.PathLike)):
            with open(image, "rb") as handle:
                raw = handle.read()
        else:
            raw = bytes(image)

        with Image.open(BytesIO(raw)) as source:
            source = source.convert("RGB")

            # Re-encode using a standard JPEG stream.
            buffer = BytesIO()
            source.save(
                buffer,
                format="JPEG",
                quality=92,
                optimize=True,
                progressive=False,
            )
            data = buffer.getvalue()

        encoded = base64.b64encode(data).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"

    except Exception as exc:
        raise RuntimeError(f"Could not normalize image for vision API: {exc}") from exc


def _validate(
    payload: Dict[str, Any],
    ocr_results: List[Dict[str, Any]],
    model: str,
) -> Dict[str, Any]:
    result = empty_semantic_result(model=model)
    result["raw_response"] = payload

    by_id = {item["id"]: item for item in ocr_results}
    fields = payload.get("fields", {})

    if not isinstance(fields, dict):
        result["errors"].append(
            "OpenRouter response did not contain a valid fields object."
        )
        return result

    for field in FIELDS:
        raw = fields.get(field, {})
        if not isinstance(raw, dict):
            continue

        status = str(raw.get("status", "missing")).lower()
        if status not in {"detected", "missing", "unclear"}:
            status = "unclear"

        value = raw.get("value")
        if value is not None:
            value = str(value).strip() or None

        ids = raw.get("evidence_ids", [])
        if not isinstance(ids, list):
            ids = []

        valid_ids = []
        for evidence_id in ids:
            try:
                evidence_id = int(evidence_id)
            except (TypeError, ValueError):
                continue
            if evidence_id in by_id and evidence_id not in valid_ids:
                valid_ids.append(evidence_id)

        if status == "detected" and (not value or not valid_ids):
            status = "unclear" if value else "missing"

        if status == "missing":
            value = None
            valid_ids = []

        evidence = [by_id[i]["text"] for i in valid_ids]

        try:
            confidence = float(raw.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0

        result["fields"][field] = {
            "value": value,
            "status": status,
            "confidence": max(0.0, min(1.0, confidence)),
            "evidence_ids": valid_ids,
            "evidence": evidence,
            "reason": str(raw.get("reason", "")).strip(),
            "source": "openrouter",
        }

    return result


def semantic_extract(
    ocr_results: Iterable[Dict[str, Any]],
    images: Optional[Iterable[Union[bytes, bytearray, memoryview, str]]] = None,
    *,
    model: str = DEFAULT_MODEL,
    timeout: int = 90,
) -> Dict[str, Any]:
    """
    Run OpenRouter vision + OCR semantic extraction.

    `images` may contain raw image bytes or file paths.
    """
    result = empty_semantic_result(model=model)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        result["errors"].append("OPENROUTER_API_KEY is not set.")
        return result

    cleaned_ocr = _normalise_ocr(ocr_results)
    prompt = build_prompt(cleaned_ocr)

    content: List[Dict[str, Any]] = [
        {
            "type": "text",
            "text": prompt,
        }
    ]

    for image in images or []:
        try:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": _image_data_url(image),
                    },
                }
            )
        except Exception as exc:
            result["errors"].append(f"Could not encode image: {exc}")

    if len(content) == 1:
        result["errors"].append("No package image was supplied.")
        return result

    try:
        import requests

        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://openrouter.ai/",
                "X-Title": "LMSCAN SIH Package Compliance",
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
                "temperature": 0,
                "max_tokens": 3000,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "lmscan_package_extraction",
                        "strict": True,
                        "schema": _schema(),
                    },
                },
            },
            timeout=timeout,
        )

        if response.status_code >= 400:
            body = response.text[:4000]
            result["errors"].append(
                f"OpenRouter HTTP {response.status_code}: {body}"
            )
            return result

        try:
            data = response.json()
        except ValueError:
            result["errors"].append(
                "OpenRouter returned non-JSON HTTP response: "
                + response.text[:2000]
            )
            return result
    except Exception as exc:
        result["errors"].append(
            f"OpenRouter request failed: {type(exc).__name__}: {exc}"
        )
        return result

    if isinstance(data, dict) and data.get("error"):
        result["errors"].append(
            "OpenRouter model error: " + json.dumps(
                data.get("error"), ensure_ascii=False
            )
        )
        result["raw_response"] = data
        return result

    try:
        message = data["choices"][0]["message"]
        raw_content = message.get("content", "")

        if not raw_content:
            result["errors"].append(
                "OpenRouter returned an empty model message."
            )
            result["raw_response"] = data
            return result

        payload = json.loads(raw_content)
    except Exception as exc:
        result["errors"].append(
            f"Could not parse OpenRouter structured output: {type(exc).__name__}: {exc}"
        )
        result["raw_response"] = data
        return result

    return _validate(payload, cleaned_ocr, model=model)


def merge_with_deterministic(
    deterministic: Dict[str, Any],
    ai_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    AI fills empty fields but does not overwrite deterministic values.

    A future evidence-fusion stage can selectively replace a deterministic
    value only when visual evidence is stronger and auditable.
    """
    merged = dict(deterministic or {})
    ai_fields = ai_result.get("fields", {})

    for field in FIELDS:
        ai_field = ai_fields.get(field, {})
        if ai_field.get("status") != "detected":
            continue

        ai_value = ai_field.get("value")
        if ai_value and not merged.get(field):
            merged[field] = ai_value

    merged["ai_semantics"] = ai_fields
    merged["ai_model"] = ai_result.get("model", DEFAULT_MODEL)
    merged["ai_provider"] = "openrouter"
    merged["ai_errors"] = ai_result.get("errors", [])

    return merged


run_ai_extraction = semantic_extract

__all__ = [
    "FIELDS",
    "DEFAULT_MODEL",
    "empty_semantic_result",
    "build_prompt",
    "semantic_extract",
    "merge_with_deterministic",
    "run_ai_extraction",
]
