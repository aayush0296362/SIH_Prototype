import streamlit as st
import hashlib
from services.core import analyze_package
from services.inspection_db import init_db, save_inspection, get_inspections, get_inspection, delete_inspection

st.set_page_config(
    page_title="LMSCAN | Package Compliance",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Persistent inspection history database
init_db()

# ============================================================
# PROFESSIONAL WHITE + SKY BLUE THEME
# ============================================================

st.markdown("""
<style>
.stApp {
    background: #ffffff;
    color: #0f172a;
}

.main .block-container {
    max-width: 1120px;
    padding-top: 1rem;
    padding-bottom: 2.5rem;
}

/* Header */
.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0 14px;
    margin-bottom: 20px;
    border-bottom: 2px solid #e0f2fe;
}

.brand {
    font-size: 25px;
    font-weight: 800;
    color: #0f172a;
}

.brand-blue {
    color: #0284c7;
}

.brand-sub {
    display: block;
    margin-top: 3px;
    font-size: 8px;
    letter-spacing: 1.7px;
    color: #64748b;
    font-weight: 700;
}

.status-pill {
    background: #f0f9ff;
    color: #0369a1;
    border: 1px solid #7dd3fc;
    border-radius: 20px;
    padding: 7px 13px;
    font-size: 11px;
    font-weight: 700;
}

/* Main hero */
.hero {
    background: #f0f9ff;
    border: 2px solid #38bdf8;
    border-radius: 16px;
    padding: 26px 30px 24px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 6px 18px rgba(14,165,233,0.10);
}

.hero:before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 6px;
    background: #0ea5e9;
}

.hero:after {
    content: "";
    position: absolute;
    right: -55px;
    top: -75px;
    width: 160px;
    height: 160px;
    border-radius: 50%;
    border: 22px solid rgba(56,189,248,0.13);
}

.hero-badge {
    display: inline-block;
    background: #ffffff;
    border: 1px solid #7dd3fc;
    color: #0284c7;
    border-radius: 20px;
    padding: 6px 11px;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1px;
    position: relative;
    z-index: 2;
}

.hero-title {
    margin-top: 10px;
    font-size: 34px;
    line-height: 1.1;
    font-weight: 800;
    letter-spacing: -0.8px;
    color: #0f172a;
    position: relative;
    z-index: 2;
}

.hero-title span {
    color: #0284c7;
}

.hero-text {
    max-width: 720px;
    margin-top: 9px;
    color: #475569;
    font-size: 13px;
    line-height: 1.55;
    position: relative;
    z-index: 2;
}

.hero-chips {
    display: flex;
    justify-content: center;
    gap: 9px;
    flex-wrap: wrap;
    margin-top: 16px;
    position: relative;
    z-index: 2;
}

.hero-chip {
    background: #ffffff;
    border: 1px solid #bae6fd;
    border-radius: 8px;
    padding: 7px 12px;
    color: #0369a1;
    font-size: 10px;
    font-weight: 700;
}

/* Cards */
.card {
    background: #ffffff;
    border: 1px solid #bae6fd;
    border-top: 4px solid #38bdf8;
    border-radius: 13px;
    padding: 18px 19px;
    min-height: 135px;
    box-shadow: 0 4px 14px rgba(15,23,42,0.05);
}

.capture-card {
    min-height: 112px;
}

.card-icon {
    font-size: 24px;
}

.card-title {
    margin-top: 6px;
    font-size: 18px;
    font-weight: 800;
    color: #0f172a;
}

.card-text {
    margin-top: 6px;
    font-size: 12px;
    line-height: 1.5;
    color: #64748b;
}

/* Sections */
.section-heading {
    margin-top: 22px;
    margin-bottom: 5px;
    font-size: 19px;
    font-weight: 800;
    color: #0f172a;
}

.section-line {
    width: 38px;
    height: 4px;
    background: #38bdf8;
    border-radius: 10px;
    margin-bottom: 12px;
}

/* Workflow */
.workflow-card {
    background: #f8fcff;
    border: 1px solid #bae6fd;
    border-radius: 11px;
    padding: 12px 7px;
    text-align: center;
    min-height: 94px;
}

.workflow-number {
    display: inline-block;
    background: #e0f2fe;
    color: #0369a1;
    border-radius: 20px;
    padding: 4px 8px;
    font-size: 9px;
    font-weight: 800;
}

.workflow-title {
    margin-top: 6px;
    color: #0f172a;
    font-size: 12px;
    font-weight: 800;
}

.workflow-text {
    margin-top: 3px;
    color: #64748b;
    font-size: 9px;
}

/* Results */
.result-card {
    background: #ffffff;
    border: 1px solid #dbeafe;
    border-left: 4px solid #38bdf8;
    border-radius: 10px;
    padding: 12px 14px;
    min-height: 64px;
    box-shadow: 0 2px 8px rgba(15,23,42,0.03);
}

.result-label {
    color: #64748b;
    font-size: 9px;
    font-weight: 800;
    text-transform: uppercase;
}

.result-value {
    color: #0f172a;
    font-size: 14px;
    font-weight: 750;
    margin-top: 4px;
}

.result-missing {
    color: #94a3b8;
    font-size: 11px;
    margin-top: 4px;
}

.package-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin-top: 4px;
    align-items: start;
}

.package-section-card {
    min-height: 0;
}

.package-section-card {
    background: #ffffff;
    border: 1px solid #dbeafe;
    border-radius: 12px;
    padding: 14px 15px;
    box-shadow: 0 2px 8px rgba(15,23,42,0.03);
}

.package-section-title {
    color: #0369a1;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .5px;
    text-transform: uppercase;
    margin-bottom: 9px;
}

.package-field {
    padding: 8px 0;
    border-bottom: 1px solid #f1f5f9;
}

.package-field:last-child {
    border-bottom: 0;
    padding-bottom: 0;
}

.package-field-label {
    color: #64748b;
    font-size: 8px;
    font-weight: 800;
    text-transform: uppercase;
}

.package-field-value {
    color: #0f172a;
    font-size: 12px;
    font-weight: 750;
    line-height: 1.45;
    margin-top: 3px;
    word-break: break-word;
}

.package-field-meta {
    color: #94a3b8;
    font-size: 8px;
    margin-top: 3px;
}

.ai-chip {
    display: inline-block;
    margin-left: 5px;
    background: #eef2ff;
    color: #4338ca;
    border: 1px solid #c7d2fe;
    border-radius: 999px;
    padding: 2px 5px;
    font-size: 7px;
    font-weight: 800;
}

.fusion-warning {
    background: #fffbeb;
    border: 1px solid #fde68a;
    color: #92400e;
    border-radius: 9px;
    padding: 9px 11px;
    font-size: 9px;
    margin-top: 10px;
}

.key-facts {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
    margin: 4px 0 12px;
}

.key-fact {
    background: #f8fcff;
    border: 1px solid #dbeafe;
    border-radius: 11px;
    padding: 11px 12px;
}

.key-fact-label {
    color: #64748b;
    font-size: 8px;
    font-weight: 800;
    text-transform: uppercase;
}

.key-fact-value {
    color: #0f172a;
    font-size: 12px;
    font-weight: 800;
    margin-top: 4px;
    word-break: break-word;
}

.section-note {
    color: #94a3b8;
    font-size: 9px;
    margin: 2px 0 8px;
}

.metric-card {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 10px;
    padding: 14px;
    text-align: center;
}

.metric-number {
    color: #0284c7;
    font-size: 22px;
    font-weight: 800;
}

.metric-label {
    color: #64748b;
    font-size: 9px;
    font-weight: 800;
    margin-top: 3px;
}

.compliance-hero {
    background: linear-gradient(135deg, #f8fcff 0%, #eef9ff 100%);
    border: 1px solid #bae6fd;
    border-radius: 14px;
    padding: 18px 20px;
    margin: 8px 0 18px;
}

.compliance-decision {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    flex-wrap: wrap;
}

.decision-title {
    color: #0f172a;
    font-size: 16px;
    font-weight: 800;
}

.decision-subtitle {
    margin-top: 4px;
    color: #64748b;
    font-size: 11px;
}

.decision-pill {
    border-radius: 999px;
    padding: 8px 13px;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .3px;
    white-space: nowrap;
}

.decision-review {
    background: #fff7ed;
    color: #c2410c;
    border: 1px solid #fdba74;
}

.decision-pass {
    background: #ecfdf5;
    color: #047857;
    border: 1px solid #86efac;
}

.authority-card {
    background: #ffffff;
    border: 1px solid #dbeafe;
    border-radius: 13px;
    margin: 0 0 14px;
    overflow: hidden;
    box-shadow: 0 3px 12px rgba(15,23,42,0.04);
}

.authority-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 13px 16px;
    background: #f8fcff;
    border-bottom: 1px solid #e0f2fe;
}

.authority-name {
    color: #0f172a;
    font-size: 14px;
    font-weight: 800;
}

.authority-count {
    color: #64748b;
    font-size: 10px;
    font-weight: 700;
}

.rule-row {
    display: grid;
    grid-template-columns: 28px minmax(0, 1fr) auto;
    align-items: start;
    gap: 10px;
    padding: 12px 16px;
    border-bottom: 1px solid #f1f5f9;
}

.rule-row:last-child {
    border-bottom: 0;
}

.rule-icon {
    font-size: 15px;
    line-height: 1.4;
}

.rule-main {
    min-width: 0;
}

.rule-title {
    color: #0f172a;
    font-size: 11px;
    font-weight: 800;
    line-height: 1.4;
}

.rule-message {
    margin-top: 3px;
    color: #64748b;
    font-size: 10px;
    line-height: 1.45;
}

.rule-evidence {
    margin-top: 5px;
    color: #475569;
    font-size: 9px;
    line-height: 1.45;
}

.rule-evidence code {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 5px;
    padding: 2px 5px;
    color: #0369a1;
}

.rule-badge {
    border-radius: 999px;
    padding: 4px 7px;
    font-size: 8px;
    font-weight: 800;
    white-space: nowrap;
    align-self: start;
}

.badge-detected {
    background: #ecfdf5;
    color: #047857;
    border: 1px solid #a7f3d0;
}

.badge-missing {
    background: #fff7ed;
    color: #c2410c;
    border: 1px solid #fed7aa;
}

.badge-unclear {
    background: #fffbeb;
    color: #a16207;
    border: 1px solid #fde68a;
}

.badge-na {
    background: #f8fafc;
    color: #64748b;
    border: 1px solid #cbd5e1;
}

.review-box {
    background: #fffaf5;
    border: 1px solid #fed7aa;
    border-left: 4px solid #f59e0b;
    border-radius: 11px;
    padding: 13px 15px;
    margin-top: 14px;
}

.review-title {
    color: #9a3412;
    font-size: 12px;
    font-weight: 800;
}

.review-item {
    margin-top: 7px;
    color: #7c2d12;
    font-size: 10px;
    line-height: 1.45;
}

.legend {
    display: flex;
    gap: 7px;
    flex-wrap: wrap;
    margin: 4px 0 14px;
}

.legend-chip {
    border-radius: 999px;
    padding: 4px 8px;
    font-size: 8px;
    font-weight: 800;
}

.ocr-note {
    color: #64748b;
    font-size: 9px;
    margin-top: 3px;
}

/* Buttons */
div.stButton > button {
    border-radius: 9px;
    min-height: 42px;
    font-weight: 700;
}

/* Primary action buttons — force the same solid blue style across Streamlit versions. */
div.stButton > button[kind="primary"],
div.stButton > button[data-testid="stBaseButton-primary"] {
    background: #0284c7 !important;
    border: 1px solid #0284c7 !important;
    color: #ffffff !important;
    box-shadow: none !important;
}

div.stButton > button[kind="primary"]:hover,
div.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: #0369a1 !important;
    border-color: #0369a1 !important;
    color: #ffffff !important;
}

div.stButton > button[kind="primary"]:active,
div.stButton > button[data-testid="stBaseButton-primary"]:active {
    background: #075985 !important;
    border-color: #075985 !important;
    color: #ffffff !important;
}

/* Upload + camera areas */
[data-testid="stFileUploader"] {
    background: #f0f9ff !important;
    border: 1px dashed #38bdf8 !important;
    border-radius: 11px !important;
    padding: 6px !important;
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
    border-color: #0284c7 !important;
    color: #0284c7 !important;
}

/* The camera widget is sized through st.camera_input(width=...). */
[data-testid="stCameraInput"] {
    max-width: 420px !important;
}

[data-testid="stCameraInput"] video,
[data-testid="stCameraInput"] img {
    width: 100% !important;
    max-width: 420px !important;
    max-height: 245px !important;
    object-fit: cover !important;
    border-radius: 10px !important;
}

[data-testid="stCameraInput"] button {
    border-radius: 8px !important;
    font-weight: 700 !important;
}

@media (max-width: 800px) {
    .key-facts {
        grid-template-columns: 1fr !important;
    }
}

/* Back button */
.back-button-wrap {
    margin-bottom: 5px;
}

/* Streamlit renders secondary buttons with this base test id. */
[data-testid="stBaseButton-secondary"] {
    background: #e0f2fe !important;
    color: #0369a1 !important;
    border: 1px solid #7dd3fc !important;
    border-radius: 9px !important;
    min-height: 38px !important;
    padding: 6px 14px !important;
    font-weight: 750 !important;
}

[data-testid="stBaseButton-secondary"]:hover {
    background: #bae6fd !important;
    color: #0369a1 !important;
    border-color: #38bdf8 !important;
}

/* Keep the back action visually compact rather than full-width. */
.back-button-wrap {
    width: 112px;
}

.package-scan-helper {
    color: #64748b;
    font-size: 10px;
    margin-top: -4px;
    margin-bottom: 9px;
}




/* Inspector form controls */
[data-testid="stRadio"] label,
[data-testid="stRadio"] label p,
[data-testid="stRadio"] p {
    color: #0f172a !important;
    font-weight: 650 !important;
}

[data-testid="stRadio"] div[role="radiogroup"] {
    gap: 10px !important;
}

[data-testid="stTextArea"] label,
[data-testid="stTextArea"] label p {
    color: #475569 !important;
    font-weight: 700 !important;
}

[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #bae6fd !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    line-height: 1.5 !important;
}

[data-testid="stTextArea"] textarea::placeholder {
    color: #94a3b8 !important;
    opacity: 1 !important;
}

[data-testid="stTextArea"] textarea:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 1px #38bdf8 !important;
}

[data-testid="stRadio"] input + div {
    border-color: #94a3b8 !important;
}

[data-testid="stRadio"] input:checked + div {
    border-color: #0284c7 !important;
}

/* Inspector Review */
.violation-card {
    background: #fffaf5;
    border: 1px solid #fed7aa;
    border-left: 5px solid #f59e0b;
    border-radius: 12px;
    padding: 14px 16px;
    margin: 0 0 10px;
}
.violation-title {
    color: #0f172a;
    font-size: 12px;
    font-weight: 800;
}
.violation-meta {
    color: #9a3412;
    font-size: 9px;
    font-weight: 700;
    margin-top: 4px;
}
.violation-message {
    color: #64748b;
    font-size: 10px;
    line-height: 1.5;
    margin-top: 6px;
}
.violation-evidence {
    background: #ffffff;
    border: 1px solid #fde68a;
    border-radius: 8px;
    padding: 7px 9px;
    margin-top: 8px;
    color: #475569;
    font-size: 9px;
    line-height: 1.45;
}
.review-complete {
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    border-left: 5px solid #10b981;
    border-radius: 12px;
    padding: 13px 15px;
    color: #065f46;
    font-size: 10px;
    font-weight: 700;
    margin-top: 12px;
}

/* Inspection History */
.history-card {
    display:grid;
    grid-template-columns: minmax(0, 1fr) 150px 240px;
    gap:16px;
    align-items:center;
    background:#ffffff;
    border:1px solid #dbeafe;
    border-left:4px solid #38bdf8;
    border-radius:12px;
    padding:14px 16px;
    margin:0 0 8px;
    box-shadow:0 2px 8px rgba(15,23,42,0.03);
}
.history-id { color:#0284c7; font-size:9px; font-weight:800; letter-spacing:.5px; }
.history-product { color:#0f172a; font-size:14px; font-weight:800; margin-top:3px; }
.history-meta { color:#64748b; font-size:9px; margin-top:4px; }
.history-score { text-align:center; }
.history-score-number { color:#0284c7; font-size:19px; font-weight:800; }
.history-score-label { color:#64748b; font-size:8px; font-weight:800; margin-top:2px; }
.history-decision { text-align:right; }
.history-decision-pill { display:inline-block; background:#f0f9ff; color:#0369a1; border:1px solid #bae6fd; border-radius:999px; padding:5px 9px; font-size:8px; font-weight:800; }
.history-date { color:#94a3b8; font-size:8px; margin-top:5px; }
.delete-confirm-box {
    background:#fff7ed;
    border:1px solid #fdba74;
    border-left:4px solid #f97316;
    border-radius:11px;
    padding:12px 14px;
    margin: -2px 0 12px;
}
.delete-confirm-title { color:#9a3412; font-size:12px; font-weight:800; }
.delete-confirm-text { color:#7c2d12; font-size:10px; margin-top:4px; line-height:1.45; }
@media (max-width: 850px) {
    .history-card { grid-template-columns:1fr 1fr; }
    .history-decision { text-align:left; }
}

/* Inspector Portal */
.inspector-banner {
    background: #f8fcff;
    border: 1px solid #bae6fd;
    border-left: 5px solid #0284c7;
    border-radius: 12px;
    padding: 13px 16px;
    margin: 8px 0 16px;
}
.inspector-banner-title { color:#0f172a; font-size:14px; font-weight:800; }
.inspector-banner-text { color:#64748b; font-size:10px; margin-top:4px; line-height:1.5; }
.inspector-stat {
    background:#fff; border:1px solid #dbeafe; border-radius:11px;
    padding:12px; text-align:center; min-height:78px;
}
.inspector-stat-number { color:#0284c7; font-size:20px; font-weight:800; }
.inspector-stat-label { color:#64748b; font-size:8px; font-weight:800; margin-top:3px; }

/* Footer */
.footer {
    border-top: 1px solid #e2e8f0;
    margin-top: 28px;
    padding-top: 13px;
    text-align: center;
    color: #94a3b8;
    font-size: 10px;
}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "home"
if "consumer_scan_started" not in st.session_state:
    st.session_state.consumer_scan_started = False
if "evidence_files" not in st.session_state:
    st.session_state.evidence_files = []
if "inspector_files" not in st.session_state:
    st.session_state.inspector_files = []
if "inspector_scan_started" not in st.session_state:
    st.session_state.inspector_scan_started = False
if "inspector_review_status" not in st.session_state:
    st.session_state.inspector_review_status = {}
if "inspector_decision" not in st.session_state:
    st.session_state.inspector_decision = "Requires Review"
if "inspector_notes" not in st.session_state:
    st.session_state.inspector_notes = ""
if "inspection_submitted" not in st.session_state:
    st.session_state.inspection_submitted = False
if "pending_delete_inspection_id" not in st.session_state:
    st.session_state.pending_delete_inspection_id = None
if "inspection_saved_id" not in st.session_state:
    st.session_state.inspection_saved_id = None
if "inspector_view" not in st.session_state:
    st.session_state.inspector_view = "new"
if "selected_inspection_id" not in st.session_state:
    st.session_state.selected_inspection_id = None


@st.cache_resource(show_spinner=False)
def _cached_core_analyzer():
    """Keep the imported core pipeline available across Streamlit reruns."""
    return analyze_package


def _image_signature(image_files):
    """Create a stable cache key from the actual uploaded image bytes."""
    digest = hashlib.sha256()
    for image_file in image_files:
        try:
            raw = image_file.getvalue()
        except Exception:
            raw = bytes(image_file)
        digest.update(len(raw).to_bytes(8, "big"))
        digest.update(raw)
    return digest.hexdigest()


@st.cache_data(show_spinner=False, max_entries=24)
def _cached_package_analysis(image_signature, image_bytes_list):
    """
    Cache the expensive OCR + AI + fusion + compliance pipeline.
    The signature prevents Streamlit from reprocessing identical images.
    """
    analyzer = _cached_core_analyzer()
    return analyzer(image_bytes_list, use_ai=True)

def render_topbar():
    st.markdown("""
    <div class="topbar">
      <div class="brand">📦 LM<span class="brand-blue">SCAN</span>
        <span class="brand-sub">LEGAL METROLOGY PACKAGE COMPLIANCE</span>
      </div>
      <div class="status-pill">● Inspection Platform</div>
    </div>
    """, unsafe_allow_html=True)

def home_page():
    render_topbar()

    st.markdown("""
    <div class="hero">
      <div class="hero-badge">AI-ASSISTED PACKAGE INSPECTION</div>
      <div class="hero-title">Package Compliance <span>Made Simple.</span></div>
      <div class="hero-text">
        Capture a packaged product, extract visible declarations with OCR,
        and review evidence-based compliance findings.
      </div>
      <div class="hero-chips">
        <div class="hero-chip">📷 Capture</div>
        <div class="hero-chip">🔍 OCR</div>
        <div class="hero-chip">⚖️ Compliance</div>
        <div class="hero-chip">📋 Evidence</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns(2, gap="medium")

    with left:
        st.markdown("""
        <div class="card">
          <div class="card-icon">📷</div>
          <div class="card-title">Scan a Package</div>
          <div class="card-text">
            Capture or upload package images to extract declarations
            and check them against inspection rules.
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        if st.button(
            "Start Package Scan  →",
            use_container_width=True,
            type="primary",
            key="home_scan",
        ):
            st.session_state.page = "consumer"
            st.session_state.consumer_scan_started = False
            st.session_state.evidence_files = []
            st.rerun()

    with right:
        st.markdown("""
        <div class="card">
          <div class="card-icon">🛡️</div>
          <div class="card-title">Inspector Portal</div>
          <div class="card-text">
            Review inspection evidence, findings and structured
            compliance records.
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        if st.button(
            "Inspector Portal  →",
            use_container_width=True,
            type="primary",
            key="home_inspector",
        ):
            st.session_state.page = "inspector"
            st.session_state.inspector_scan_started = False
            st.session_state.inspector_files = []
            st.session_state.inspector_review_status = {}
            st.session_state.inspector_view = "new"
            st.session_state.inspection_saved_id = None
            st.session_state.inspector_decision = "Requires Review"
            st.session_state.inspector_notes = ""
            st.session_state.inspection_submitted = False
            st.rerun()

    st.markdown(
        '<div class="section-heading">⚙️ How LMSCAN Works</div>'
        '<div class="section-line"></div>',
        unsafe_allow_html=True,
    )

    columns = st.columns(5)
    steps = [
        ("01", "Capture", "Package image"),
        ("02", "OCR", "Read visible text"),
        ("03", "Extract", "Find declarations"),
        ("04", "Check", "Apply rules"),
        ("05", "Review", "Evidence result"),
    ]

    for column, (number, title, desc) in zip(columns, steps):
        with column:
            st.markdown(f"""
            <div class="workflow-card">
              <div class="workflow-number">{number}</div>
              <div class="workflow-title">{title}</div>
              <div class="workflow-text">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class="footer">
      LMSCAN • AI-assisted • Human verified • Evidence linked
      <br><br>
      SIH26034 — Legal Metrology Package Compliance Scanner
    </div>
    """, unsafe_allow_html=True)




def render_declarations(declarations):
    """Show the most useful package facts first, with deeper details collapsed."""
    import html

    st.markdown(
        '<div class="section-heading">📋 Package Information</div>'
        '<div class="section-line"></div>',
        unsafe_allow_html=True,
    )

    fusion_fields = declarations.get("fusion_fields", {})

    def value(field):
        return declarations.get(field)

    def fact(label, field):
        current = value(field)
        if current:
            return (
                '<div class="key-fact">'
                f'<div class="key-fact-label">{html.escape(label)}</div>'
                f'<div class="key-fact-value">✓ {html.escape(str(current))}</div>'
                '</div>'
            )
        return (
            '<div class="key-fact">'
            f'<div class="key-fact-label">{html.escape(label)}</div>'
            '<div class="key-fact-value" '
            'style="color:#94a3b8;font-weight:600;">Not detected</div>'
            '</div>'
        )

    key_fields = [
        ("Product", "product_name"),
        ("MRP", "mrp"),
        ("Net Quantity", "net_quantity"),
        ("Batch / Lot", "batch_number"),
        ("Packed / Manufacturing", "manufacturing_date"),
        ("Expiry / Use-by", "expiry_date"),
    ]

    st.markdown(
        '<div class="key-facts">'
        + "".join(fact(label, field) for label, field in key_fields)
        + '</div>',
        unsafe_allow_html=True,
    )

    # Deeper information is grouped into compact expanders rather than shown
    # all at once.
    with st.expander("🔎 Regulatory & Food Details", expanded=False):
        fields = [
            ("FSSAI Licence Number", "fssai_license_number"),
            ("Ingredients", "ingredients"),
            ("Nutrition Information", "nutrition"),
            ("Veg / Non-Veg", "veg_nonveg"),
            ("Allergen Declaration", "allergen_declaration"),
            ("Best Before", "best_before"),
            ("Country of Origin", "country_of_origin"),
        ]

        rows = []
        for label, field in fields:
            current = value(field)
            if current:
                status = "✓"
                val = html.escape(str(current))
            else:
                status = "—"
                val = "Not detected"

            rows.append(
                '<div class="package-field">'
                f'<div class="package-field-label">{html.escape(label)}</div>'
                f'<div class="package-field-value">{status} {val}</div>'
                '</div>'
            )

        st.markdown("".join(rows), unsafe_allow_html=True)

    with st.expander("🏭 Manufacturer & Contact", expanded=False):
        fields = [
            ("Manufacturer / Packer", "manufacturer"),
            ("Manufacturer Address", "manufacturer_address"),
            ("Consumer Care", "consumer_care"),
        ]

        rows = []
        for label, field in fields:
            current = value(field)
            decision = fusion_fields.get(field, {}).get("decision", "")

            if current:
                chip = ""
                if decision == "ai_fill":
                    chip = '<span class="ai-chip">AI SUPPORTED</span>'
                elif decision == "agreement":
                    chip = '<span class="ai-chip">AI + OCR</span>'

                rows.append(
                    '<div class="package-field">'
                    f'<div class="package-field-label">{html.escape(label)}{chip}</div>'
                    f'<div class="package-field-value">✓ {html.escape(str(current))}</div>'
                    '</div>'
                )
            else:
                rows.append(
                    '<div class="package-field">'
                    f'<div class="package-field-label">{html.escape(label)}</div>'
                    '<div class="package-field-value" '
                    'style="color:#94a3b8;font-weight:600;">Not detected</div>'
                    '</div>'
                )

        st.markdown("".join(rows), unsafe_allow_html=True)

    with st.expander("📦 Storage & Usage", expanded=False):
        fields = [
            ("Storage Instructions", "storage_instructions"),
            ("Directions for Use", "directions_for_use"),
        ]

        rows = []
        for label, field in fields:
            current = value(field)
            rows.append(
                '<div class="package-field">'
                f'<div class="package-field-label">{html.escape(label)}</div>'
                + (
                    f'<div class="package-field-value">✓ {html.escape(str(current))}</div>'
                    if current
                    else '<div class="package-field-value" style="color:#94a3b8;font-weight:600;">Not detected</div>'
                )
                + '</div>'
            )

        st.markdown("".join(rows), unsafe_allow_html=True)

    # Surface only genuinely useful AI/fusion activity.
    fusion = declarations.get("fusion", {})
    ai_additions = sum(
        1
        for item in fusion.get("fields", {}).values()
        if item.get("decision") == "ai_fill"
    )
    conflicts = sum(
        1
        for item in fusion.get("fields", {}).values()
        if item.get("decision") == "conflict"
    )

    if ai_additions or conflicts:
        st.markdown(
            '<div class="fusion-warning">🔗 '
            + html.escape(
                f"AI-supported additions: {ai_additions} • "
                f"Conflicts requiring review: {conflicts}"
            )
            + '</div>',
            unsafe_allow_html=True,
        )

def render_compliance(result):
    'Render a professional, easy-to-scan regulatory compliance dashboard.'
    if not result:
        return

    import html

    findings = result.get("rules") or result.get("findings") or []

    # Calculate the visible score from the actual displayed rules.
    applicable_findings = [
        f for f in findings
        if f.get("status") != "not_applicable"
    ]
    detected_count = sum(
        1 for f in applicable_findings if f.get("status") == "detected"
    )
    missing_count = sum(
        1 for f in applicable_findings if f.get("status") == "missing"
    )
    unclear_count = sum(
        1 for f in applicable_findings if f.get("status") == "unclear"
    )
    na_count = sum(
        1 for f in findings if f.get("status") == "not_applicable"
    )
    applicable_count = len(applicable_findings)

    compliance_percent = (
        round((detected_count / applicable_count) * 100, 1)
        if applicable_count else 100.0
    )

    if missing_count:
        decision = "REQUIRES REVIEW"
        decision_class = "decision-review"
        decision_icon = "⚠️"
        decision_text = (
            f"{missing_count} applicable requirement"
            f"{'s' if missing_count != 1 else ''} not detected."
        )
    elif unclear_count:
        decision = "REQUIRES REVIEW"
        decision_class = "decision-review"
        decision_icon = "⚠️"
        decision_text = (
            f"{unclear_count} requirement"
            f"{'s' if unclear_count != 1 else ''} need clarification."
        )
    else:
        decision = "COMPLIANCE CHECK PASSED"
        decision_class = "decision-pass"
        decision_icon = "✅"
        decision_text = "All currently applicable rules have evidence."

    st.markdown(
        '<div class="section-heading">⚖️ Compliance Inspection</div>'
        '<div class="section-line"></div>',
        unsafe_allow_html=True,
    )

    hero_html = (
        '<div class="compliance-hero">'
        '<div class="compliance-decision">'
        '<div>'
        f'<div class="decision-title">{decision_icon} {html.escape(decision)}</div>'
        f'<div class="decision-subtitle">{html.escape(decision_text)}</div>'
        '</div>'
        f'<div class="decision-pill {decision_class}">'
        f'{compliance_percent}% COMPLIANCE'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    metrics = [
        (m1, f"{compliance_percent}%", "COMPLIANCE"),
        (m2, f"{detected_count}/{applicable_count}", "RULES SATISFIED"),
        (m3, str(missing_count + unclear_count), "REQUIRING REVIEW"),
        (m4, str(na_count), "NOT APPLICABLE"),
    ]
    for col, number, label in metrics:
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-number">{html.escape(number)}</div>'
                f'<div class="metric-label">{html.escape(label)}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    context = result.get("context", {})
    context_items = []
    if context.get("is_food") is True:
        context_items.append("Food product")
    elif context.get("is_food") is False:
        context_items.append("Food status not confirmed")

    if context.get("is_imported") is True:
        context_items.append("Imported")
    elif context.get("is_imported") is False:
        context_items.append("Domestic / not identified as imported")

    if context_items:
        st.markdown(
            '<div class="ocr-note">Context used by rule engine: '
            + html.escape(" • ".join(context_items))
            + '</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="legend">'
        '<span class="legend-chip badge-detected">✅ DETECTED</span>'
        '<span class="legend-chip badge-missing">❌ MISSING</span>'
        '<span class="legend-chip badge-unclear">⚠️ UNCLEAR</span>'
        '<span class="legend-chip badge-na">— NOT APPLICABLE</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Group rules by authority so the legal source is immediately clear.
    groups = {}
    for finding in findings:
        authority = finding.get("authority") or "Inspection Rules"
        groups.setdefault(authority, []).append(finding)

    status_meta = {
        "detected": ("✅", "badge-detected", "DETECTED"),
        "missing": ("❌", "badge-missing", "MISSING"),
        "unclear": ("⚠️", "badge-unclear", "UNCLEAR"),
        "not_applicable": ("—", "badge-na", "NOT APPLICABLE"),
    }

    authority_order = ["FSSAI", "Legal Metrology"]
    ordered_authorities = (
        [a for a in authority_order if a in groups]
        + [a for a in groups if a not in authority_order]
    )

    st.markdown("### 📑 Regulatory Checks")

    for authority in ordered_authorities:
        authority_findings = groups[authority]
        applicable_here = [
            f for f in authority_findings
            if f.get("status") != "not_applicable"
        ]
        satisfied_here = sum(
            1 for f in applicable_here if f.get("status") == "detected"
        )

        row_html = []
        for finding in authority_findings:
            finding_status = finding.get("status", "unclear")
            icon, badge_class, badge_text = status_meta.get(
                finding_status,
                ("ℹ️", "badge-unclear", "REVIEW"),
            )

            label = html.escape(
                str(
                    finding.get("requirement")
                    or finding.get("label")
                    or finding.get("field")
                    or "Requirement"
                )
            )
            message = html.escape(str(finding.get("message", "")))

            evidence_html = ""
            value = finding.get("value")
            if value:
                evidence_html = (
                    '<div class="rule-evidence">Evidence: '
                    f'<code>{html.escape(str(value))}</code></div>'
                )

            source_html = ""
            rule_id = finding.get("rule_id")
            source = finding.get("source")
            if rule_id:
                source_text = str(rule_id)
                if source:
                    source_text += f" • {source}"
                source_html = (
                    f'<div class="rule-evidence">{html.escape(source_text)}</div>'
                )

            row_html.append(
                '<div class="rule-row">'
                f'<div class="rule-icon">{icon}</div>'
                '<div class="rule-main">'
                f'<div class="rule-title">{label}</div>'
                f'<div class="rule-message">{message}</div>'
                f'{evidence_html}'
                f'{source_html}'
                '</div>'
                f'<div class="rule-badge {badge_class}">{badge_text}</div>'
                '</div>'
            )

        rows_html = "".join(row_html)
        header_html = (
            '<div class="authority-header">'
            f'<div class="authority-name">⚖️ {html.escape(str(authority))}</div>'
            f'<div class="authority-count">{satisfied_here}/{len(applicable_here)} '
            'applicable satisfied</div>'
            '</div>'
        )

        st.markdown(
            '<div class="authority-card">'
            + header_html
            + rows_html
            + '</div>',
            unsafe_allow_html=True,
        )

    review_items = [
        f for f in findings
        if f.get("status") in ("missing", "unclear")
    ]

    if review_items:
        review_html = []
        for finding in review_items:
            label = html.escape(
                str(
                    finding.get("requirement")
                    or finding.get("label")
                    or finding.get("field")
                    or "Requirement"
                )
            )
            message = html.escape(
                str(finding.get("message", "Review required."))
            )
            severity = str(finding.get("severity", "")).upper()
            severity_text = f" • {severity} priority" if severity else ""
            review_html.append(
                f'<div class="review-item">• <strong>{label}</strong>: '
                f'{message}{html.escape(severity_text)}</div>'
            )

        st.markdown(
            '<div class="review-box">'
            '<div class="review-title">⚠️ Items Requiring Human Review</div>'
            + "".join(review_html)
            + '</div>',
            unsafe_allow_html=True,
        )

    st.caption(
        "Compliance score = detected applicable rules ÷ total applicable rules. "
        "Not Applicable rules are excluded."
    )

def consumer_page():
    render_topbar()
    back_col, _ = st.columns([1.2, 8.8], gap="small")
    with back_col:
        if st.button("← Back to Home", key="back_home", type="secondary"):
            st.session_state.page = "home"
            st.session_state.consumer_scan_started = False
            st.session_state.evidence_files = []
            st.rerun()
    st.markdown('<div style="margin-top:15px;"><div class="hero-badge">CONSUMER VERIFICATION</div><h1 style="margin-top:12px;">📦 Scan a Package</h1><p style="color:#64748b;">Capture clear package evidence before checking mandatory product declarations.</p></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-heading">📸 Capture Package Evidence</div>'
        '<div class="section-line"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="package-scan-helper">'
        'Use a clear, well-lit photo. Multiple views improve declaration coverage.'
        '</div>',
        unsafe_allow_html=True,
    )
    camera_col, upload_col = st.columns(2, gap="large")
    with camera_col:
        st.markdown('<div class="card capture-card" style="min-height:96px;"><div class="card-icon">📷</div><div class="card-title">Take a Photo</div><div class="card-text">Capture a clear photograph of the package.</div></div>', unsafe_allow_html=True)
        camera_photo = st.camera_input(
            "Capture package",
            key="package_camera",
            width=420,
        )
    with upload_col:
        st.markdown('<div class="card capture-card" style="min-height:96px;"><div class="card-icon">📁</div><div class="card-title">Upload Images</div><div class="card-text">Upload one or more package photographs. Multiple views can improve evidence coverage.</div></div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload package photographs",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="consumer_package_upload",
            width=420,
        )
    evidence_files=[]
    if camera_photo is not None: evidence_files.append(camera_photo)
    if uploaded_files: evidence_files.extend(uploaded_files)
    if evidence_files: st.session_state.evidence_files=evidence_files
    elif not st.session_state.consumer_scan_started: st.session_state.evidence_files=[]
    evidence_files=st.session_state.get("evidence_files",[])
    if evidence_files:
        st.markdown('<div class="section-heading">🖼️ Evidence Review</div><div class="section-line"></div>', unsafe_allow_html=True)
        st.success(f"{len(evidence_files)} image{'s' if len(evidence_files)!=1 else ''} ready for analysis.")
        preview_columns=st.columns(min(len(evidence_files),4))
        for index,image_file in enumerate(evidence_files):
            with preview_columns[index % len(preview_columns)]:
                st.image(image_file, caption=getattr(image_file,"name",f"Image {index+1}"), use_container_width=True)
        if st.button("🔍 Analyze Package", type="primary", use_container_width=True, key="analyze_package"):
            st.session_state.consumer_scan_started=True; st.rerun()
    if not st.session_state.get("consumer_scan_started",False): return
    evidence_files=st.session_state.get("evidence_files",[])
    if not evidence_files: st.warning("Please capture or upload a package image first."); return
    st.markdown(
        '<div class="section-heading">🧠 Package Analysis</div>'
        '<div class="section-line"></div>',
        unsafe_allow_html=True,
    )

    image_bytes_list = []
    for image_file in evidence_files:
        try:
            image_file.seek(0)
        except Exception:
            pass
        image_bytes_list.append(image_file.getvalue())

    image_signature = _image_signature(evidence_files)

    with st.spinner(
        "Running LMSCAN analysis (OCR → AI → Fusion → Compliance)..."
    ):
        inspection = _cached_package_analysis(
            image_signature,
            tuple(image_bytes_list),
        )

    if inspection.get("status") != "ok":
        st.error("Package analysis could not be completed.")
        for error in inspection.get("errors", []):
            st.write(f"• {error}")
        return

    ocr_results = inspection.get("ocr_results", [])
    declarations = inspection.get("declarations", {})
    compliance_result = inspection.get("compliance", {})

    st.success(
        f"LMSCAN analysis completed — "
        f"{len(ocr_results)} OCR evidence elements processed."
    )

    render_declarations(declarations)

    with st.expander("🧪 Analysis Engine Details"):
        ai_result = inspection.get("ai") or {}
        fusion_result = inspection.get("fusion") or {}

        st.write(
            f"**AI provider:** {ai_result.get('provider', 'not used')}  "
            f"• **Model:** {ai_result.get('model', 'not used')}"
        )

        ai_errors = ai_result.get("errors", [])
        if ai_errors:
            st.warning(
                "AI layer reported an issue; deterministic results were "
                "retained where possible."
            )
            for error in ai_errors:
                st.write(f"• {error}")
        else:
            st.success("OpenRouter semantic extraction completed.")

        st.write(
            f"**Fusion:** {fusion_result.get('detected_count', 0)} detected • "
            f"{fusion_result.get('unclear_count', 0)} unclear • "
            f"{fusion_result.get('missing_count', 0)} missing"
        )
        st.caption("Performance: identical package images are cached to avoid repeating OCR + AI work on Streamlit reruns.")

        ai_fill_count = sum(
            1
            for item in fusion_result.get("fields", {}).values()
            if item.get("decision") == "ai_fill"
        )
        conflict_count = sum(
            1
            for item in fusion_result.get("fields", {}).values()
            if item.get("decision") == "conflict"
        )

        st.write(
            f"**AI-supported additions:** {ai_fill_count}  •  "
            f"**Conflicts requiring review:** {conflict_count}"
        )

    with st.expander("🔎 OCR Evidence"):
        for i, item in enumerate(ocr_results):
            st.write(
                f"{i + 1}. {item.get('text', '')} | "
                f"confidence={item.get('confidence', 0):.3f} | "
                f"source={item.get('source', 'unknown')}"
            )

    render_compliance(compliance_result)

    st.markdown(
        '<div class="section-heading">📝 Raw Extracted Text</div>'
        '<div class="section-line"></div>',
        unsafe_allow_html=True,
    )
    with st.expander("View Raw OCR Text"):
        raw_text = declarations.get("raw_text", [])
        if raw_text:
            for raw_line in raw_text:
                st.write(f"• {raw_line}")
        else:
            st.caption("No readable text detected.")

    st.markdown('<div class="footer">OCR → Declaration Extraction → Compliance Review</div>', unsafe_allow_html=True)


def render_inspector_summary(inspection):
    import html
    declarations = inspection.get("declarations", {}) or {}
    compliance = inspection.get("compliance", {}) or {}
    findings = compliance.get("rules") or compliance.get("findings") or []
    applicable = [f for f in findings if f.get("status") != "not_applicable"]
    detected = sum(1 for f in applicable if f.get("status") == "detected")
    missing = sum(1 for f in applicable if f.get("status") == "missing")
    unclear = sum(1 for f in applicable if f.get("status") == "unclear")
    na = sum(1 for f in findings if f.get("status") == "not_applicable")
    total = len(applicable)
    score = round((detected / total) * 100, 1) if total else 100.0
    review = missing or unclear
    decision = "REQUIRES INSPECTOR REVIEW" if review else "COMPLIANCE CHECK PASSED"
    icon = "⚠️" if review else "✅"
    cls = "decision-review" if review else "decision-pass"

    st.markdown('<div class="section-heading">🛡️ Inspection Summary</div><div class="section-line"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="compliance-hero"><div class="compliance-decision"><div>'
        f'<div class="decision-title">{icon} {html.escape(decision)}</div>'
        '<div class="decision-subtitle">LMSCAN evaluated the package evidence against the configured applicable rules. The inspector remains the final decision-maker.</div>'
        '</div>'
        f'<div class="decision-pill {cls}">{score}% COMPLIANCE</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    c1,c2,c3,c4 = st.columns(4)
    for col, number, label in [
        (c1,f"{detected}/{total}","RULES SATISFIED"),
        (c2,str(missing),"MISSING"),
        (c3,str(unclear),"UNCLEAR"),
        (c4,str(na),"NOT APPLICABLE"),
    ]:
        with col:
            st.markdown(
                f'<div class="inspector-stat"><div class="inspector-stat-number">{number}</div>'
                f'<div class="inspector-stat-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-heading">📌 Key Inspection Facts</div><div class="section-line"></div>', unsafe_allow_html=True)
    fields = [
        ("Product","product_name"),("MRP","mrp"),("Net Quantity","net_quantity"),
        ("Batch / Lot","batch_number"),("Manufacturer","manufacturer"),
        ("FSSAI Licence","fssai_license_number"),("Manufacturing / Packing","manufacturing_date"),
        ("Expiry / Use-by","expiry_date"),("Consumer Care","consumer_care"),
    ]
    cards = []
    for label, field in fields:
        value = declarations.get(field)
        display = html.escape(str(value)) if value else "Not detected"
        style = "" if value else ' style="color:#94a3b8;font-weight:600;"'
        cards.append(
            '<div class="package-field">'
            f'<div class="package-field-label">{html.escape(label)}</div>'
            f'<div class="package-field-value"{style}>{display}</div></div>'
        )
    st.markdown(
        '<div class="package-grid"><div class="package-section-card">'
        + ''.join(cards[:5]) +
        '</div><div class="package-section-card">' +
        ''.join(cards[5:]) +
        '</div></div>',
        unsafe_allow_html=True,
    )


def _reset_inspector_workflow():
    """Reset only the current inspection workflow state."""
    st.session_state.inspector_scan_started = False
    st.session_state.inspector_files = []
    st.session_state.inspector_review_status = {}
    st.session_state.inspector_decision = "Requires Review"
    st.session_state.inspector_notes = ""
    st.session_state.inspection_submitted = False
    st.session_state.inspection_saved_id = None
    st.session_state.pending_delete_inspection_id = None


def _inspection_status_label(decision):
    return {
        "Compliant": "✅ Compliant",
        "Requires Correction": "⚠️ Requires Correction",
        "Non-Compliant": "❌ Non-Compliant",
        "Unable to Determine": "❓ Unable to Determine",
    }.get(decision, decision or "Requires Review")


def _save_current_inspection(inspection, decision, notes, review_status):
    """Persist a complete inspector review and return its inspection ID."""
    declarations = inspection.get("declarations", {}) or {}
    compliance = inspection.get("compliance", {}) or {}
    findings = compliance.get("rules") or compliance.get("findings") or []
    applicable = [f for f in findings if f.get("status") != "not_applicable"]
    detected = sum(1 for f in applicable if f.get("status") == "detected")
    score = round((detected / len(applicable)) * 100, 1) if applicable else 100.0

    record = {
        "decision": decision,
        "notes": notes.strip(),
        "review_status": review_status,
        "inspection": inspection,
        "summary": {
            "product_name": declarations.get("product_name"),
            "manufacturer": declarations.get("manufacturer"),
            "manufacturer_address": declarations.get("manufacturer_address"),
            "batch_number": declarations.get("batch_number"),
            "mrp": declarations.get("mrp"),
            "net_quantity": declarations.get("net_quantity"),
            "fssai_license_number": declarations.get("fssai_license_number"),
            "manufacturing_date": declarations.get("manufacturing_date"),
            "expiry_date": declarations.get("expiry_date"),
            "compliance_percent": score,
            "applicable_rules": len(applicable),
            "detected_rules": detected,
            "missing_rules": sum(1 for f in applicable if f.get("status") == "missing"),
            "unclear_rules": sum(1 for f in applicable if f.get("status") == "unclear"),
            "evidence_images": inspection.get("images_processed", 0),
        },
    }
    return save_inspection(record)


def inspection_history_page():
    """Professional persistent inspection-history view."""
    render_topbar()

    back_col, _ = st.columns([1.2, 8.8], gap="small")
    with back_col:
        if st.button("← Inspector Portal", key="history_back", type="secondary"):
            st.session_state.inspector_view = "new"
            st.rerun()

    st.markdown(
        '<div style="margin-top:15px;">'
        '<div class="hero-badge">PERSISTENT INSPECTION RECORDS</div>'
        '<h1 style="margin-top:12px;">📋 Inspection History</h1>'
        '<p style="color:#64748b;">Every submitted inspector review is stored locally in the LMSCAN database and can be reopened for audit.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    records = get_inspections()

    if not records:
        st.info("No completed inspections have been saved yet. Complete an inspection to create the first history record.")
        if st.button("🔍 Start New Inspection", type="primary", use_container_width=True, key="history_start_new_empty"):
            st.session_state.inspector_view = "new"
            _reset_inspector_workflow()
            st.rerun()
        return

    # Summary metrics
    total = len(records)
    compliant = sum(1 for r in records if r.get("decision") == "Compliant")
    requires = sum(1 for r in records if r.get("decision") == "Requires Correction")
    non_compliant = sum(1 for r in records if r.get("decision") == "Non-Compliant")

    c1, c2, c3, c4 = st.columns(4)
    for col, number, label in [
        (c1, total, "TOTAL INSPECTIONS"),
        (c2, compliant, "COMPLIANT"),
        (c3, requires, "REQUIRES CORRECTION"),
        (c4, non_compliant, "NON-COMPLIANT"),
    ]:
        with col:
            st.markdown(
                f'<div class="inspector-stat"><div class="inspector-stat-number">{number}</div>'
                f'<div class="inspector-stat-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-heading">🔎 Search & Filter</div><div class="section-line"></div>', unsafe_allow_html=True)
    f1, f2 = st.columns([2.2, 1])
    with f1:
        search = st.text_input(
            "Search",
            placeholder="Product, manufacturer, batch or inspection ID...",
            key="history_search",
        ).strip().lower()
    with f2:
        status_filter = st.selectbox(
            "Decision",
            ["All", "Compliant", "Requires Correction", "Non-Compliant", "Unable to Determine"],
            key="history_status_filter",
        )

    filtered = []
    for record in records:
        haystack = " ".join([
            str(record.get("inspection_id", "")),
            str(record.get("summary", {}).get("product_name", "")),
            str(record.get("summary", {}).get("manufacturer", "")),
            str(record.get("summary", {}).get("batch_number", "")),
        ]).lower()
        if search and search not in haystack:
            continue
        if status_filter != "All" and record.get("decision") != status_filter:
            continue
        filtered.append(record)

    st.caption(f"Showing {len(filtered)} of {total} saved inspection record{'s' if total != 1 else ''}.")

    if not filtered:
        st.warning("No inspection records match the current filters.")
        return

    import html
    for record in filtered:
        summary = record.get("summary", {}) or {}
        decision = record.get("decision", "Requires Review")
        decision_text = html.escape(_inspection_status_label(decision))
        score = summary.get("compliance_percent", "—")
        product = html.escape(str(summary.get("product_name") or "Unknown product"))
        manufacturer = html.escape(str(summary.get("manufacturer") or "Manufacturer not detected"))
        batch = html.escape(str(summary.get("batch_number") or "Batch not detected"))
        inspection_id = html.escape(str(record.get("inspection_id", "—")))
        created_at = html.escape(str(record.get("created_at", "—")))

        st.markdown(
            '<div class="history-card">'
            '<div class="history-main">'
            f'<div class="history-id">{inspection_id}</div>'
            f'<div class="history-product">{product}</div>'
            f'<div class="history-meta">{manufacturer} • {batch}</div>'
            '</div>'
            '<div class="history-score">'
            f'<div class="history-score-number">{html.escape(str(score))}%</div>'
            '<div class="history-score-label">COMPLIANCE</div>'
            '</div>'
            '<div class="history-decision">'
            f'<div class="history-decision-pill">{decision_text}</div>'
            f'<div class="history-date">{created_at}</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        action_id = str(record.get("inspection_id"))
        view_col, delete_col = st.columns([3.2, 1], gap="small")
        with view_col:
            if st.button(
                "🔎 View Inspection Details →",
                use_container_width=True,
                type="primary",
                key=f"view_history_{action_id}",
            ):
                st.session_state.selected_inspection_id = action_id
                st.session_state.inspector_view = "history_detail"
                st.session_state.pending_delete_inspection_id = None
                st.rerun()
        with delete_col:
            if st.button(
                "🗑️ Delete",
                use_container_width=True,
                key=f"delete_history_{action_id}",
            ):
                st.session_state.pending_delete_inspection_id = action_id
                st.rerun()

        if st.session_state.get("pending_delete_inspection_id") == action_id:
            st.markdown(
                '<div class="delete-confirm-box">'
                '<div class="delete-confirm-title">⚠️ Delete this inspection record?</div>'
                f'<div class="delete-confirm-text">This will permanently remove <strong>{html.escape(action_id)}</strong> from Inspection History. This action cannot be undone.</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            cancel_col, confirm_col, _ = st.columns([1, 1.5, 5.5], gap="small")
            with cancel_col:
                if st.button("Cancel", key=f"cancel_delete_{action_id}", use_container_width=True):
                    st.session_state.pending_delete_inspection_id = None
                    st.rerun()
            with confirm_col:
                if st.button("Delete Permanently", type="primary", key=f"confirm_delete_{action_id}", use_container_width=True):
                    deleted = delete_inspection(action_id)
                    st.session_state.pending_delete_inspection_id = None
                    if deleted:
                        st.success(f"Inspection {action_id} deleted successfully.")
                    else:
                        st.warning(f"Inspection {action_id} was not found.")
                    st.rerun()


def inspection_history_detail_page():
    """Show one immutable saved inspection record in audit-friendly sections."""
    render_topbar()
    inspection_id = st.session_state.get("selected_inspection_id")
    record = get_inspection(inspection_id) if inspection_id else None

    if not record:
        st.error("Inspection record could not be found.")
        if st.button("← Back to History", key="detail_back_missing", type="secondary"):
            st.session_state.inspector_view = "history"
            st.rerun()
        return

    if st.button("← Back to Inspection History", key="detail_back", type="secondary"):
        st.session_state.inspector_view = "history"
        st.rerun()

    import html
    summary = record.get("summary", {}) or {}
    inspection = record.get("inspection", {}) or {}
    declarations = inspection.get("declarations", {}) or {}

    st.markdown(
        f'<div style="margin-top:15px;">'
        f'<div class="hero-badge">INSPECTION RECORD {html.escape(str(inspection_id))}</div>'
        f'<h1 style="margin-top:12px;">📄 Inspection Details</h1>'
        f'<p style="color:#64748b;">Saved on {html.escape(str(record.get("created_at", "—")))}.</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    decision = record.get("decision", "Requires Review")
    score = summary.get("compliance_percent", 0)
    decision_class = "decision-pass" if decision == "Compliant" else "decision-review"
    icon = "✅" if decision == "Compliant" else "⚠️" if decision == "Requires Correction" else "❌" if decision == "Non-Compliant" else "❓"

    st.markdown(
        '<div class="compliance-hero"><div class="compliance-decision"><div>'
        f'<div class="decision-title">{icon} {html.escape(decision.upper())}</div>'
        '<div class="decision-subtitle">Final inspector decision stored as part of the audit record.</div>'
        '</div>'
        f'<div class="decision-pill {decision_class}">{html.escape(str(score))}% COMPLIANCE</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-heading">📌 Package Summary</div><div class="section-line"></div>', unsafe_allow_html=True)
    summary_items = [
        ("Product", declarations.get("product_name")),
        ("Manufacturer", declarations.get("manufacturer")),
        ("Batch / Lot", declarations.get("batch_number")),
        ("MRP", declarations.get("mrp")),
        ("Net Quantity", declarations.get("net_quantity")),
        ("FSSAI Licence", declarations.get("fssai_license_number")),
        ("Manufacturing / Packing", declarations.get("manufacturing_date")),
        ("Expiry / Use-by", declarations.get("expiry_date")),
    ]
    cards = []
    for label, value in summary_items:
        display = html.escape(str(value)) if value else "Not detected"
        style = "" if value else ' style="color:#94a3b8;font-weight:600;"'
        cards.append(
            '<div class="key-fact">'
            f'<div class="key-fact-label">{html.escape(label)}</div>'
            f'<div class="key-fact-value"{style}>{display}</div>'
            '</div>'
        )
    st.markdown('<div class="key-facts">' + ''.join(cards) + '</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-heading">⚖️ Regulatory Findings</div><div class="section-line"></div>', unsafe_allow_html=True)
    render_compliance(inspection.get("compliance", {}) or {})

    st.markdown('<div class="section-heading">🧾 Inspector Review</div><div class="section-line"></div>', unsafe_allow_html=True)
    review_status = record.get("review_status", {}) or {}
    st.write("**Finding review decisions:**")
    if review_status:
        for rule_key, status in review_status.items():
            st.write(f"• {rule_key}: **{status}**")
    else:
        st.caption("No individual finding review decisions were recorded.")

    notes = record.get("notes", "")
    if notes:
        st.markdown(
            '<div class="review-box"><div class="review-title">📝 Inspector Notes</div>'
            f'<div class="review-item">{html.escape(str(notes)).replace(chr(10), "<br>")}</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.caption("No inspector notes were recorded.")

    with st.expander("📋 Extracted Declarations"):
        st.json({k: v for k, v in declarations.items() if k not in ("raw_text", "evidence", "fusion")})
    with st.expander("🔗 Evidence Fusion"):
        st.json(inspection.get("fusion", {}) or {})
    with st.expander("🤖 AI Engine"):
        ai = inspection.get("ai", {}) or {}
        st.write(f"Provider: {ai.get('provider', 'not used')} • Model: {ai.get('model', 'not used')}")
        if ai.get("errors"):
            for error in ai["errors"]:
                st.write(f"• {error}")
    with st.expander("🔍 OCR Evidence"):
        for i, item in enumerate(inspection.get("ocr_results", []) or []):
            st.write(f"{i + 1}. {item.get('text', '')} | confidence={item.get('confidence', 0):.3f}")


def inspector_page():
    """Inspector workspace: start a new inspection or open persistent history."""
    view = st.session_state.get("inspector_view", "new")
    if view == "history":
        inspection_history_page()
        return
    if view == "history_detail":
        inspection_history_detail_page()
        return

    render_topbar()
    back_col, nav_col = st.columns([1.2, 8.8], gap="small")
    with back_col:
        if st.button("← Back to Home", key="inspector_back", type="secondary"):
            st.session_state.page = "home"
            _reset_inspector_workflow()
            st.rerun()
    with nav_col:
        if st.button("📋 Inspection History", key="open_inspection_history", use_container_width=False):
            st.session_state.inspector_view = "history"
            st.rerun()

    st.markdown(
        '<div style="margin-top:15px;"><div class="hero-badge">AUTHORIZED INSPECTION WORKSPACE</div>'
        '<h1 style="margin-top:12px;">🛡️ Inspector Portal</h1>'
        '<p style="color:#64748b;">Run the same LMSCAN OCR, AI, evidence-fusion and compliance engine, '
        'then review the evidence before making an inspection decision.</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="inspector-banner"><div class="inspector-banner-title">⚖️ Human-in-the-loop inspection</div>'
        '<div class="inspector-banner-text">LMSCAN provides evidence and rule findings. '
        'The inspector remains the final decision-maker. Conflicting or missing declarations are surfaced for manual review.</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-heading">📸 Package Evidence</div><div class="section-line"></div>', unsafe_allow_html=True)
    camera_col, upload_col = st.columns(2, gap="large")
    with camera_col:
        st.markdown('<div class="card capture-card"><div class="card-icon">📷</div><div class="card-title">Capture Evidence</div><div class="card-text">Take a clear package photograph for inspection.</div></div>', unsafe_allow_html=True)
        camera = st.camera_input("Capture inspection evidence", key="inspector_camera", width=420)
    with upload_col:
        st.markdown('<div class="card capture-card"><div class="card-icon">📁</div><div class="card-title">Upload Evidence</div><div class="card-text">Upload multiple package views when more coverage is required.</div></div>', unsafe_allow_html=True)
        uploads = st.file_uploader("Upload inspection photographs", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="inspector_uploads", width=420)

    files = []
    if camera is not None:
        files.append(camera)
    if uploads:
        files.extend(uploads)
    if files:
        st.session_state.inspector_files = files
    files = st.session_state.get("inspector_files", [])

    if files:
        st.success(f"{len(files)} evidence image{'s' if len(files) != 1 else ''} ready for inspection.")
        cols = st.columns(min(len(files), 4))
        for i, f in enumerate(files):
            with cols[i % len(cols)]:
                st.image(f, caption=getattr(f, "name", f"Evidence {i + 1}"), use_container_width=True)
        if st.button("⚡ Run Inspector Analysis", type="primary", use_container_width=True, key="run_inspector_analysis"):
            st.session_state.inspector_scan_started = True
            st.rerun()

    if not st.session_state.get("inspector_scan_started", False):
        return

    files = st.session_state.get("inspector_files", [])
    if not files:
        st.warning("Please capture or upload inspection evidence first.")
        return

    image_bytes_list = []
    for image_file in files:
        try:
            image_file.seek(0)
        except Exception:
            pass
        image_bytes_list.append(image_file.getvalue())

    image_signature = _image_signature(files)
    with st.spinner("Running OCR → AI → Evidence Fusion → Compliance..."):
        inspection = _cached_package_analysis(image_signature, tuple(image_bytes_list))

    if inspection.get("status") != "ok":
        st.error("Inspection analysis could not be completed.")
        for error in inspection.get("errors", []):
            st.write(f"• {error}")
        return

    render_inspector_summary(inspection)
    st.markdown('<div class="section-heading">⚖️ Rule-by-Rule Findings</div><div class="section-line"></div>', unsafe_allow_html=True)
    render_compliance(inspection.get("compliance", {}))

    rules = (inspection.get("compliance", {}) or {}).get("rules") or (inspection.get("compliance", {}) or {}).get("findings") or []
    review = [f for f in rules if f.get("status") in ("missing", "unclear")]

    st.markdown('<div class="section-heading">⚠️ Findings Requiring Inspector Review</div><div class="section-line"></div>', unsafe_allow_html=True)
    if review:
        st.write(f"**{len(review)} finding(s)** need human attention before the final decision.")
        import html
        for idx, finding in enumerate(review):
            title = html.escape(str(finding.get("requirement") or finding.get("label") or finding.get("field") or "Inspection requirement"))
            authority = html.escape(str(finding.get("authority") or "Inspection Rules"))
            severity = html.escape(str(finding.get("severity") or "Review"))
            message = html.escape(str(finding.get("message") or "Manual verification is recommended."))
            evidence = finding.get("value")
            evidence_text = (
                f'<div class="violation-evidence"><strong>Evidence:</strong> {html.escape(str(evidence))}</div>'
                if evidence else
                '<div class="violation-evidence"><strong>Evidence:</strong> No confirmed value was extracted.</div>'
            )
            st.markdown(
                '<div class="violation-card">'
                f'<div class="violation-title">⚠️ {title}</div>'
                f'<div class="violation-meta">{authority} • {severity}</div>'
                f'<div class="violation-message">{message}</div>'
                f'{evidence_text}'
                '</div>',
                unsafe_allow_html=True,
            )
    else:
        st.success("No missing or unclear applicable rule findings were returned by the current rule set.")

    st.markdown('<div class="section-heading">📝 Final Inspector Decision</div><div class="section-line"></div>', unsafe_allow_html=True)
    decision = st.radio(
        "Inspection outcome",
        ["Compliant", "Requires Correction", "Non-Compliant", "Unable to Determine"],
        index=(0 if st.session_state.inspector_decision == "Compliant" else 1 if st.session_state.inspector_decision == "Requires Correction" else 2 if st.session_state.inspector_decision == "Non-Compliant" else 3),
        key="inspector_decision_widget",
        horizontal=True,
    )
    st.session_state.inspector_decision = decision

    notes = st.text_area(
        "Inspector Notes",
        value=st.session_state.inspector_notes,
        placeholder="Record observations, corrective action required, or other inspection notes...",
        height=110,
        key="inspector_notes_widget",
    )
    st.session_state.inspector_notes = notes

    submit_col, flag_col = st.columns(2)
    with submit_col:
        if st.button("✅ Submit Inspection Decision", type="primary", use_container_width=True, key="submit_inspection_decision"):
            if not st.session_state.get("inspection_saved_id"):
                saved_id = _save_current_inspection(
                    inspection,
                    st.session_state.inspector_decision,
                    st.session_state.inspector_notes,
                    dict(st.session_state.inspector_review_status),
                )
                st.session_state.inspection_saved_id = saved_id
            st.session_state.inspection_submitted = True
            st.rerun()
    with flag_col:
        if st.button("⚠️ Flag Inspection for Further Review", use_container_width=True, key="flag_inspection_review"):
            if not st.session_state.get("inspection_saved_id"):
                saved_id = _save_current_inspection(
                    inspection,
                    "Requires Correction",
                    st.session_state.inspector_notes,
                    dict(st.session_state.inspector_review_status),
                )
                st.session_state.inspection_saved_id = saved_id
            st.session_state.inspector_decision = "Requires Correction"
            st.session_state.inspection_submitted = True
            st.rerun()

    if st.session_state.get("inspection_submitted"):
        saved_id = st.session_state.get("inspection_saved_id")
        st.success(f"Inspection **{saved_id}** saved successfully. Final decision: **{st.session_state.inspector_decision}**")
        st.info("This inspection is now available in Inspection History and can be reopened for audit.")
        h1, h2 = st.columns(2)
        with h1:
            if st.button("📋 View Inspection History", type="primary", use_container_width=True, key="view_history_after_save"):
                st.session_state.inspector_view = "history"
                st.rerun()
        with h2:
            if st.button("➕ Start New Inspection", use_container_width=True, key="start_new_after_save"):
                _reset_inspector_workflow()
                st.rerun()

    st.caption("Submitted inspector reviews are persisted in the LMSCAN SQLite database for history and audit purposes.")


if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "consumer":
    consumer_page()
elif st.session_state.page == "inspector":
    inspector_page()
