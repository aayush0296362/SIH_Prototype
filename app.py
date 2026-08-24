import textwrap
from abc import ABC, abstractmethod
from services.extraction import extract_declarations
from services.ocr import extract_text
import easyocr
import numpy as np
import streamlit as st
from PIL import Image
from io import BytesIO


# ---------------- OCR ENGINE ----------------

@st.cache_resource
def get_ocr_reader():
    return easyocr.Reader(
        ["en"],
        gpu=False
    )


# ---------------- OCR EXTRACTION ----------------

def extract_text(image_file):
    """
    Extract readable text from a package image.
    """

    image_bytes = image_file.getvalue()

    image = Image.open(
        BytesIO(image_bytes)
    ).convert("RGB")

    image_array = np.array(image)

    reader = get_ocr_reader()

    results = reader.readtext(
        image_array,
        detail=1
    )

    extracted = []

    for result in results:

        text = result[1]
        confidence = result[2]

        if confidence >= 0.30:

            extracted.append({
                "text": text,
                "confidence": round(
                    float(confidence),
                    3
                )
            })

    return extracted


# ---------------- INSPECTION PIPELINE ----------------

class Pipeline(ABC):
    """Abstract inspection pipeline for package compliance checks."""

    def __init__(self, name: str = "inspection_pipeline"):
        self.name = name

    @abstractmethod
    def detect_package(self, image):
        """Identify the package region(s) within an image."""
        raise NotImplementedError

    @abstractmethod
    def extract_declarations(
        self,
        image,
        package_region=None
    ):
        """Extract product declarations from the package region."""
        raise NotImplementedError

    @abstractmethod
    def apply_rules(self, declarations):
        """Compare declarations against legal metrology rules."""
        raise NotImplementedError

    @abstractmethod
    def create_evidence(
        self,
        image_name,
        package_region,
        declarations,
        findings
    ):
        """Create a structured evidence record for later review."""
        raise NotImplementedError

    def run(self, images):
        """Run the complete package compliance workflow."""

        results = []

        for image in images:

            package_region = self.detect_package(
                image
            )

            declarations = self.extract_declarations(
                image,
                package_region
            )

            findings = self.apply_rules(
                declarations
            )

            evidence = self.create_evidence(
                image_name=getattr(
                    image,
                    "name",
                    "uploaded_image"
                ),
                package_region=package_region,
                declarations=declarations,
                findings=findings
            )

            results.append(evidence)

        return {
            "pipeline": self.name,
            "results": results,
            "total_images": len(results),
            "passed": sum(
                1
                for item in results
                if item.get("status") == "pass"
            ),
            "failed": sum(
                1
                for item in results
                if item.get("status") == "fail"
            ),
        }


class CompliancePipeline(Pipeline):
    """Concrete implementation used by the app to approximate OCR + rule checks."""

    def detect_package(self, image):
        return {
            "label": "primary_package_region",
            "image_name": getattr(image, "name", "uploaded_image"),
            "confidence": 0.96,
        }

    def extract_declarations(self, image, package_region=None):
        text = getattr(image, "name", "uploaded_image").lower()
        labels = {
            "product_name": "sample product",
            "net_content": "500 g",
            "batch_code": "BATCH-2024-07",
            "manufacturer": "demo manufacturer",
            "source_text": text,
        }
        return labels

    def apply_rules(self, declarations):
        findings = []

        if declarations.get("net_content"):
            findings.append({
                "rule": "net_content_present",
                "status": "pass",
                "message": "Mandatory net content declaration found.",
            })
        else:
            findings.append({
                "rule": "net_content_present",
                "status": "fail",
                "message": "Net content declaration missing.",
            })

        if declarations.get("manufacturer"):
            findings.append({
                "rule": "manufacturer_present",
                "status": "pass",
                "message": "Manufacturer information available.",
            })
        else:
            findings.append({
                "rule": "manufacturer_present",
                "status": "fail",
                "message": "Manufacturer information missing.",
            })

        return {
            "status": "pass" if all(item["status"] == "pass" for item in findings) else "fail",
            "findings": findings,
        }

    def create_evidence(self, image_name, package_region, declarations, findings):
        return {
            "image_name": image_name,
            "package_region": package_region,
            "declarations": declarations,
            "findings": findings["findings"],
            "status": findings["status"],
            "summary": (
                "Compliance check completed successfully."
                if findings["status"] == "pass"
                else "Manual review recommended due to failed checks."
            ),
        }


