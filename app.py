import streamlit as st
from io import BytesIO
from PIL import Image
import numpy as np
from services.ocr import extract_text
from services.extraction import extract_declarations
from services.compliance import check_compliance

st.set_page_config(
    page_title="LMSCAN | Package Compliance",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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

/* Buttons */
div.stButton > button {
    border-radius: 9px;
    min-height: 42px;
    font-weight: 700;
}

div.stButton > button[kind="primary"] {
    background: #0284c7;
    border-color: #0284c7;
    color: white;
}

div.stButton > button[kind="primary"]:hover {
    background: #0369a1;
    border-color: #0369a1;
}

/* Upload area */
[data-testid="stFileUploader"] {
    background: #f8fcff;
    border: 1px dashed #38bdf8;
    border-radius: 11px;
}

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
        if st.button("Start Package Scan  →", type="primary",
                     use_container_width=True, key="home_consumer"):
            st.session_state.page = "consumer"
            st.session_state.consumer_scan_started = False
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
        st.button("Inspector Portal  →", use_container_width=True,
                  disabled=True, key="home_inspector")

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
    fields = [("product_name","Product Name"),("mrp","MRP"),("net_quantity","Net Quantity"),("manufacturer","Manufacturer"),("manufacturing_date","Manufacturing Date"),("expiry_date","Expiry Date"),("best_before","Best Before"),("consumer_care","Consumer Care"),("country_of_origin","Country of Origin"),("batch_number","Batch Number")]
    st.markdown('<div class="section-heading">📋 Package Information</div><div class="section-line"></div>', unsafe_allow_html=True)
    for start in range(0, len(fields), 2):
        row, columns = fields[start:start+2], st.columns(2, gap="medium")
        for column, (field,label) in zip(columns,row):
            value = declarations.get(field)
            with column:
                if value:
                    st.markdown(f'<div class="result-card"><div class="result-label">{label}</div><div class="result-value">✓ {value}</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="result-card"><div class="result-label">{label}</div><div class="result-missing">Not detected in provided evidence</div></div>', unsafe_allow_html=True)
        st.write("")

def render_compliance(result):
    if not result:
        return
    detected = result.get("detected_fields", 0)
    total = result.get("total_fields", 10)
    missing = result.get("missing_fields", [])
    status = str(result.get("status", "review")).upper()
    st.markdown('<div class="section-heading">⚖️ Compliance Summary</div><div class="section-line"></div>', unsafe_allow_html=True)
    m1,m2,m3 = st.columns(3)
    for col,number,label in [(m1,f"{detected}/{total}","DECLARATIONS DETECTED"),(m2,str(len(missing)),"FIELDS REQUIRING REVIEW"),(m3,status,"INSPECTION STATUS")]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-number">{number}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)
    findings = result.get("findings", [])
    if findings:
        st.write("")
        for finding in findings:
            status = finding.get("status", "review")
            label = finding.get("label", finding.get("field", "Field"))
            message = finding.get("message", "")
            if status == "detected": st.success(f"✓ **{label}:** {message}")
            elif status == "missing": st.warning(f"⚠ **{label}:** {message}")
            else: st.info(f"ℹ **{label}:** {message}")

def consumer_page():
    render_topbar()
    if st.button("← Back to Home", key="back_home"):
        st.session_state.page="home"; st.session_state.consumer_scan_started=False; st.session_state.evidence_files=[]; st.rerun()
    st.markdown('<div style="margin-top:15px;"><div class="hero-badge">CONSUMER VERIFICATION</div><h1 style="margin-top:12px;">📦 Scan a Package</h1><p style="color:#64748b;">Capture clear package evidence before checking mandatory product declarations.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">📸 Capture Package Evidence</div><div class="section-line"></div>', unsafe_allow_html=True)
    camera_col, upload_col = st.columns(2, gap="large")
    with camera_col:
        st.markdown('<div class="card"><div class="card-icon">📷</div><div class="card-title">Take a Photo</div><div class="card-text">Capture a clear photograph of the package.</div></div>', unsafe_allow_html=True)
        camera_photo = st.camera_input("Capture package", key="package_camera")
    with upload_col:
        st.markdown('<div class="card"><div class="card-icon">📁</div><div class="card-title">Upload Images</div><div class="card-text">Upload one or more package photographs. Multiple views can improve evidence coverage.</div></div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Upload package photographs", type=["jpg","jpeg","png"], accept_multiple_files=True, key="consumer_package_upload")
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
    st.markdown('<div class="section-heading">🧠 Package Analysis</div><div class="section-line"></div>', unsafe_allow_html=True)
    with st.spinner("Reading package text with OCR..."):
        ocr_results = []
        for image_file in evidence_files:
            ocr_results.extend(
                extract_text(
                    Image.open(
                        BytesIO(image_file.getvalue())
                    ).convert("RGB")
                )
            )

    st.success(
        f"EasyOCR completed — {len(ocr_results)} evidence elements detected."
    )
    declarations=extract_declarations(ocr_results)
    compliance_result=check_compliance(declarations)
    render_declarations(declarations)

    # Development diagnostic: proves what the extraction layer actually
    # receives from services/ocr.py. Remove or hide for final deployment.
    with st.expander("🧪 OCR Engine Debug (Development)"):
        for i, item in enumerate(ocr_results):
            st.write(
                f"{i + 1}. {item.get('text', '')} | "
                f"confidence={item.get('confidence', 0):.3f} | "
                f"source={item.get('source', 'unknown')}"
            )
    render_compliance(compliance_result)
    st.markdown('<div class="section-heading">🔎 OCR Evidence</div><div class="section-line"></div>', unsafe_allow_html=True)
    with st.expander("View Raw OCR Text"):
        raw_text=declarations.get("raw_text",[])
        if raw_text:
            for text in raw_text: st.write(f"• {text}")
        else: st.caption("No readable text detected.")
    st.markdown('<div class="footer">OCR → Declaration Extraction → Compliance Review</div>', unsafe_allow_html=True)

if st.session_state.page == "home": home_page()
else: consumer_page()
