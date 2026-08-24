import streamlit as st

st.set_page_config(
    page_title="Package Compliance Scanner",
    page_icon="📦",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"


# ---------------- HOME PAGE ----------------
def home_page():

    # Custom CSS
    st.markdown("""
    <style>

    /* Main heading */
    .main-title {
        text-align: center;
        font-size: 48px;
        font-weight: 700;
        color: #1f2937;
        margin-top: 40px;
        margin-bottom: 8px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #6b7280;
        margin-bottom: 45px;
    }

    /* Cards */
    .mode-card {
        border: 1px solid #d1d5db;
        border-radius: 18px;
        padding: 35px 30px;
        min-height: 310px;
        background-color: #ffffff;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        transition: 0.3s;
    }

    .mode-card:hover {
        border-color: #2563eb;
        box-shadow: 0 8px 25px rgba(37,99,235,0.15);
    }

    .card-icon {
        font-size: 45px;
        margin-bottom: 10px;
    }

    .card-title {
        font-size: 28px;
        font-weight: 650;
        color: #1f2937;
        margin-bottom: 15px;
    }

    .card-text {
        font-size: 17px;
        color: #6b7280;
        line-height: 1.6;
    }

    /* Buttons */
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 48px;
        font-size: 16px;
        font-weight: 600;
        border: none;
        background-color: #2563eb;
        color: white;
    }

    div.stButton > button:hover {
        background-color: #1d4ed8;
        color: white;
    }

    </style>
    """, unsafe_allow_html=True)


    # Header
    st.markdown(
        '<div class="main-title">📦 Package Compliance Scanner</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Smart Legal Metrology Compliance Intelligence Platform</div>',
        unsafe_allow_html=True
    )


    # Two columns
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="mode-card">
            <div class="card-icon">👤</div>
            <div class="card-title">Consumer</div>
            <div class="card-text">
                Scan a packaged product and instantly check whether
                essential mandatory information is present on its label.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        if st.button("Scan a Product →", key="consumer_btn"):
            st.session_state.page = "consumer"
            st.rerun()


    with col2:
        st.markdown("""
        <div class="mode-card">
            <div class="card-icon">🛡️</div>
            <div class="card-title">Inspector</div>
            <div class="card-text">
                Access compliance insights, inspection data and
                identify areas that require greater enforcement attention.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        if st.button("Inspector Login →", key="inspector_btn"):
            st.session_state.page = "login"
            st.rerun()


    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown(
        "<p style='text-align:center; color:#9ca3af;'>"
        "Powered by AI • OCR • Risk-Based Compliance Intelligence"
        "</p>",
        unsafe_allow_html=True
    )


# ---------------- CONSUMER PAGE ----------------
def consumer_page():
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.title("👤 Consumer Product Check")
    st.write("Upload a packaged product image to verify its mandatory label information.")

    uploaded_file = st.file_uploader(
        "Upload Product Image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:
        st.success("Image uploaded successfully! Scanner module will analyze the package details.")
        st.image(uploaded_file, caption="Product Image", width=400)

        if st.button("🔍 Scan Package", type="primary"):
            st.info("Scanning module coming next — we'll connect our working OCR here! 🚀")


# ---------------- INSPECTOR LOGIN ----------------
def login_page():
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.title("🛡️ Inspector Access")
    st.write("Enter your credentials to access the enforcement dashboard.")

    inspector_id = st.text_input("Inspector ID")
    password = st.text_input("Password", type="password")

    if st.button("Access Dashboard", type="primary"):
        # Demo authentication for prototype
        if inspector_id == "INS001" and password == "demo123":
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("Invalid credentials. For demo use: INS001 / demo123")


# ---------------- INSPECTOR DASHBOARD ----------------
# ---------------- INSPECTOR DASHBOARD ----------------
def dashboard_page():

    st.markdown("""
    <style>

    .dashboard-header {
        padding: 10px 0 20px 0;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 25px;
    }

    .dashboard-title {
        font-size: 34px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 5px;
    }

    .dashboard-subtitle {
        color: #6b7280;
        font-size: 16px;
    }

    .metric-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.04);
        text-align: center;
    }

    .metric-number {
        font-size: 30px;
        font-weight: 700;
        color: #2563eb;
    }

    .metric-label {
        font-size: 14px;
        color: #6b7280;
        margin-top: 5px;
    }

    .section-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 20px;
        margin-top: 15px;
    }

    </style>
    """, unsafe_allow_html=True)

    # Top section
    left, right = st.columns([6, 1])

    with left:
        st.markdown("""
        <div class="dashboard-header">
            <div class="dashboard-title">🛡️ Inspector Dashboard</div>
            <div class="dashboard-subtitle">
                Compliance intelligence and enforcement monitoring overview
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        if st.button("Logout"):
            st.session_state.page = "home"
            st.rerun()

    # Metric cards
    st.markdown("### Compliance Overview")

    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        ("1,248", "Products Scanned"),
        ("892", "Compliant Products"),
        ("356", "Violations Found"),
        ("4", "High-Risk Areas")
    ]

    for col, (number, label) in zip([c1, c2, c3, c4], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{number}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Analytics section
    left_col, right_col = st.columns([1.3, 1])

    with left_col:
        st.markdown("### 📊 Violation Analysis")

        chart_data = {
            "Violation Type": [
                "Missing MRP",
                "Net Quantity",
                "Manufacturer Info",
                "Consumer Care"
            ],
            "Cases": [86, 64, 42, 31]
        }

        st.bar_chart(
            chart_data,
            x="Violation Type",
            y="Cases"
        )

    with right_col:
        st.markdown("### 📍 Area-wise Risk Monitoring")

        st.markdown("""
        <div class="section-card">
            🔴 <b>Delhi</b> — High Risk<br>
            <span style="color:#6b7280;">Frequent declaration violations detected</span>
        </div>

        <div class="section-card">
            🟡 <b>Chandigarh</b> — Medium Risk<br>
            <span style="color:#6b7280;">Moderate compliance issues observed</span>
        </div>

        <div class="section-card">
            🟢 <b>Mohali</b> — Low Risk<br>
            <span style="color:#6b7280;">Higher overall compliance rate</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Recent inspections
    st.markdown("### 📋 Recent Inspection Records")

    inspection_data = {
        "Product": ["ABC Biscuits", "Fresh Oil", "Healthy Snacks", "Daily Essentials"],
        "Location": ["Delhi", "Mohali", "Chandigarh", "Delhi"],
        "Status": ["Non-Compliant", "Compliant", "Under Review", "Non-Compliant"]
    }

    st.dataframe(
        inspection_data,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Main action
    if st.button("📸 Start New Inspection", type="primary"):
       st.session_state.page = "inspection"
       st.rerun()

    # ---------------- INSPECTOR PRODUCT INSPECTION ----------------
def inspection_page():

    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.title("🛡️ New Product Inspection")

    st.write(
        "Upload a packaged commodity image to perform an official compliance inspection."
    )

    st.divider()

    # Inspection details
    st.subheader("📋 Inspection Details")

    col1, col2 = st.columns(2)

    with col1:
        location = st.text_input(
            "Inspection Location",
            placeholder="e.g. Mohali, Punjab"
        )

    with col2:
        inspection_type = st.selectbox(
            "Inspection Type",
            [
                "Routine Inspection",
                "Complaint-Based Inspection",
                "Special Inspection"
            ]
        )

    st.subheader("📸 Product Package Scan")

    uploaded_file = st.file_uploader(
        "Upload Product Image",
        type=["jpg", "jpeg", "png"],
        key="inspector_upload"
    )

    if uploaded_file:

        st.image(
            uploaded_file,
            caption="Product Selected for Inspection",
            width=450
        )

        st.success("Product image uploaded successfully!")

        if st.button("🔍 Analyze Package Compliance", type="primary"):

            st.info("🔄 Analyzing mandatory declarations...")

            # Demo prototype result for now
            st.success("Analysis Completed!")

            st.subheader("📊 Compliance Result")

            st.warning("⚠️ Non-Compliant Package Detected")

            st.write("### Issues Identified:")

            issues = [
                "❌ Manufacturer address not clearly detected",
                "❌ Consumer care information missing",
                "⚠️ MRP declaration requires verification"
            ]

            for issue in issues:
                st.write(issue)

            st.divider()

            st.subheader("💡 Corrective Assistance")

            st.info("""
            The manufacturer/packer should ensure that all mandatory
            declarations required under the Legal Metrology
            (Packaged Commodities) Rules are clearly displayed.
            """)

            st.button("📄 Generate Inspection Report")

# ---------------- ROUTING ----------------
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "consumer":
    consumer_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.page == "dashboard":
    dashboard_page()
elif st.session_state.page == "inspection":
    inspection_page()