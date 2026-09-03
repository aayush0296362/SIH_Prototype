import streamlit as st
import easyocr


@st.cache_resource
def get_ocr_reader():

    return easyocr.Reader(
        ["en"],
        gpu=False
    )


def extract_text(image):

    reader = get_ocr_reader()

    results = reader.readtext(
        image,
        detail=1
    )

    cleaned_results = []

    for bbox, text, confidence in results:

        if confidence >= 0.25:

            cleaned_results.append({
                "text": text,
                "confidence": float(confidence),
                "bbox": bbox
            })

    return cleaned_results