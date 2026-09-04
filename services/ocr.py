import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image


# ============================================================
# LMSCAN OCR ENGINE V11
# ============================================================
# Main improvements over the previous OCR layer:
#
# 1. Every OCR bounding box is converted back to ORIGINAL image
#    coordinates. This is critical because upscaled variants otherwise
#    have a different coordinate system.
#
# 2. We DO NOT throw away a useful OCR candidate just because another
#    preprocessing pass detected similar text. All meaningful variants
#    are retained for the extraction/evidence-fusion layer.
#
# 3. Duplicate suppression is geometry-aware and variant-aware.
#
# 4. Text boxes from different OCR passes are clustered spatially.
#    A cluster can contain:
#        BLACK
#        BLACK MASOOR
#        MASOCR
#    instead of arbitrarily keeping only one.
#
# 5. EasyOCR receives more suitable preprocessing variants:
#        original
#        2x upscaled
#        contrast enhanced
#        sharpened
#        adaptive threshold
#        OTSU
#
# 6. We preserve:
#        text
#        confidence
#        bbox
#        source
#        center
#        original-size geometry
#
# 7. OCR evidence is sorted in original-image coordinates.
#
# This remains compatible with:
#        from services.ocr import extract_text
# ============================================================


# ============================================================
# OCR READER
# ============================================================

@st.cache_resource
def get_ocr_reader():

    return easyocr.Reader(
        ["en"],
        gpu=False
    )


# ============================================================
# IMAGE CONVERSION
# ============================================================

def image_to_numpy(image):

    if isinstance(image, Image.Image):

        image = image.convert("RGB")

        return np.array(image)

    image = np.asarray(image)

    if image.ndim == 2:
        image = cv2.cvtColor(
            image,
            cv2.COLOR_GRAY2RGB
        )

    return image


# ============================================================
# PREPROCESSING
# ============================================================

