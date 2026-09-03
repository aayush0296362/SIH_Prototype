import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>

        /* ================================
           LMSCAN - PROFESSIONAL THEME
           Sky Blue + White
        ================================= */

        /* Main application background */
        .stApp {
            background: #ffffff;
            color: #0f172a;
        }

        /* Main content width */
        .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* Headings */
        h1, h2, h3 {
            color: #0f172a !important;
            font-weight: 700;
        }

        h1 {
            letter-spacing: -0.5px;
        }

        /* Normal text */
        p, span, label {
            color: #334155;
        }

        /* Sky-blue buttons */
        .stButton > button {
            background: #38bdf8;
            color: #ffffff;
            border: none;
            border-radius: 10px;
            padding: 0.55rem 1.2rem;
            font-weight: 600;
            transition: 0.2s ease;
        }

        .stButton > button:hover {
            background: #0ea5e9;
            color: #ffffff;
            border: none;
        }

        /* File uploader */
        [data-testid="stFileUploader"] {
            background: #f0f9ff;
            border: 1px solid #bae6fd;
            border-radius: 12px;
            padding: 0.5rem;
        }

        /* Expanders */
        [data-testid="stExpander"] {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
        }

        /* Success messages */
        [data-testid="stAlert"] {
            border-radius: 10px;
        }

        /* Metric cards */
        [data-testid="stMetric"] {
            background: #f0f9ff;
            border: 1px solid #bae6fd;
            border-radius: 12px;
            padding: 1rem;
        }

        /* Horizontal divider */
        hr {
            border-color: #e2e8f0;
        }

        /* Links */
        a {
            color: #0284c7 !important;
        }

        /* Images */
        img {
            border-radius: 10px;
        }

        /* Remove excessive Streamlit decoration */
        [data-testid="stDecoration"] {
            display: none;
        }

        /* Clean top spacing */
        header[data-testid="stHeader"] {
            background: transparent;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )