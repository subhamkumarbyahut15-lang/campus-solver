import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ADMIN_KEY = os.getenv("ADMIN_KEY", "admin123")

# ── App Configuration (No Sidebar) ────────────────────────────────────────────
st.set_page_config(
    page_title="Campus Command",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed" # Hides the sidebar for a web-app feel
)

# ── Complete UI Overhaul (CSS) ────────────────────────────────────────────────
st.markdown("""
<style>
    /* Hide standard Streamlit header/footer for a clean slate */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Pull content up to fill the empty header space */
    .block-container { padding-top: 1rem; max-width: 1200px; }

    /* Top Hero Section */
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        background: -webkit-linear-gradient(#60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle { color: #94a3b8; margin-top: 0.5rem; font-size: 1.1rem; }
    
    /* Glass Cards */
    .glass-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 10px 15px rgba(0, 0, 0, 0.03);
        border: 1px solid #f1f5f9;
        margin-bottom: 1rem;
    }
    
    /* Make tabs look like a modern segmented control */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8fafc;
        padding: 8px;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 8px;
        border: none !important;
        background-color: transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        color: #0f172a !important;
        font-weight: 600;
    }
    
    /* Custom Status Pills */
    .status-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 99px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .bg-blue { background: #dbeafe; color: #1e40af; }
    .bg-yellow { background: #fef3c7; color: #92400e; }
    .bg-green { background: #dcfce7; color: #166534; }
</style>
""", unsafe_allow_html=True)

# ── API Helpers ───────────────────────────────────────────────────────────────
def api_request(method, endpoint, payload=None, params=None):
    try:
        url = f"{BACKEND_URL}{endpoint}"
        if method == "GET":
            r = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            r = requests.post(url, json=payload, timeout=15)
        else:
            r = requests.put(url, json=payload, timeout=10)
        return r.json(), r.status_code
    except Exception as e:
        return {"detail": "Backend Offline"}, 503

# ── Top Hero Section (Information First) ──────────────────────────────────────
# Try to fetch global stats for the hero banner
stats_data, code = api_request("GET", "/admin/stats")
total_issues = stats_data.get("total", 0) if code == 200 else "--"
resolved_issues = stats_data.get("by_status", {}).get("Resolved", 0) if code == 200 else "--"

