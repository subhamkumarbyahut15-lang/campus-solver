import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Initialize env vars. 
# TODO: Move ADMIN_KEY to AWS Secrets Manager before deploying to production.
load_dotenv()

API_GATEWAY = os.getenv("BACKEND_URL", "http://localhost:8000")
ADMIN_KEY = os.getenv("ADMIN_KEY", "admin_secure_2024")

# Standardized institutional categories
CATEGORY_MAPPING = {
    "Facilities & Infrastructure": "🏗️",
    "Sanitation & Housekeeping":   "🧹",
    "Dining & Mess Services":      "🍛",
    "Academic & IT Support":       "💻",
    "Safety & Security":           "🛡️",
    "General Grievance":           "📝",
}

STATUS_INDICATORS = {
    "Pending":     "🔵",
    "Under Review":"🟡",
    "Resolved":    "🟢",
    "Dismissed":   "🔴",
}

# ── App Configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CampusOps | Grievance Redressal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium, clean UI override (resembling enterprise tools like Linear or Vercel)
st.markdown("""
<style>
    /* Base spacing and typography */
    .block-container { padding-top: 2rem; max-width: 1200px; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -0.02em; }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] { background-color: #FAFAFA; border-right: 1px solid #EAEAEA; }
    
    /* Data Cards */
    .ticket-card {
        background-color: #FFFFFF;
        border: 1px solid #E4E4E7;
        border-radius: 6px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        transition: box-shadow 0.2s ease;
    }
    .ticket-card:hover { box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); }
    
    /* Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .status-pending { background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
    .status-review  { background-color: #FEF3C7; color: #B45309; border: 1px solid #FDE68A; }
    .status-resolved{ background-color: #F0FDF4; color: #15803D; border: 1px solid #BBF7D0; }
    .status-dismiss { background-color: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
    
    /* Data Viz / Confidence Bar */
    .metric-bar-bg {
        background-color: #F4F4F5;
        border-radius: 4px;
        height: 6px;
        width: 100%;
        margin-top: 6px;
        overflow: hidden;
    }
    .metric-bar-fill {
        height: 100%;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ── Service Layer ─────────────────────────────────────────────────────────────
class ApiClient:
    """Wrapper for backend communications to handle standard timeouts and errors."""
    @staticmethod
    def get(path: str, params: dict = None):
        try:
            res = requests.get(f"{API_GATEWAY}{path}", params=params, timeout=10)
            return res.json(), res.status_code
        except requests.exceptions.RequestException as e:
            return {"detail": "Service unavailable. Check API Gateway."}, 503

    @staticmethod
    def post(path: str, payload: dict):
        try:
            res = requests.post(f"{API_GATEWAY}{path}", json=payload, timeout=15)
            return res.json(), res.status_code
        except requests.exceptions.RequestException:
            return {"detail": "Service unavailable."}, 503

    @staticmethod
    def put(path: str, payload: dict):
        try:
            res = requests.put(f"{API_GATEWAY}{path}", json=payload, timeout=10)
            return res.json(), res.status_code
        except requests.exceptions.RequestException:
            return {"detail": "Service unavailable."}, 503

def render_confidence_metric(score: float):
    percentage = int(score * 100)
    color = "#10B981" if percentage >= 80 else "#F59E0B" if percentage >= 60 else "#EF4444"
    return f"""
    <div style='font-size:12px; color:#71717A; font-weight:500;'>Routing Confidence: {percentage}%</div>
    <div class='metric-bar-bg'>
        <div class='metric-bar-fill' style='width:{percentage}%; background-color:{color};'></div>
    </div>
    """

# ── Navigation ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏛️ CampusOps Portal")
    st.caption("Centralized Grievance Redressal")
    st.markdown("---")
    active_view = st.radio(
        "Navigation",
        ["Submit Ticket", "Check Status", "Management Console", "Analytics"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    # Silent health check
    health_data, status_code = ApiClient.get("/")
    if status_code == 200:
        st.markdown("<small style='color: #10B981;'>● System Operational</small>", unsafe_allow_html=True)
    else:
        st.markdown("<small style='color: #EF4444;'>● API Disconnected</small>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# VIEW 1: SUBMISSION FORM
# ══════════════════════════════════════════════════════════════════════════════
if active_view == "Submit Ticket":
    st.header("Open a Support Ticket")
    st.markdown("Provide detailed information regarding the issue. Our automated system will route it to the appropriate administrative department.")
    
    col_form, col_guidance = st.columns([2, 1], gap="large")

    with col_form:
        with st.form("ticket_submission", clear_on_submit=False):
            req_name = st.text_input("Complainant Name / ID *", placeholder="e.g., Vikram S. (Roll No. 2023014)")
            req_email = st.text_input("Official Email ID", placeholder="v.sharma@university.edu")
            req_desc = st.text_area(
                "Issue Description *",
                placeholder="Specify the exact location, time, and nature of the issue. e.g., 'The HVAC system in Lecture Hall C is malfunctioning, causing excessive noise during classes.'",
                height=180
            )
            
            is_submitted = st.form_submit_button("Submit Ticket", use_container_width=True)

        if is_submitted:
            if not req_name.strip() or len(req_desc.strip()) < 15:
                st.error("Validation Error: Please provide a valid identifier and a detailed description.")
            else:
                with st.spinner("Processing and routing..."):
                    payload = {
                        "student_name": req_name,
                        "student_email": req_email,
                        "description": req_desc,
                    }
                    data, code = ApiClient.post("/submit", payload)
                
                if code == 200:
                    st.success("Ticket successfully logged in the system.")
                    st.markdown(f"""
                    <div class='ticket-card'>
                        <h4 style='margin-top:0; color:#3F3F46;'>Ticket Reference ID</h4>
                        <h2 style='font-family:monospace; color:#09090B;'>{data['tracking_id']}</h2>
                        <hr style='border:none; border-top:1px solid #E4E4E7; margin: 16px 0;'>
                        <p style='margin:4px 0;'><b>Assigned Department:</b> {data['department']}</p>
                        <p style='margin:4px 0;'><b>Classification:</b> {CATEGORY_MAPPING.get(data['category'],'')} {data['category']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(render_confidence_metric(data['confidence']), unsafe_allow_html=True)
                else:
                    st.error(f"System Error: {data.get('detail', 'Failed to communicate with the routing engine.')}")

    with col_guidance:
        st.markdown("#### Submission Guidelines")
        st.markdown("""
        - **Be Specific:** Include room numbers, blocks, or landmarks.
        - **Maintain Protocol:** Use formal language; do not submit duplicates.
        - **Tracking:** Save your Reference ID. You will need it to check updates.
        """)
        st.divider()
        st.markdown("#### Operational Categories")
        for cat_name, cat_icon in CATEGORY_MAPPING.items():
            st.markdown(f"<div style='font-size: 14px; margin-bottom: 8px;'>{cat_icon} {cat_name}</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# VIEW 2: STATUS TRACKER
# ══════════════════════════════════════════════════════════════════════════════
elif active_view == "Check Status":
    st.header("Ticket Status Tracker")
    
    col_search, _ = st.columns([1, 1])
    with col_search:
        search_id = st.text_input("Enter Ticket Reference ID", placeholder="TKT-XXXX-XXXX").strip().upper()
        trigger_search = st.button("Retrieve Status")

    if trigger_search:
        if not search_id:
            st.warning("Please enter a valid Reference ID.")
        else:
            data, code = ApiClient.get(f"/track/{search_id}")

            if code == 200:
                status = data.get("status", "Pending")
                cat = data.get("category", "General Grievance")
                
                # Determine CSS class for the badge
                badge_class = {
                    "Pending": "status-pending",
                    "Under Review": "status-review",
                    "Resolved": "status-resolved",
                    "Dismissed": "status-dismiss"
                }.get(status, "status-pending")

                st.markdown(f"""
                <div style='margin-top: 24px;' class='ticket-card'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <h3 style='margin:0; font-family:monospace;'>{data['tracking_id']}</h3>
                        <span class='status-badge {badge_class}'>{STATUS_INDICATORS.get(status, '')} {status}</span>
                    </div>
                    <hr style='border:none; border-top:1px solid #E4E4E7; margin: 16px 0;'>
                    <div style='display:grid; grid-template-columns: 1fr 1fr; gap: 16px; font-size: 14px;'>
                        <div><b style='color:#71717A;'>Requester:</b> {data['student_name']}</div>
                        <div><b style='color:#71717A;'>Department:</b> {data.get('department','Unassigned')}</div>
                        <div><b style='color:#71717A;'>Category:</b> {cat}</div>
                        <div><b style='color:#71717A;'>Filed On:</b> {str(data.get('created_at',''))[:16].replace('T',' ')}</div>
                    </div>
                    <div style='margin-top: 20px; padding: 16px; background-color: #F8FAFC; border-radius: 6px; border: 1px solid #E2E8F0;'>
                        <b style='color:#475569; font-size: 12px; text-transform: uppercase;'>Original Description</b>
                        <p style='margin-top: 8px; font-size: 14px; color: #334155;'>{data.get('description', '')}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if data.get("resolution"):
                    st.markdown("#### Official Resolution Note")
                    st.info(data["resolution"], icon="📋")

            elif code == 404:
                st.error("Record not found. Please verify the Reference ID.")
            else:
                st.error("An error occurred while fetching the record.")


# ══════════════════════════════════════════════════════════════════════════════
# VIEW 3: MANAGEMENT CONSOLE
# ══════════════════════════════════════════════════════════════════════════════
elif active_view == "Management Console":
    st.header("Management Console")

    # Session-based Auth
    if not st.session_state.get("is_authenticated", False):
        st.info("Authentication required. Please enter administrative credentials.")
        pwd = st.text_input("Access Key", type="password")
        if st.button("Authenticate"):
            if pwd == ADMIN_KEY:
                st.session_state["is_authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid Access Key.")
        st.stop()

    col_btn, _ = st.columns([1, 5])
    with col_btn:
        if st.button("Terminate Session", use_container_width=True):
            st.session_state["is_authenticated"] = False
            st.rerun()

    st.markdown("---")

    # Data Filtering
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        f_status = st.selectbox("Status Filter", ["All", "Pending", "Under Review", "Resolved", "Dismissed"])
    with f_col2:
        f_dept = st.selectbox("Department Filter", [
            "All", "Estates & Maintenance", "Security Protocol",
            "Hostel Administration", "Academic Registry", "IT Services"
        ])

    params = {}
    if f_status != "All": params["status"] = f_status
    if f_dept != "All": params["department"] = f_dept

    data, code = ApiClient.get("/admin/problems", params=params)

    if code != 200:
        st.error("Failed to fetch administrative records.")
        st.stop()

    records = data.get("problems", [])
    
    if not records:
        st.markdown("<p style='color:#71717A; padding:20px 0;'>No records match the current filter criteria.</p>", unsafe_allow_html=True)
    else:
        st.caption(f"Showing {len(records)} active records.")
        for idx, row in enumerate(records):
            current_status = row.get("status", "Pending")
            
            with st.expander(f"{row['tracking_id']} | {row.get('department', 'Unassigned')} | {current_status.upper()}"):
                c_details, c_actions = st.columns([3, 2], gap="large")
                
                with c_details:
                    st.markdown(f"**Requester:** {row['student_name']} `({row.get('student_email', 'N/A')})`")
                    st.markdown(f"**Classification:** {row.get('category', 'General')}")
                    st.markdown(render_confidence_metric(row.get("confidence", 0.0)), unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown("**Description:**")
                    st.write(row.get("description", ""))
                    if row.get("resolution"):
                        st.markdown("**Prior Resolution Notes:**")
                        st.caption(row["resolution"])

                with c_actions:
                    new_state = st.selectbox(
                        "Update Status",
                        ["Pending", "Under Review", "Resolved", "Dismissed"],
                        index=["Pending", "Under Review", "Resolved", "Dismissed"].index(current_status),
                        key=f"st_{row['id']}"
                    )
                    note = st.text_area("Administrative Notes", value=row.get("resolution", ""), key=f"nt_{row['id']}")
                    
                    if st.button("Commit Changes", key=f"up_{row['id']}", type="primary"):
                        res, c = ApiClient.put(f"/admin/problem/{row['id']}", {
                            "status": new_state,
                            "resolution": note
                        })
                        if c == 200:
                            st.success("Record updated.")
                            st.rerun()
                        else:
                            st.error("Database commit failed.")


# ══════════════════════════════════════════════════════════════════════════════
# VIEW 4: ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif active_view == "Analytics":
    st.header("System Analytics & Telemetry")
    
    data, code = ApiClient.get("/admin/stats")
    if code != 200:
        st.error("Telemetry server unreachable.")
        st.stop()

    total = data.get("total", 0)
    b_status = data.get("by_status", {})
    b_dept = data.get("by_department", {})

    # Top-line metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Tickets Logged", total)
    m2.metric("Pending Triage", b_status.get("Pending", 0))
    m3.metric("Under Review", b_status.get("Under Review", 0))
    m4.metric("Successfully Resolved", b_status.get("Resolved", 0))

    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2, gap="large")

    with col_chart1:
        st.markdown("#### Department Load Distribution")
        if b_dept:
            for dept, count in sorted(b_dept.items(), key=lambda x: -x[1]):
                ratio = count / total if total else 0
                st.markdown(f"<div style='font-size:14px; margin-bottom:4px;'>{dept} <span style='float:right; color:#71717A;'>{count} tickets</span></div>", unsafe_allow_html=True)
                st.progress(ratio)
        else:
            st.caption("Insufficient data points.")

    with col_chart2:
        st.markdown("#### Resolution Efficiency")
        if b_status:
            for stat, count in b_status.items():
                ratio = count / total if total else 0
                st.markdown(f"<div style='font-size:14px; margin-bottom:4px;'>{stat} <span style='float:right; color:#71717A;'>{int(ratio*100)}%</span></div>", unsafe_allow_html=True)
                st.progress(ratio)
        else:
            st.caption("Insufficient data points.")