# A ready-to-use concrete pipeline for the app.
inspection_pipeline = CompliancePipeline("inspection_pipeline")

st.set_page_config(
    page_title="Package Compliance Scanner",
    page_icon="📦",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "consumer_scan_started" not in st.session_state:
    st.session_state.consumer_scan_started = False

# ---------------- HOME PAGE ----------------

def home_page():

    # ==================== PAGE CSS ====================

    st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(37,99,235,0.16), transparent 30%),
        radial-gradient(circle at 90% 15%, rgba(14,165,233,0.10), transparent 28%),
        #080d18;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* NAVBAR */
.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 5px 25px 5px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 60px;
}

.brand {
    font-size: 25px;
    font-weight: 800;
    color: #f8fafc;
}

.brand span {
    color: #38bdf8;
}

.brand-small {
    display: block;
    color: #64748b;
    font-size: 9px;
    letter-spacing: 2px;
    margin-top: 5px;
}

.nav-status {
    padding: 9px 16px;
    border-radius: 30px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.10);
    color: #94a3b8;
    font-size: 13px;
}

.status-dot {
    color: #22c55e;
    margin-right: 6px;
}

/* HERO */
.hero {
    text-align: center;
    margin-bottom: 45px;
}

.hero-badge {
    display: inline-block;
    padding: 7px 15px;
    border-radius: 30px;
    background: rgba(56,189,248,0.10);
    border: 1px solid rgba(56,189,248,0.25);
    color: #7dd3fc;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 20px;
}

.hero-title {
    color: #f8fafc;
    font-size: 58px;
    font-weight: 850;
    line-height: 1.05;
    letter-spacing: -2px;
}

.highlight {
    background: linear-gradient(90deg, #38bdf8, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    max-width: 720px;
    margin: 20px auto;
    color: #94a3b8;
    font-size: 17px;
    line-height: 1.7;
}

/* ACTION CARDS */
.action-card {
    padding: 28px;
    min-height: 165px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.09);
    background: rgba(255,255,255,0.035);
    transition: 0.25s ease;
}

.action-card:hover {
    transform: translateY(-5px);
    border-color: rgba(56,189,248,0.45);
    background: rgba(56,189,248,0.06);
}

.action-icon {
    font-size: 30px;
    margin-bottom: 10px;
}

.action-title {
    color: #f8fafc;
    font-size: 22px;
    font-weight: 750;
}

.action-text {
    color: #94a3b8;
    font-size: 14px;
    line-height: 1.5;
    margin-top: 7px;
}

/* BUTTONS */
div.stButton > button {
    border-radius: 11px;
    min-height: 46px;
    font-weight: 700;
    transition: 0.2s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px);
}

/* FEATURES */
.section-label {
    text-align: center;
    color: #64748b;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    margin: 55px 0 20px 0;
}

.feature {
    text-align: center;
    padding: 15px 5px;
}

.feature-icon {
    font-size: 25px;
    margin-bottom: 8px;
}

.feature-title {
    color: #e2e8f0;
    font-size: 14px;
    font-weight: 700;
}

.feature-text {
    color: #64748b;
    font-size: 12px;
    margin-top: 4px;
}

/* WORKFLOW */
.workflow {
    margin-top: 35px;
    padding: 28px;
    border-radius: 20px;
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
}

.workflow-title {
    text-align: center;
    color: #f8fafc;
    font-size: 20px;
    font-weight: 750;
    margin-bottom: 25px;
}

.step {
    text-align: center;
}

.step-number {
    color: #38bdf8;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
}

.step-title {
    color: #e2e8f0;
    font-size: 14px;
    font-weight: 700;
    margin-top: 7px;
}

.step-text {
    color: #64748b;
    font-size: 12px;
    margin-top: 5px;
}

/* FOOTER */
.footer {
    text-align: center;
    color: #475569;
    font-size: 12px;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.06);
}
</style>
""", unsafe_allow_html=True)


    # ==================== NAVBAR ====================

    st.markdown("""
<div class="topbar">
<div class="brand">
📦 LM<span>SCAN</span>
<span class="brand-small">LEGAL METROLOGY INTELLIGENCE</span>
</div>
<div class="nav-status">
<span class="status-dot">●</span> AI Inspection Platform
</div>
</div>
""", unsafe_allow_html=True)


    # ==================== HERO ====================

    st.markdown("""