def create_variants(image):

    img = image_to_numpy(image)

    # Ensure uint8.
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)

    # Prevent very large phone/WhatsApp images from making CPU OCR
    # excessively slow.
    max_dim = 1800
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(
            img,
            (max(1, int(w * scale)), max(1, int(h * scale))),
            interpolation=cv2.INTER_AREA,
        )

    original_h, original_w = img.shape[:2]

    # --------------------------------------------------------
    # Original
    # --------------------------------------------------------

    original = img.copy()

    # --------------------------------------------------------
    # 2x upscale
    # --------------------------------------------------------

    upscaled = cv2.resize(
        img,
        None,
        fx=2.0,
        fy=2.0,
        interpolation=cv2.INTER_CUBIC
    )

    # --------------------------------------------------------
    # Grayscale
    # --------------------------------------------------------

    gray = cv2.cvtColor(
        upscaled,
        cv2.COLOR_RGB2GRAY
    )

    # --------------------------------------------------------
    # CLAHE
    # --------------------------------------------------------

    clahe = cv2.createCLAHE(
        clipLimit=2.5,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # --------------------------------------------------------
    # Mild denoising
    # --------------------------------------------------------
    # Keep this mild. Aggressive denoising can destroy small letters
    # on transparent/reflective packaging.

    denoised = cv2.fastNlMeansDenoising(
        enhanced,
        None,
        7,
        7,
        21
    )

    # --------------------------------------------------------
    # Sharpen
    # --------------------------------------------------------

    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ], dtype=np.float32)

    sharpened = cv2.filter2D(
        denoised,
        -1,
        kernel
    )

    # --------------------------------------------------------
    # Adaptive threshold
    # --------------------------------------------------------

    threshold = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    # --------------------------------------------------------
    # OTSU
    # --------------------------------------------------------

    _, otsu = cv2.threshold(
        denoised,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # FAST MODE:
    # Keep only the two most useful passes. This preserves the V11
    # evidence/bbox architecture without running EasyOCR six times.
    return [
        {
            "name": "original",
            "image": original,
            "scale_x": 1.0,
            "scale_y": 1.0,
        },
        {
            "name": "enhanced",
            "image": enhanced,
            "scale_x": 2.0,
            "scale_y": 2.0,
        },
    ]


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_ocr_text(text):

    if not text:
        return ""

    text = str(text)

    # Normalize common OCR whitespace without destroying punctuation.
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")

    text = " ".join(
        text.split()
    )

    return text.strip()


# ============================================================
# BBOX UTILITIES
# ============================================================

def normalize_bbox_to_original(
    bbox,
    scale_x,
    scale_y
):
    """
    EasyOCR returns coordinates in the coordinates of the image passed
    to it. Upscaled images therefore have 2x coordinates.

    Convert all coordinates back to the original uploaded-image space.
    """

    if bbox is None:
        return []

    normalized = []

    try:
        for point in bbox[:4]:

            x = float(point[0]) / float(scale_x)
            y = float(point[1]) / float(scale_y)

            normalized.append(
                [x, y]
            )

        return normalized

    except Exception:
        return []


def get_center(bbox):

    try:

        xs = [
            float(point[0])
            for point in bbox[:4]
        ]

        ys = [
            float(point[1])
            for point in bbox[:4]
        ]

        if not xs or not ys:
            raise ValueError

        return (
            sum(xs) / len(xs),
            sum(ys) / len(ys)
        )

    except Exception:

        return (
            0.0,
            0.0
        )


def bbox_dimensions(bbox):

    try:

        xs = [
            float(point[0])
            for point in bbox[:4]
        ]

        ys = [
            float(point[1])
            for point in bbox[:4]
        ]

        return (
            max(xs) - min(xs),
            max(ys) - min(ys)
        )

    except Exception:

        return (
            0.0,
            0.0
        )


def bbox_iou(a, b):

    try:

        ax1 = min(float(p[0]) for p in a[:4])
        ay1 = min(float(p[1]) for p in a[:4])
        ax2 = max(float(p[0]) for p in a[:4])
        ay2 = max(float(p[1]) for p in a[:4])

        bx1 = min(float(p[0]) for p in b[:4])
        by1 = min(float(p[1]) for p in b[:4])
        bx2 = max(float(p[0]) for p in b[:4])
        by2 = max(float(p[1]) for p in b[:4])

        ix1 = max(ax1, bx1)
        iy1 = max(ay1, by1)
        ix2 = min(ax2, bx2)
        iy2 = min(ay2, by2)

        iw = max(0.0, ix2 - ix1)
        ih = max(0.0, iy2 - iy1)

        intersection = iw * ih

        area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
        area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)

        union = area_a + area_b - intersection

        if union <= 0:
            return 0.0

        return intersection / union

    except Exception:

        return 0.0


def center_distance(a, b):

    ax, ay = get_center(a)
    bx, by = get_center(b)

    return float(
        np.hypot(
            ax - bx,
            ay - by
        )
    )


# ============================================================
# TEXT SIMILARITY
# ============================================================

def normalized_alnum(text):

    return "".join(
        ch.lower()
        for ch in normalize_ocr_text(text)
        if ch.isalnum()
    )


def text_similarity(a, b):

    aa = normalized_alnum(a)
    bb = normalized_alnum(b)

    if not aa or not bb:
        return 0.0

    # Exact normalized match.
    if aa == bb:
        return 1.0

    # Substring relation is important for:
    # "BLACK" vs "BLACK MASOOR"
    if aa in bb or bb in aa:
        shorter = min(len(aa), len(bb))
        longer = max(len(aa), len(bb))

        return 0.75 + 0.25 * (
            shorter / max(1, longer)
        )

    from difflib import SequenceMatcher

    return SequenceMatcher(
        None,
        aa,
        bb
    ).ratio()


# ============================================================
# OCR QUALITY
# ============================================================

def is_useful_ocr_text(text):

    text = normalize_ocr_text(text)

    if not text:
        return False

    # Reject obvious single-symbol garbage.
    alnum = sum(
        ch.isalnum()
        for ch in text
    )

    if alnum == 0:
        return False

    if len(text) > 180:
        return False

    return True