st.markdown(f"""
<div class="hero-container">
    <div>
        <h1 class="hero-title">Campus Command</h1>
        <div class="hero-subtitle">Unified Operations & Issue Tracking</div>
    </div>
    <div style="text-align: right;">
        <div style="color: #60a5fa; font-size: 0.9rem; text-transform: uppercase; font-weight: 700;">System Status: Online</div>
        <div style="color: #e2e8f0; margin-top: 8px;"><b>{total_issues}</b> Total Reports • <b>{resolved_issues}</b> Resolved</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Reactive Navigation (Tabs instead of pages) ───────────────────────────────
tab_report, tab_track, tab_insights, tab_admin = st.tabs([
    "🚀 Report Issue", 
    "🔍 Track Status", 
    "📊 Insights", 
    "⚙️ Admin Hub"
])

# ── TAB 1: Report Issue ───────────────────────────────────────────────────────
with tab_report:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("What needs attention?")
    
    col1, col2 = st.columns([2, 1], gap="large")
    with col1:
        with st.form("report_form", clear_on_submit=False):
            name = st.text_input("Your Name / ID")
            desc = st.text_area("Description of the problem", height=150)
            submitted = st.form_submit_button("Submit to System", type="primary", use_container_width=True)

        if submitted:
            if not name or len(desc) < 10:
                st.warning("Please provide a valid name and detailed description.")
            else:
                with st.spinner("Routing..."):
                    data, code = api_request("POST", "/submit", payload={"student_name": name, "description": desc})
                if code == 200:
                    st.success("Issue logged successfully.")
                    st.info(f"**Save your Tracking ID:** `{data['tracking_id']}`\n\nRouted to: **{data['department']}**")
                else:
                    st.error("Failed to submit issue.")
    with col2:
        st.markdown("#### Intelligent Routing")
        st.write("Our AI automatically analyzes your report and dispatches it to the correct department (Maintenance, IT, Security, etc.) instantly.")
    st.markdown("</div>", unsafe_allow_html=True)

# ── TAB 2: Track Status ───────────────────────────────────────────────────────
with tab_track:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Lookup")
        tracking_id = st.text_input("Enter Tracking ID").strip().upper()
        search = st.button("Check Status", use_container_width=True)
        
    with c2:
        if search and tracking_id:
            data, code = api_request("GET", f"/track/{tracking_id}")
            if code == 200:
                status = data.get("status", "Pending")
                color = {"Submitted": "bg-blue", "In Progress": "bg-yellow", "Resolved": "bg-green"}.get(status, "bg-blue")
                
                st.markdown(f"""
                <div style='background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0;'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'>
                        <h3 style='margin:0;'>{data['tracking_id']}</h3>
                        <span class='status-pill {color}'>{status}</span>
                    </div>
                    <b>Reported by:</b> {data['student_name']}<br>
                    <b>Assigned to:</b> {data.get('department', 'Pending')}<br>
                    <hr>
                    <p style='color: #475569;'>{data['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                if data.get("resolution"):
                    st.success(f"**Resolution Note:** {data['resolution']}")
            else:
                st.error("ID not found.")
    st.markdown("</div>", unsafe_allow_html=True)

# ── TAB 3: Insights ───────────────────────────────────────────────────────────
with tab_insights:
    if code != 200:
        st.info("System analytics are currently updating. Check back later.")
    else:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Department Workload")
            for dept, count in stats_data.get("by_department", {}).items():
                st.write(f"**{dept}**")
                st.progress(count / total_issues if total_issues else 0, text=str(count))
        with c2:
            st.subheader("Category Breakdown")
            for cat, count in stats_data.get("by_category", {}).items():
                st.write(f"**{cat}**")
                st.progress(count / total_issues if total_issues else 0, text=str(count))
        st.markdown("</div>", unsafe_allow_html=True)

# ── TAB 4: Admin Hub ──────────────────────────────────────────────────────────
# ── TAB 4: Admin Hub ──────────────────────────────────────────────────────────
# ── TAB 4: Admin Hub ──────────────────────────────────────────────────────────
with tab_admin:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    if not st.session_state.get("admin_auth"):
        st.subheader("Restricted Access")
        pwd = st.text_input("Administrator Password", type="password")
        if st.button("Unlock Terminal"):
            if pwd == ADMIN_KEY:
                st.session_state["admin_auth"] = True
                st.rerun()
            else:
                st.error("Access Denied.")
    else:
        st.success("Admin Terminal Active")
        if st.button("Lock Terminal"):
            st.session_state["admin_auth"] = False
            st.rerun()
        
        st.divider()

        # --- NEW SORTING & FILTERING FEATURE ---
        st.markdown("#### Filter Work Queue")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            # Add or remove departments here based on your backend logic
            filter_dept = st.selectbox("Department", [
                "All Departments", 
                "Housekeeping Department", 
                "Maintenance Department", 
                "Security & Discipline Cell", 
                "Academic Office", 
                "Mess Committee"
            ])
        with f_col2:
            filter_status = st.selectbox("Status", [
                "All Statuses", 
                "Submitted", 
                "In Progress", 
                "Resolved", 
                "Rejected"
            ])

        # Build the query parameters based on user selection
        api_params = {}
        if filter_dept != "All Departments":
            api_params["department"] = filter_dept
        if filter_status != "All Statuses":
            api_params["status"] = filter_status

        # Fetch problems using the new filters
        data, code = api_request("GET", "/admin/problems", params=api_params) 
        # ---------------------------------------
        
        st.divider()

        if code == 200 and data.get("problems"):
            st.caption(f"Showing {len(data['problems'])} ticket(s)")
            for p in data["problems"]:
                with st.expander(f"[{p['status'].upper()}] {p['tracking_id']} - {p.get('department', 'Unassigned')}"):
                    st.write(f"**Reported by:** {p['student_name']}")
                    st.write(f"**Issue:** {p['description']}")
                    
                    # Ensure the selectbox defaults to the current status
                    current_status = p.get("status", "Submitted")
                    status_options = ["Submitted", "In Progress", "Resolved", "Rejected"]
                    default_index = status_options.index(current_status) if current_status in status_options else 0
                    
                    new_status = st.selectbox(
                        "Update Status", 
                        status_options, 
                        index=default_index,
                        key=f"s_{p['id']}"
                    )
                    
                    note = st.text_input("Resolution Note", value=p.get("resolution", ""), key=f"n_{p['id']}")
                    if st.button("Save Changes", key=f"btn_{p['id']}", type="primary"):
                        api_request("PUT", f"/admin/problem/{p['id']}", {"status": new_status, "resolution": note})
                        st.success("Ticket updated!")
                        st.rerun()
        else:
            st.info("No active issues match this filter. Queue is clear!")
            
    st.markdown("</div>", unsafe_allow_html=True)