<div class="hero">
<div class="hero-badge">AI-ASSISTED COMPLIANCE</div>
<div class="hero-title">Smarter Package<br><span class="highlight">Compliance Intelligence</span></div>
<div class="hero-subtitle">
Verify packaged-product declarations with AI-assisted inspection,
evidence-linked findings and transparent human verification.
</div>
</div>
""", unsafe_allow_html=True)


    # ==================== ACTION CARDS ====================

    col1, col2 = st.columns(2, gap="large")

    with col1:

        st.markdown("""
<div class="action-card">
<div class="action-icon">📸</div>
<div class="action-title">Scan a Package</div>
<div class="action-text">
Capture or upload a packaged product and check its visible
declarations using AI-assisted analysis.
</div>
</div>
""", unsafe_allow_html=True)

        st.write("")

        if st.button(
            "Start Package Scan  →",
            key="consumer_btn",
            type="primary",
        ):
            st.session_state.page = "consumer"
            st.rerun()


    with col2:

        st.markdown("""
<div class="action-card">
<div class="action-icon">🛡️</div>
<div class="action-title">Inspector Portal</div>
<div class="action-text">
Access inspection workflows, compliance intelligence,
evidence and enforcement analytics.
</div>
</div>
""", unsafe_allow_html=True)

        st.write("")

        if st.button(
            "Open Inspector Portal  →",
            key="inspector_btn",

        ):
            st.session_state.page = "login"
            st.rerun()


    # ==================== FEATURES ====================

    st.markdown(
        '<div class="section-label">BUILT FOR EVIDENCE-BASED INSPECTION</div>',
        unsafe_allow_html=True
    )

    f1, f2, f3, f4, f5 = st.columns(5)

    features = [
        ("🔎", "AI OCR", "Extract package text"),
        ("📦", "Multi-Side", "Inspect multiple views"),
        ("⚖️", "Rule Engine", "Structured compliance"),
        ("🔐", "Evidence", "Integrity-aware records"),
        ("🔳", "QR Verify", "Verify inspection records")
    ]

    for col, (icon, title, description) in zip(
        [f1, f2, f3, f4, f5],
        features
    ):
        with col:

            st.markdown(f"""
<div class="feature">
<div class="feature-icon">{icon}</div>
<div class="feature-title">{title}</div>
<div class="feature-text">{description}</div>
</div>
""", unsafe_allow_html=True)


    # ==================== WORKFLOW ====================

    st.markdown("""
<div class="workflow">
<div class="workflow-title">How the inspection works</div>
</div>
""", unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)

    steps = [
        ("01", "Capture", "Package images"),
        ("02", "Analyze", "AI + OCR extraction"),
        ("03", "Verify", "Human review"),
        ("04", "Record", "Evidence + QR")
    ]

    for col, (number, title, description) in zip(
        [s1, s2, s3, s4],
        steps
    ):
        with col:

            st.markdown(f"""
<div class="step">
<div class="step-number">{number}</div>
<div class="step-title">{title}</div>
<div class="step-text">{description}</div>
</div>
""", unsafe_allow_html=True)


    # ==================== FOOTER ====================

    st.markdown("""
<div class="footer">
AI-assisted • Human verified • Evidence linked
<br><br>
SIH26034 — Legal Metrology Package Compliance Scanner
</div>
""", unsafe_allow_html=True)

# ---------------- CONSUMER PAGE ----------------
# ---------------- CONSUMER PAGE ----------------

def consumer_page():

    # ==================== CSS ====================

    st.markdown("""
<style>

.scan-header {
    padding: 10px 0 25px 0;
}

.scan-badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    background: rgba(56,189,248,0.10);
    border: 1px solid rgba(56,189,248,0.25);
    color: #7dd3fc;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}

.scan-title {
    color: #f8fafc;
    font-size: 38px;
    font-weight: 800;
    margin-top: 10px;
}

.scan-subtitle {
    color: #94a3b8;
    font-size: 15px;
    margin-top: 5px;
}

.upload-panel {
    padding: 28px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.09);
    background: rgba(255,255,255,0.035);
    margin-top: 20px;
}

.panel-title {
    color: #f8fafc;
    font-size: 20px;
    font-weight: 750;
}

.panel-text {
    color: #64748b;
    font-size: 13px;
    margin-top: 5px;
}

.capture-card {
    padding: 16px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.025);
    text-align: center;
}

.capture-icon {
    font-size: 25px;
}

.capture-title {
    color: #e2e8f0;
    font-size: 13px;
    font-weight: 700;
    margin-top: 5px;
}