def adjusted_confidence(
    confidence,
    text,
    source_name
):
    """
    Confidence is kept as OCR confidence, but we also calculate a
    conservative quality-adjusted confidence for ranking.

    Thresholding is deliberately NOT aggressive because low-confidence
    candidates can contain the correct word that a high-confidence pass
    missed.
    """

    score = float(
        np.clip(
            confidence,
            0.0,
            1.0
        )
    )

    text = normalize_ocr_text(text)

    # Very short alphabetic fragments are less useful.
    if len(text) <= 2 and text.isalpha():
        score *= 0.85

    # Preserve potentially important short numeric values.
    if any(ch.isdigit() for ch in text):
        score *= 1.02

    # Original image is generally a strong baseline.
    if source_name == "original":
        score *= 1.03

    return float(
        np.clip(
            score,
            0.0,
            1.0
        )
    )


# ============================================================
# SINGLE OCR PASS
# ============================================================

def run_ocr(
    reader,
    image,
    source_name,
    scale_x=1.0,
    scale_y=1.0
):

    try:

        results = reader.readtext(
            image,
            detail=1,
            paragraph=False,
            width_ths=0.65,
            height_ths=0.65,
            mag_ratio=1.0
        )

    except Exception as error:

        print(
            f"OCR error in {source_name}: {error}"
        )

        return []

    output = []

    for result in results:

        if len(result) < 3:
            continue

        raw_bbox = result[0]

        text = normalize_ocr_text(
            result[1]
        )

        try:
            confidence = float(
                result[2]
            )
        except Exception:
            confidence = 0.0

        # Keep useful candidates down to 0.15.
        # The extraction layer decides which evidence is trustworthy.
        if confidence < 0.15:
            continue

        if not is_useful_ocr_text(text):
            continue

        bbox = normalize_bbox_to_original(
            raw_bbox,
            scale_x,
            scale_y
        )

        if not bbox:
            continue

        center = get_center(
            bbox
        )

        output.append({

            "text": text,

            "confidence": confidence,

            "adjusted_confidence":
                adjusted_confidence(
                    confidence,
                    text,
                    source_name
                ),

            "bbox": bbox,

            "center": center,

            "source": source_name

        })

    return output


# ============================================================
# GEOMETRY-AWARE DUPLICATE CHECK
# ============================================================

def is_spatial_duplicate(
    result,
    existing
):
    """
    Only considers two detections duplicates when:
    - their text is substantially similar
    - their original-image boxes overlap OR centers are close
    - their dimensions are reasonably compatible
    """

    text = result["text"]
    bbox = result["bbox"]

    rw, rh = bbox_dimensions(bbox)

    for old in existing:

        old_text = old["text"]
        old_bbox = old["bbox"]

        similarity = text_similarity(
            text,
            old_text
        )

        if similarity < 0.72:
            continue

        iou = bbox_iou(
            bbox,
            old_bbox
        )

        distance = center_distance(
            bbox,
            old_bbox
        )

        ow, oh = bbox_dimensions(
            old_bbox
        )

        scale = max(
            10.0,
            rh,
            oh,
            rw * 0.08,
            ow * 0.08
        )

        # Same region if boxes overlap meaningfully.
        if iou >= 0.20:
            return True

        # Or if the centers are close relative to text height.
        if distance <= max(
            18.0,
            scale * 1.8
        ):
            return True

    return False


# ============================================================
# MERGE OCR RESULTS
# ============================================================

