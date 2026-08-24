import re


def clean_text(text):
    if not text:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(text)
    ).strip()


def extract_declarations(ocr_results):

    # -----------------------------------------
    # 1. Get readable text from OCR
    # -----------------------------------------

    texts = []

    for result in ocr_results:

        if isinstance(result, dict):

            text = result.get("text", "")
            confidence = float(
                result.get("confidence", 0)
            )

        elif isinstance(result, (list, tuple)):

            if len(result) >= 3:
                text = result[1]
                confidence = float(result[2])
            else:
                continue

        else:
            continue

        text = clean_text(text)

        if text and confidence >= 0.25:
            texts.append(text)

    # -----------------------------------------
    # 2. Create result
    # -----------------------------------------

    declarations = {
        "product_name": None,
        "mrp": None,
        "net_quantity": None,
        "manufacturer": None,
        "manufacturing_date": None,
        "expiry_date": None,
        "best_before": None,
        "consumer_care": None,
        "country_of_origin": None,
        "batch_number": None,
        "raw_text": texts
    }
   
    # -----------------------------------------
    # 3. Product name
    # -----------------------------------------

    for text in texts:

        if "doritos" in text.lower():

            declarations["product_name"] = text
            break

        if "kurkure" in text.lower():

            declarations["product_name"] = text
            break

        if "lays" in text.lower():

            declarations["product_name"] = text
            break

        if "bingo" in text.lower():

            declarations["product_name"] = text
            break

    # -----------------------------------------
    # 4. Consumer care / email
    # -----------------------------------------

    email = re.search(
        r"[\w\.-]+@[\w\.-]+\.\w+",
        " ".join(texts),
        re.IGNORECASE
    )

    if email:

        declarations["consumer_care"] = (
            email.group(0)
        )

    # -----------------------------------------
    # 5. MRP
    # -----------------------------------------

    full_text = " ".join(texts)

    mrp = re.search(
        r"(?:MRP|M\.R\.P)"
        r"\s*[:\-]?\s*"
        r"(?:₹|Rs\.?|INR)?"
        r"\s*(\d+(?:\.\d{1,2})?)",
        full_text,
        re.IGNORECASE
    )

    if mrp:

        declarations["mrp"] = (
            "₹" + mrp.group(1)
        )

    # -----------------------------------------
    # 6. Net quantity
    # -----------------------------------------

    quantity = re.search(
        r"(?:NET\s*(?:WEIGHT|WT|QTY|QUANTITY)?)"
        r"\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)"
        r"\s*(kg|kgs|g|gm|gms|grams?|ml|l|ltr)",
        full_text,
        re.IGNORECASE
    )

    if quantity:

        declarations["net_quantity"] = (
            quantity.group(1)
            + " "
            + quantity.group(2)
        )

    # -----------------------------------------
    # 7. Manufacturer
    # -----------------------------------------

    manufacturer = re.search(
        r"(?:MANUFACTURED\s+BY|"
        r"MANUFACTURER|"
        r"PACKED\s+BY)"
        r"\s*[:\-]?\s*"
        r"(.{3,150})",
        full_text,
        re.IGNORECASE
    )

    if manufacturer:

        declarations["manufacturer"] = clean_text(
            manufacturer.group(1)
        )

    # -----------------------------------------
    # 8. Batch / Lot
    # -----------------------------------------

    batch = re.search(
        r"(?:BATCH|LOT)"
        r"\s*(?:NO\.?)?"
        r"\s*[:\-]?\s*"
        r"([A-Z0-9\/\-]{3,30})",
        full_text,
        re.IGNORECASE
    )

    if batch:

        declarations["batch_number"] = (
            batch.group(1)
        )

    # -----------------------------------------
    # 9. Dates
    # -----------------------------------------

    dates = re.findall(
        r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b",
        full_text
    )

    if len(dates) >= 1:

        declarations["manufacturing_date"] = (
            dates[0]
        )

    if len(dates) >= 2:

        declarations["expiry_date"] = (
            dates[1]
        )

    # -----------------------------------------
    # RETURN
    # -----------------------------------------

    return declarations