.capture-text {
    color: #64748b;
    font-size: 11px;
    margin-top: 4px;
}

.preview-panel {
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.025);
    margin-top: 25px;
}

.preview-title {
    color: #f8fafc;
    font-size: 18px;
    font-weight: 750;
}

.status-ready {
    color: #22c55e;
    font-size: 13px;
    font-weight: 700;
}

.analysis-panel {
    padding: 24px;
    border-radius: 18px;
    border: 1px solid rgba(56,189,248,0.20);
    background: rgba(56,189,248,0.04);
    margin-top: 25px;
}

.analysis-title {
    color: #f8fafc;
    font-size: 19px;
    font-weight: 750;
}

.pipeline-step {
    padding: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}

.pipeline-number {
    color: #38bdf8;
    font-size: 11px;
    font-weight: 800;
}

.pipeline-name {
    color: #e2e8f0;
    font-size: 14px;
    font-weight: 700;
}

.pipeline-description {
    color: #64748b;
    font-size: 11px;
}

</style>
""", unsafe_allow_html=True)


    # ==================== BACK ====================

    if st.button("← Back to Home", key="consumer_back"):
        st.session_state.page = "home"
        st.session_state.consumer_scan_started = False
        st.rerun()


    # ==================== HEADER ====================

    st.markdown("""
<div class="scan-header">

<div class="scan-badge">
CONSUMER VERIFICATION
</div>

<div class="scan-title">
📦 Scan a Package
</div>

<div class="scan-subtitle">
Capture package evidence before checking mandatory declarations.
</div>

</div>
""", unsafe_allow_html=True)


    # ==================== UPLOAD PANEL ====================

    st.markdown("""
<div class="upload-panel">

<div class="panel-title">
📸 Capture Package Evidence
</div>

<div class="panel-text">
Upload clear photographs of the package. Multiple views improve
the ability to verify declarations.
</div>

</div>
""", unsafe_allow_html=True)


       # ==================== PACKAGE EVIDENCE ====================

    cam_col, upload_col = st.columns(2)

    with cam_col:

        st.markdown("""
        <div class="capture-source">
            <div class="source-icon">📷</div>
            <div class="source-title">Take a Photo</div>
            <div class="source-text">
                Use your device camera to capture the package.
            </div>
        </div>
        """, unsafe_allow_html=True)

        camera_photo = st.camera_input(
            "Capture package",
            key="package_camera",
            resolution="1080p",
            width=420
        )

    with upload_col:

        st.markdown("""
        <div class="capture-source">
            <div class="source-icon">📁</div>
            <div class="source-title">Upload Image</div>
            <div class="source-text">
                Select an existing package photograph.
            </div>
        </div>
        """, unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Upload package photographs",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="consumer_package_upload"
        )
    # ==================== COMBINE EVIDENCE ====================

    evidence_files = []

    if camera_photo is not None:
        evidence_files.append(camera_photo)

    if uploaded_files:
        evidence_files.extend(uploaded_files)

    # Preserve the uploaded evidence when the Analyze button causes a rerun.
    st.session_state.evidence_files = evidence_files

    # ==================== PREVIEW ====================

    if evidence_files:

        st.markdown("""
<div class="preview-panel">

<div class="preview-title">
📋 Evidence Review
</div>

</div>
""", unsafe_allow_html=True)

        st.success(
            f"{len(evidence_files)} image"
            f"{'s' if len(evidence_files) != 1 else ''} captured"
        )

        preview_columns = st.columns(
            min(len(evidence_files), 4)
        )

        for index, uploaded_file in enumerate(evidence_files):

            with preview_columns[index % len(preview_columns)]:

                st.image(
                    uploaded_file,
                    caption=uploaded_file.name,
                    width=180
                )

    st.markdown("""
