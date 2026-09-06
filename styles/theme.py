import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>

        /* ================================
           LMSCAN - PROFESSIONAL THEME
           Sky Blue + White
        ================================= */

        .stApp {
            background: #ffffff;
            color: #0f172a;
        }

        .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            color: #0f172a !important;
            font-weight: 700;
        }

        h1 {
            letter-spacing: -0.5px;
        }

        p, span, label {
            color: #334155;
        }

        /* Normal Streamlit buttons */
        .stButton > button {
            background: #38bdf8 !important;
            color: #ffffff !important;
            border: 1px solid #38bdf8 !important;
            border-radius: 10px !important;
            padding: 0.55rem 1.2rem;
            font-weight: 600;
            transition: 0.2s ease;
        }

        .stButton > button:hover {
            background: #0ea5e9 !important;
            color: #ffffff !important;
            border-color: #0ea5e9 !important;
        }

        /* Secondary buttons, including Back to Home */
        [data-testid="stBaseButton-secondary"] {
            background: #ffffff !important;
            color: #0369a1 !important;
            border: 1px solid #7dd3fc !important;
            border-radius: 9px !important;
            font-weight: 700 !important;
        }

        [data-testid="stBaseButton-secondary"]:hover {
            background: #f0f9ff !important;
            color: #0284c7 !important;
            border-color: #38bdf8 !important;
        }

        /* Camera widget */
        [data-testid="stCameraInput"] {
            background: #f0f9ff !important;
            border: 1px solid #bae6fd !important;
            border-radius: 12px !important;
            padding: 6px !important;
            overflow: hidden !important;
        }

        [data-testid="stCameraInput"] > div {
            border-radius: 10px !important;
        }

        /* Actual camera capture button */
        [data-testid="stCameraInput"] button,
        [data-testid="stCameraInput"] [data-testid="stBaseButton-secondary"],
        [data-testid="stCameraInput"] [data-testid="stBaseButton-primary"] {
            background: #38bdf8 !important;
            color: #ffffff !important;
            border: 1px solid #38bdf8 !important;
            border-radius: 9px !important;
            min-height: 38px !important;
            font-weight: 700 !important;
            opacity: 1 !important;
            box-shadow: none !important;
        }

        [data-testid="stCameraInput"] button:hover,
        [data-testid="stCameraInput"] [data-testid="stBaseButton-secondary"]:hover,
        [data-testid="stCameraInput"] [data-testid="stBaseButton-primary"]:hover {
            background: #0ea5e9 !important;
            color: #ffffff !important;
            border-color: #0ea5e9 !important;
        }

        /* Camera action row */
        [data-testid="stCameraInput"] [data-testid="stHorizontalBlock"] {
            background: transparent !important;
        }

        /* File uploader */
        [data-testid="stFileUploader"] {
            background: #f0f9ff !important;
            border: 1px solid #bae6fd !important;
            border-radius: 12px !important;
            padding: 0.5rem !important;
        }

        [data-testid="stFileUploader"] section {
            background: #f0f9ff !important;
            border-radius: 10px !important;
        }

        [data-testid="stFileUploader"] button {
            background: #ffffff !important;
            color: #0369a1 !important;
            border: 1px solid #7dd3fc !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
        }

        [data-testid="stFileUploader"] button:hover {
            background: #f0f9ff !important;
            color: #0284c7 !important;
            border-color: #38bdf8 !important;
        }

        [data-testid="stExpander"] {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
        }

        [data-testid="stAlert"] {
            border-radius: 10px;
        }

        [data-testid="stMetric"] {
            background: #f0f9ff;
            border: 1px solid #bae6fd;
            border-radius: 12px;
            padding: 1rem;
        }

        hr {
            border-color: #e2e8f0;
        }

        a {
            color: #0284c7 !important;
        }

        img {
            border-radius: 10px;
        }

        [data-testid="stDecoration"] {
            display: none;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