def merge_results(all_results):

    """
    IMPORTANT CHANGE:

    The previous implementation sorted by confidence and deleted the
    lower-confidence version.

    That can destroy useful evidence:

        BLACK MASOOR
        BLACK

    or:

        Wegha International
        Megha International

    V11 instead keeps both when their text carries different information.

    Exact duplicates are collapsed, while meaningful alternative readings
    are retained for extraction-layer evidence fusion.
    """

    if not all_results:
        return []

    # Highest adjusted confidence first.
    ordered = sorted(
        all_results,
        key=lambda x: (
            x.get(
                "adjusted_confidence",
                x.get("confidence", 0.0)
            ),
            len(x.get("text", "")),
        ),
        reverse=True
    )

    merged = []

    for result in ordered:

        text = normalize_ocr_text(
            result.get("text", "")
        )

        if not text:
            continue

        result = dict(result)
        result["text"] = text

        # Exact-ish duplicate.
        duplicate = False

        for old in merged:

            similarity = text_similarity(
                text,
                old["text"]
            )

            if similarity < 0.90:
                continue

            iou = bbox_iou(
                result["bbox"],
                old["bbox"]
            )

            distance = center_distance(
                result["bbox"],
                old["bbox"]
            )

            if (
                iou >= 0.35
                or distance <= 15.0
            ):
                duplicate = True
                break

        if duplicate:
            continue

        merged.append(
            result
        )

    # Keep meaningful candidates but cap extreme duplicate explosions.
    # A text can occur in many preprocessing passes; retaining a few
    # independent observations is enough for evidence fusion.
    grouped = []

    for item in merged:

        placed = False

        for group in grouped:

            representative = group[0]

            similarity = text_similarity(
                item["text"],
                representative["text"]
            )

            if similarity < 0.72:
                continue

            if center_distance(
                item["bbox"],
                representative["bbox"]
            ) <= 35.0:

                if len(group) < 6:
                    group.append(item)

                placed = True
                break

        if not placed:
            grouped.append(
                [item]
            )

    final_results = []

    for group in grouped:

        # Add all distinct readings from the group.
        # Extraction needs to see alternative OCR readings.
        group.sort(
            key=lambda x: (
                x.get(
                    "adjusted_confidence",
                    x.get("confidence", 0.0)
                ),
                len(x["text"])
            ),
            reverse=True
        )

        for item in group[:6]:

            final_results.append({

                "text":
                    item["text"],

                "confidence":
                    item["confidence"],

                "adjusted_confidence":
                    item.get(
                        "adjusted_confidence",
                        item["confidence"]
                    ),

                "bbox":
                    item["bbox"],

                "source":
                    item["source"]

            })

    return final_results


# ============================================================
# READING ORDER
# ============================================================

def sort_reading_order(results):

    if not results:
        return []

    # Estimate typical text-line height.
    heights = []

    for item in results:

        _, h = bbox_dimensions(
            item["bbox"]
        )

        if h > 0:
            heights.append(h)

    median_height = (
        float(np.median(heights))
        if heights
        else 20.0
    )

    # Tolerance grows slightly with font size.
    row_tolerance = max(
        12.0,
        median_height * 0.65
    )

    def key(item):

        x, y = get_center(
            item["bbox"]
        )

        # Quantize Y into approximate visual rows.
        row = round(
            y / row_tolerance
        )

        return (
            row,
            y,
            x
        )

    return sorted(
        results,
        key=key
    )


# ============================================================
# OPTIONAL DEBUG CLUSTERS
# ============================================================

def build_ocr_clusters(results):

    """
    Returns spatial OCR groups for debugging / future UI.
    It does NOT replace the raw OCR evidence.
    """

    clusters = []

    for item in results:

        placed = False

        for cluster in clusters:

            representative = cluster[0]

            if (
                text_similarity(
                    item["text"],
                    representative["text"]
                ) >= 0.55
                and center_distance(
                    item["bbox"],
                    representative["bbox"]
                ) <= 60
            ):
                cluster.append(item)
                placed = True
                break

        if not placed:

            clusters.append(
                [item]
            )

    return clusters


# ============================================================
# MAIN OCR
# ============================================================

def extract_text(image):

    reader = get_ocr_reader()

    variants = create_variants(
        image
    )

    all_results = []

    # --------------------------------------------------------
    # Run all preprocessing variants.
    # --------------------------------------------------------

    for variant in variants:

        results = run_ocr(
            reader,
            variant["image"],
            variant["name"],
            variant["scale_x"],
            variant["scale_y"]
        )

        all_results.extend(
            results
        )

    # --------------------------------------------------------
    # Merge exact duplicates while retaining meaningful
    # alternative readings.
    # --------------------------------------------------------

    final_results = merge_results(
        all_results
    )

    # --------------------------------------------------------
    # Reading order.
    # --------------------------------------------------------

    final_results = sort_reading_order(
        final_results
    )

    return final_results


# ============================================================
# OPTIONAL BACKWARD-COMPATIBILITY ALIASES
# ============================================================

def ocr_image(image):
    return extract_text(image)


def perform_ocr(image):
    return extract_text(image)
