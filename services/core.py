"""
LMSCAN Core Inspection Pipeline

Single shared pipeline for:
    Consumer Portal
    Inspector Portal
    Future batch/offline validation

Flow:
    Images
      -> EasyOCR
      -> deterministic extraction
      -> OpenRouter semantic extraction
      -> evidence fusion
      -> context-aware compliance
      -> one reusable inspection result

This module does not render UI.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Iterable, List, Union

from PIL import Image

from services.ocr import extract_text
from services.extraction import extract_declarations
from services.ai_extraction import semantic_extract
from services.evidence_fusion import fuse_results, apply_fusion_to_legacy_result
from services.compliance import check_compliance


ImageInput = Union[
    str,
    Path,
    bytes,
    bytearray,
    memoryview,
    Any,  # Streamlit UploadedFile / camera object
]


def _load_pil_image(image: ImageInput) -> Image.Image:
    """Load an input into a detached RGB PIL image."""
    if isinstance(image, Image.Image):
        return image.convert("RGB").copy()

    if isinstance(image, (str, Path)):
        with Image.open(image) as img:
            return img.convert("RGB").copy()

    if isinstance(image, (bytes, bytearray, memoryview)):
        with Image.open(BytesIO(bytes(image))) as img:
            return img.convert("RGB").copy()

    # Streamlit UploadedFile / camera input commonly exposes getvalue().
    getvalue = getattr(image, "getvalue", None)
    if callable(getvalue):
        raw = getvalue()
        with Image.open(BytesIO(raw)) as img:
            return img.convert("RGB").copy()

    # Last-resort file-like object.
    read = getattr(image, "read", None)
    if callable(read):
        raw = read()
        with Image.open(BytesIO(raw)) as img:
            return img.convert("RGB").copy()

    raise TypeError(
        "Unsupported image input. Use a file path, image bytes, PIL Image, "
        "or an object exposing getvalue()."
    )


def analyze_package(
    images: Iterable[ImageInput],
    *,
    use_ai: bool = True,
    ai_model: str | None = None,
    ai_timeout: int = 90,
) -> Dict[str, Any]:
    """
    Run the complete LMSCAN inspection pipeline.

    Parameters
    ----------
    images:
        One or more package images.
    use_ai:
        If False, run OCR + deterministic extraction + compliance only.
        This provides a safe fallback when the AI provider is unavailable.
    ai_model:
        Optional OpenRouter model override.
    ai_timeout:
        OpenRouter request timeout in seconds.
    """
    image_inputs = list(images or [])

    if not image_inputs:
        return {
            "status": "error",
            "errors": ["No package images were supplied."],
            "ocr_results": [],
            "declarations": {},
            "ai": None,
            "fusion": None,
            "compliance": None,
        }

    pil_images: List[Image.Image] = []
    errors: List[str] = []

    for index, image_input in enumerate(image_inputs, start=1):
        try:
            pil_images.append(_load_pil_image(image_input))
        except Exception as exc:
            errors.append(
                f"Image {index} could not be loaded: {type(exc).__name__}: {exc}"
            )

    if not pil_images:
        return {
            "status": "error",
            "errors": errors or ["No readable package images were supplied."],
            "ocr_results": [],
            "declarations": {},
            "ai": None,
            "fusion": None,
            "compliance": None,
        }

    # ------------------------------------------------------------
    # 1. OCR
    # ------------------------------------------------------------
    ocr_results: List[Dict[str, Any]] = []

    for image in pil_images:
        try:
            ocr_results.extend(extract_text(image))
        except Exception as exc:
            errors.append(
                f"OCR failed for one image: {type(exc).__name__}: {exc}"
            )

    # ------------------------------------------------------------
    # 2. Deterministic extraction
    # ------------------------------------------------------------
    try:
        deterministic = extract_declarations(ocr_results)
    except Exception as exc:
        errors.append(
            f"Deterministic extraction failed: {type(exc).__name__}: {exc}"
        )
        deterministic = {
            "raw_text": [item.get("text", "") for item in ocr_results]
        }

    # ------------------------------------------------------------
    # 3. OpenRouter semantic extraction
    # ------------------------------------------------------------
    ai_result: Dict[str, Any] | None = None

    if use_ai and ocr_results and pil_images:
        # OpenRouter module accepts paths/bytes. Convert PIL images to JPEG
        # bytes here so this works uniformly for uploaded/camera images.
        image_bytes: List[bytes] = []

        for image in pil_images:
            buffer = BytesIO()
            image.save(
                buffer,
                format="JPEG",
                quality=92,
                optimize=True,
                progressive=False,
            )
            image_bytes.append(buffer.getvalue())

        try:
            kwargs: Dict[str, Any] = {
                "images": image_bytes,
                "timeout": ai_timeout,
            }
            if ai_model:
                kwargs["model"] = ai_model

            ai_result = semantic_extract(
                ocr_results,
                **kwargs,
            )
        except Exception as exc:
            errors.append(
                f"AI semantic extraction failed: {type(exc).__name__}: {exc}"
            )
            ai_result = {
                "provider": "openrouter",
                "model": ai_model,
                "fields": {},
                "errors": [str(exc)],
            }

    # ------------------------------------------------------------
    # 4. Evidence fusion
    # ------------------------------------------------------------
    try:
        fusion = fuse_results(deterministic, ai_result or {})
        fused_declarations = apply_fusion_to_legacy_result(
            deterministic,
            fusion,
        )
    except Exception as exc:
        errors.append(
            f"Evidence fusion failed: {type(exc).__name__}: {exc}"
        )
        fusion = None
        fused_declarations = deterministic

    # ------------------------------------------------------------
    # 5. Compliance
    # ------------------------------------------------------------
    try:
        compliance = check_compliance(fused_declarations)
    except Exception as exc:
        errors.append(
            f"Compliance engine failed: {type(exc).__name__}: {exc}"
        )
        compliance = {
            "status": "review",
            "findings": [],
            "missing_fields": [],
            "total_fields": 0,
            "detected_fields": 0,
        }

    return {
        "status": "ok" if pil_images else "error",
        "errors": errors,
        "images_processed": len(pil_images),
        "ocr_results": ocr_results,
        "declarations": fused_declarations,
        "deterministic": deterministic,
        "ai": ai_result,
        "fusion": fusion,
        "compliance": compliance,
    }


def analyze_images(
    images: Iterable[ImageInput],
    **kwargs: Any,
) -> Dict[str, Any]:
    """Alias for app/inspector code."""
    return analyze_package(images, **kwargs)


__all__ = [
    "analyze_package",
    "analyze_images",
]