<div class="status-ready">
● Evidence ready for analysis
</div>
""", unsafe_allow_html=True)

    st.write("")

    if st.button(
        "🔍 Analyze Package",
        type="primary",
        key="analyze_package"
    ):

        st.session_state.consumer_scan_started = True
        st.rerun()

    # ==================== OCR ANALYSIS ====================

    if st.session_state.get(
        "consumer_scan_started",
        False
    ):

        st.markdown("## 🧠 Package Analysis")

        st.caption(
            "Reading package evidence and extracting visible declarations."
        )

        if not evidence_files:

            st.warning(
                "Please capture or upload a package image first."
            )

        else:

            # ==================== OCR ====================

            with st.spinner(
                "🔍 Reading package text..."
            ):

                ocr_results = []

                for image_file in evidence_files:

                    results = extract_text(
                        image_file
                    )

                    ocr_results.extend(
                        results
                    )

            # ==================== EXTRACTION ====================

            declarations = extract_declarations(
                ocr_results
            )
           

            # ==================== RESULTS ====================

            st.success(
                f"OCR completed — "
                f"{len(ocr_results)} text elements detected."
            )

            st.markdown(
                "### 📋 Detected Declarations"
            )

    # ==================== ANALYSIS ====================

    if st.session_state.get(
        "consumer_scan_started",
        False
    ):

        evidence_files = st.session_state.get(
            "evidence_files",
            []
        )

        st.markdown(
            "## 🧠 Package Analysis"
        )

        st.caption(
            "Analyzing package evidence and extracting visible declarations."
        )

        if not evidence_files:

            st.warning(
                "Please capture or upload a package image first."
            )

        else:

            # ==================== OCR ====================

            with st.spinner(
                "🔍 Reading package text..."
            ):

                reader = get_ocr_reader()

                ocr_results = []

                for evidence in evidence_files:

                    image_bytes = evidence.getvalue()

                    image = Image.open(
                        BytesIO(image_bytes)
                    ).convert("RGB")

                    image_array = np.array(
                        image
                    )

                    results = reader.readtext(
                        image_array,
                        detail=1
                    )

                    for result in results:

                        text = result[1]

                        confidence = float(
                            result[2]
                        )

                        if confidence >= 0.30:

                            ocr_results.append(
                                {
                                    "text": text,
                                    "confidence": confidence
                                }
                            )


            # ==================== OCR STATUS ====================

            st.success(
                f"✅ OCR completed — "
                f"{len(ocr_results)} text elements detected."
            )


            # ==================== EXTRACTION ====================

            declarations = extract_declarations(
                ocr_results
            )


            # ==================== PACKAGE INFORMATION ====================

            st.markdown(
                "## 📋 Package Information"
            )

            fields = [
                (
                    "product_name",
                    "Product Name",
                    "📦"
                ),
                (
                    "mrp",
                    "MRP",
                    "💰"
                ),
                (
                    "net_quantity",
                    "Net Quantity",
                    "⚖️"
                ),
                (
                    "manufacturer",
                    "Manufacturer",
                    "🏭"
                ),
                (
                    "manufacturing_date",
                    "Manufacturing Date",
                    "📅"
                ),
                (
                    "expiry_date",
                    "Expiry Date",
                    "⏳"
                ),
                (
                    "best_before",
                    "Best Before",
                    "🕒"
                ),
                (
                    "consumer_care",
                    "Consumer Care",
                    "📞"
                ),
                (
                    "country_of_origin",
                    "Country of Origin",
                    "🇮🇳"
                ),
                (
                    "batch_number",
                    "Batch Number",
                    "🔢"
                )
            ]


            for field, label, icon in fields:

                value = declarations.get(
                    field
                )

                col1, col2, col3 = st.columns(
                    [0.08, 0.35, 0.57]
                )

                with col1:

                    st.markdown(
                        f"""
                        <div style="
                            font-size:22px;
                            text-align:center;
                        ">
                            {icon}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:

                    st.markdown(
                        f"**{label}**"
                    )

                with col3:

                    if value:

                        st.success(
                            str(value)
                        )

                    else:

                        st.caption(
                            "Not detected in provided evidence"
                        )


            # ==================== RAW OCR ====================

            st.write("")

            with st.expander(
                "🔍 View Raw OCR Text"
            ):

                raw_text = declarations.get(
                    "raw_text",
                    []
                )

                if raw_text:

                    for text in raw_text:

                        st.write(
                            f"• {text}"
                        )

                else:

                    st.caption(
                        "No readable text detected."
                    )

        # ---------------- OCR RESULT ----------------

        st.success(
            f"OCR completed — {len(all_text)} text elements detected."
        )

        st.markdown("### 📝 Extracted Package Text")

        if all_text:

            extracted_text = "\n".join(
                f"• {text}"
                for text in all_text
            )

            st.text_area(
                "Detected text",
                extracted_text,
                height=300
            )

        else:

            st.warning(
                "No readable text was detected. "
                "Try a clearer or better-lit package image."
            )

    # ---------------- PAGE ROUTING ----------------

if st.session_state.page == "home":
    home_page()

elif st.session_state.page == "consumer":
    consumer_page()