import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

CATEGORY_ICONS = {
    "Bathroom & Hygiene":         "🚽",
    "Anti-Ragging & Safety":      "🛡️",
    "Mess & Food Quality":        "🍽️",
    "Academic Issues":            "📚",
    "Infrastructure/Maintenance": "🔧",
    "Other":                      "📌",
}

STATUS_COLORS = {
    "Submitted":   "🔵",
    "In Progress": "🟡",
    "Resolved":    "🟢",
    "Rejected":    "🔴",
}

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Campus Problem Solver",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main { padding-top: 0.5rem; }
    section[data-testid="stSidebar"] { background: #0f172a; }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    .tracking-card {
        background: linear-gradient(135deg, #1e3a5f, #0f172a);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        color: white;
        margin: 1rem 0;
    }
    .stat-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .problem-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .problem-card.resolved { border-left-color: #22c55e; }
    .problem-card.in-progress { border-left-color: #f59e0b; }
    .problem-card.rejected { border-left-color: #ef4444; }
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 99px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 4px;
    }
    .badge-blue   { background:#dbeafe; color:#1d4ed8; }
    .badge-green  { background:#dcfce7; color:#15803d; }
    .badge-yellow { background:#fef9c3; color:#a16207; }
    .badge-red    { background:#fee2e2; color:#b91c1c; }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    .confidence-bar {
        background: #e2e8f0;
        border-radius: 99px;
        height: 8px;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def api_get(endpoint, params=None):
    try:
        r = requests.get(f"{BACKEND_URL}{endpoint}", params=params, timeout=15)
        return r.json(), r.status_code
    except Exception as e:
        return {"detail": str(e)}, 500

def api_post(endpoint, payload):
    try:
        r = requests.post(f"{BACKEND_URL}{endpoint}", json=payload, timeout=30)
        return r.json(), r.status_code
    except Exception as e:
        return {"detail": str(e)}, 500

def api_put(endpoint, payload):
    try:
        r = requests.put(f"{BACKEND_URL}{endpoint}", json=payload, timeout=15)
        return r.json(), r.status_code
    except Exception as e:
        return {"detail": str(e)}, 500

def status_badge(status):
    icon = STATUS_COLORS.get(status, "⚪")
    color = {"Submitted":"badge-blue","In Progress":"badge-yellow",
             "Resolved":"badge-green","Rejected":"badge-red"}.get(status,"badge-blue")
    return f'<span class="badge {color}">{icon} {status}</span>'

def confidence_bar(score: float):
    pct = int(score * 100)
    color = "#22c55e" if pct >= 75 else "#f59e0b" if pct >= 50 else "#ef4444"
    return f"""
    <div style='font-size:0.8rem;color:#64748b'>Confidence: <b>{pct}%</b></div>
    <div class='confidence-bar'>
      <div style='width:{pct}%;background:{color};height:8px;border-radius:99px'></div>
    </div>"""

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 Campus Problem Solver")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["📝 Submit Problem", "🔍 Track My Problem", "🛠️ Admin Dashboard", "📊 Statistics"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    try:
        data, code = api_get("/")
        if code == 200:
            st.success("✅ Backend online")
        else:
            st.error("❌ Backend error")
    except:
        st.error("❌ Backend offline")
    st.caption(f"API: {BACKEND_URL}")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — SUBMIT PROBLEM
# ══════════════════════════════════════════════════════════════════════════════
if page == "📝 Submit Problem":
    st.title("📝 Submit a Campus Problem")
    st.markdown("Fill in the form below. Our AI will classify your problem and route it to the right department.")
    st.markdown("---")

    col1, col2 = st.columns([3, 2])

    with col1:
        with st.form("submit_form", clear_on_submit=False):
            st.subheader("Problem Details")
            student_name  = st.text_input("Your Full Name *", placeholder="e.g. Rahul Sharma")
            student_email = st.text_input("Email (optional)", placeholder="e.g. rahul@college.edu")
            description   = st.text_area(
                "Describe Your Problem *",
                placeholder='e.g. "The bathroom on the 3rd floor of Hostel B has no running water since yesterday morning."',
                height=160,
            )
            submitted = st.form_submit_button("🚀 Submit Problem", use_container_width=True)

        if submitted:
            if not student_name.strip():
                st.warning("⚠️ Please enter your name.")
            elif len(description.strip()) < 10:
                st.warning("⚠️ Please describe your problem in at least 10 characters.")
            else:
                with st.spinner("🤖 AI is classifying your problem..."):
                    data, code = api_post("/submit", {
                        "student_name": student_name,
                        "student_email": student_email,
                        "description": description,
                    })
                if code == 200:
                    st.success("✅ Problem submitted successfully!")
                    st.markdown(f"""
                    <div class='tracking-card'>
                        <h3 style='color:#60a5fa;margin:0'>Your Tracking ID</h3>
                        <h1 style='color:white;font-family:monospace;margin:0.5rem 0'>{data['tracking_id']}</h1>
                        <p style='color:#94a3b8;margin:0'>Save this ID to track your problem status</p>
                        <hr style='border-color:#334155;margin:1rem 0'>
                        <b style='color:#e2e8f0'>🏷️ Category:</b>
                        <span style='color:#60a5fa'> {CATEGORY_ICONS.get(data['category'],'')} {data['category']}</span><br>
                        <b style='color:#e2e8f0'>🏢 Routed to:</b>
                        <span style='color:#4ade80'> {data['department']}</span><br>
                        <b style='color:#e2e8f0'>📊 Status:</b>
                        <span style='color:#fbbf24'> 🔵 Submitted</span>
                    </div>
                    """, unsafe_allow_html=True)
                    conf_pct = int(data['confidence'] * 100)
                    st.markdown(confidence_bar(data['confidence']), unsafe_allow_html=True)
                else:
                    st.error(f"❌ Error: {data.get('detail','Unknown error')}")

    with col2:
        st.subheader("📋 How it works")
        st.markdown("""
        1. **Submit** your problem with a description
        2. **AI classifies** it into the right category
        3. **Auto-routed** to the correct department
        4. **Track** progress using your Tracking ID
        5. **Get notified** when resolved
        """)
        st.markdown("---")
        st.subheader("🏷️ Categories")
        for cat, icon in CATEGORY_ICONS.items():
            st.markdown(f"{icon} {cat}")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — TRACK MY PROBLEM
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Track My Problem":
    st.title("🔍 Track Your Problem")
    st.markdown("Enter your Tracking ID to see the current status of your submitted problem.")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        tracking_input = st.text_input(
            "Tracking ID",
            placeholder="e.g. CPS-A1B2C3D4",
            help="You received this when you submitted your problem."
        ).strip().upper()
        search_btn = st.button("🔎 Track Problem", use_container_width=False)

    if search_btn:
        if not tracking_input:
            st.warning("Please enter a Tracking ID.")
        else:
            with st.spinner("Fetching your problem status..."):
                data, code = api_get(f"/track/{tracking_input}")

            if code == 200:
                status = data.get("status", "Unknown")
                icon   = STATUS_COLORS.get(status, "⚪")
                cat    = data.get("category", "Other")

                st.markdown(f"""
                <div class='tracking-card'>
                    <div style='display:flex;justify-content:space-between;align-items:start'>
                        <div>
                            <p style='color:#94a3b8;margin:0;font-size:0.85rem'>TRACKING ID</p>
                            <h2 style='color:white;font-family:monospace;margin:0'>{data['tracking_id']}</h2>
                        </div>
                        <div style='text-align:right'>
                            <p style='color:#94a3b8;margin:0;font-size:0.85rem'>STATUS</p>
                            <h3 style='color:#fbbf24;margin:0'>{icon} {status}</h3>
                        </div>
                    </div>
                    <hr style='border-color:#334155;margin:1rem 0'>
                    <b style='color:#e2e8f0'>👤 Name:</b> <span style='color:#cbd5e1'>{data['student_name']}</span><br>
                    <b style='color:#e2e8f0'>🏷️ Category:</b> <span style='color:#60a5fa'>{CATEGORY_ICONS.get(cat,'')} {cat}</span><br>
                    <b style='color:#e2e8f0'>🏢 Department:</b> <span style='color:#4ade80'>{data.get('department','—')}</span><br>
                    <b style='color:#e2e8f0'>📅 Submitted:</b> <span style='color:#cbd5e1'>{str(data.get('created_at',''))[:19].replace('T',' ')}</span>
                </div>
                """, unsafe_allow_html=True)

                st.subheader("📄 Your Problem")
                st.info(data.get("description", ""))

                if data.get("resolution"):
                    st.subheader("✅ Resolution from Admin")
                    st.success(data["resolution"])

                if data.get("updated_at") and data["updated_at"] != data.get("created_at"):
                    st.caption(f"Last updated: {str(data['updated_at'])[:19].replace('T',' ')}")

                # Status timeline
                st.subheader("📍 Status Timeline")
                stages = ["Submitted", "In Progress", "Resolved"]
                cols = st.columns(len(stages))
                for i, (stage, col) in enumerate(zip(stages, cols)):
                    reached = stages.index(status) >= i if status in stages else i == 0
                    with col:
                        if reached:
                            st.markdown(f"**🟢 {stage}**")
                        else:
                            st.markdown(f"⚪ {stage}")

            elif code == 404:
                st.error(f"❌ No problem found with tracking ID **{tracking_input}**. Please check and try again.")
            else:
                st.error(f"❌ Error: {data.get('detail', 'Unknown error')}")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — ADMIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🛠️ Admin Dashboard":
    st.title("🛠️ Admin / Executive Dashboard")

    # Simple password gate
    if "admin_auth" not in st.session_state:
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        st.markdown("This area is restricted to administrators.")
        pwd = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.caption("Default password: `admin123` — set ADMIN_PASSWORD in your environment to change it.")
        st.stop()

    st.success("✅ Logged in as Admin")
    if st.button("Logout"):
        st.session_state.admin_auth = False
        st.rerun()

    st.markdown("---")

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filter_status = st.selectbox("Filter by Status", ["All", "Submitted", "In Progress", "Resolved", "Rejected"])
    with col_f2:
        filter_dept = st.selectbox("Filter by Department", [
            "All", "Housekeeping Department", "Security & Discipline Cell",
            "Mess Committee", "Academic Office", "Maintenance Department", "General Administration"
        ])
    with col_f3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    params = {}
    if filter_status != "All":
        params["status"] = filter_status
    if filter_dept != "All":
        params["department"] = filter_dept

    data, code = api_get("/admin/problems", params=params)

    if code != 200:
        st.error(f"Failed to load problems: {data.get('detail','')}")
        st.stop()

    problems = data.get("problems", [])
    total    = data.get("total", 0)

    # Quick counts
    c1, c2, c3, c4 = st.columns(4)
    status_counts = {}
    for p in problems:
        s = p.get("status","Unknown")
        status_counts[s] = status_counts.get(s, 0) + 1

    c1.metric("Total",       total)
    c2.metric("🔵 Submitted",  status_counts.get("Submitted", 0))
    c3.metric("🟡 In Progress",status_counts.get("In Progress", 0))
    c4.metric("🟢 Resolved",   status_counts.get("Resolved", 0))

    st.markdown("---")

    if not problems:
        st.info("No problems found matching the selected filters.")
    else:
        for p in problems:
            status  = p.get("status", "Submitted")
            cat     = p.get("category", "Other")
            card_cls = {"In Progress":"in-progress","Resolved":"resolved","Rejected":"rejected"}.get(status,"")

            with st.expander(
                f"{STATUS_COLORS.get(status,'⚪')} #{p['id']} | "
                f"{CATEGORY_ICONS.get(cat,'')} {cat} | "
                f"{p['student_name']} | "
                f"{str(p.get('created_at',''))[:10]}"
            ):
                col_info, col_action = st.columns([3, 2])

                with col_info:
                    st.markdown(f"**🆔 Tracking ID:** `{p['tracking_id']}`")
                    st.markdown(f"**👤 Student:** {p['student_name']} "
                                + (f"({p['student_email']})" if p.get('student_email') else ""))
                    st.markdown(f"**🏢 Department:** {p.get('department','—')}")
                    st.markdown(confidence_bar(p.get("confidence", 0.75)), unsafe_allow_html=True)
                    st.markdown(f"**📄 Problem:**")
                    st.info(p.get("description", ""))
                    if p.get("reason"):
                        st.caption(f"AI reason: {p['reason']}")
                    if p.get("resolution"):
                        st.success(f"**Resolution:** {p['resolution']}")

                with col_action:
                    st.markdown("**✏️ Update Status**")
                    new_status = st.selectbox(
                        "Status",
                        ["Submitted", "In Progress", "Resolved", "Rejected"],
                        index=["Submitted","In Progress","Resolved","Rejected"].index(status),
                        key=f"status_{p['id']}",
                    )
                    resolution_text = st.text_area(
                        "Resolution / Comment",
                        value=p.get("resolution", ""),
                        placeholder="Add a response or resolution note...",
                        height=100,
                        key=f"res_{p['id']}",
                    )
                    if st.button("💾 Save Update", key=f"save_{p['id']}", use_container_width=True):
                        resp, rcode = api_put(f"/admin/problem/{p['id']}", {
                            "status":     new_status,
                            "resolution": resolution_text,
                        })
                        if rcode == 200:
                            st.success("✅ Updated successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ {resp.get('detail','Update failed')}")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — STATISTICS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Statistics":
    st.title("📊 Campus Problem Statistics")
    st.markdown("Overview of all submitted problems and their resolution status.")
    st.markdown("---")

    data, code = api_get("/admin/stats")
    if code != 200:
        st.error("Could not load statistics.")
        st.stop()

    total       = data.get("total", 0)
    by_status   = data.get("by_status", {})
    by_category = data.get("by_category", {})
    by_dept     = data.get("by_department", {})

    # Top metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Total Problems",   total)
    c2.metric("🟢 Resolved",         by_status.get("Resolved", 0))
    c3.metric("🟡 In Progress",      by_status.get("In Progress", 0))
    c4.metric("🔵 Submitted",        by_status.get("Submitted", 0))

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("By Category")
        if by_category:
            for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
                pct = int(count / total * 100) if total else 0
                icon = CATEGORY_ICONS.get(cat, "📌")
                st.markdown(f"{icon} **{cat}**")
                st.progress(pct / 100, text=f"{count} problems ({pct}%)")
        else:
            st.info("No data yet.")

    with col2:
        st.subheader("By Department")
        if by_dept:
            for dept, count in sorted(by_dept.items(), key=lambda x: -x[1]):
                pct = int(count / total * 100) if total else 0
                st.markdown(f"🏢 **{dept}**")
                st.progress(pct / 100, text=f"{count} problems ({pct}%)")
        else:
            st.info("No data yet.")

    st.markdown("---")
    st.subheader("Resolution Status Breakdown")
    if by_status:
        for status, count in by_status.items():
            pct = int(count / total * 100) if total else 0
            icon = STATUS_COLORS.get(status, "⚪")
            st.markdown(f"{icon} **{status}**: {count} ({pct}%)")
    else:
        st.info("No data yet.")

    if st.button("🔄 Refresh Stats"):
        st.rerun()
