import streamlit as st
import requests
import os
from dotenv import load_dotenv

# load environment variables (plz don't leak the env file again)
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
# TODO: change this to a real db auth later, hardcoding for the hackathon
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Renamed these to sound like actual college problems
CATEGORY_ICONS = {
    "Gross Bathrooms":            "🚽",
    "Safety / Ragging":           "🛡️",
    "Trash Mess Food":            "🍽️",
    "Prof/Class Drama":           "📚",
    "Broken Stuff (Fan/Light)":   "🔧",
    "Something Else":             "📌",
}

STATUS_COLORS = {
    "Submitted":   "🔵",
    "In Progress": "🟡",
    "Resolved":    "🟢",
    "Rejected":    "🔴",
}

# ── Page Config (don't touch this, it breaks the layout somehow) ──────────────
st.set_page_config(
    page_title="Hostel Fix-It / Rant Board",
    page_icon="🤡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS (spent 3 hours on this, pls appreciate)
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

# ── API Helpers ───────────────────────────────────────────────────────────────
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
    <div style='font-size:0.8rem;color:#64748b'>AI Confidence: <b>{pct}%</b></div>
    <div class='confidence-bar'>
      <div style='width:{pct}%;background:{color};height:8px;border-radius:99px'></div>
    </div>"""

# ── Sidebar Nav ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤡 Campus Fix-It App")
    st.markdown("---")
    page = st.radio(
        "Where to?",
        ["📝 Rant / Report Issue", "🔍 Track My Complaint", "🛠️ Admin Only", "📊 The Damage (Stats)"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    
    # Quick health check
    try:
        data, code = api_get("/")
        if code == 200:
            st.success("✅ Backend is awake")
        else:
            st.error("❌ Backend is throwing a tantrum")
    except:
        st.error("❌ Backend is dead (did the server crash again?)")
    st.caption(f"API: {BACKEND_URL}")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — SUBMIT PROBLEM
# ══════════════════════════════════════════════════════════════════════════════
if page == "📝 Rant / Report Issue":
    st.title("📝 Spill it. What's broken?")
    st.markdown("Drop your issue below. The AI will try to figure out which department to annoy about it.")
    st.markdown("---")

    col1, col2 = st.columns([3, 2])

    with col1:
        with st.form("submit_form", clear_on_submit=False):
            st.subheader("The Details")
            student_name  = st.text_input("Who are you? *", placeholder="e.g. Rahul from Hostel B")
            student_email = st.text_input("Email (optional)", placeholder="so we can update you")
            description   = st.text_area(
                "What's wrong? *",
                placeholder='e.g. "The 3rd floor Wi-Fi has been dead for 3 days and I have an assignment due..."',
                height=160,
            )
            submitted = st.form_submit_button("🚀 Yeet complaint to management", use_container_width=True)

        if submitted:
            if not student_name.strip():
                st.warning("⚠️ Bro, at least give us a name.")
            elif len(description.strip()) < 10:
                st.warning("⚠️ That's too short. Give us some details.")
            else:
                with st.spinner("🤖 AI is reading your mind (and routing your issue)..."):
                    data, code = api_post("/submit", {
                        "student_name": student_name,
                        "student_email": student_email,
                        "description": description,
                    })
                if code == 200:
                    st.balloons() # cause why not
                    st.success("✅ Sent! Hopefully they actually fix it.")
                    st.markdown(f"""
                    <div class='tracking-card'>
                        <h3 style='color:#60a5fa;margin:0'>Your Receipt / Tracking ID</h3>
                        <h1 style='color:white;font-family:monospace;margin:0.5rem 0'>{data['tracking_id']}</h1>
                        <p style='color:#94a3b8;margin:0'>Screenshot this so you don't lose it</p>
                        <hr style='border-color:#334155;margin:1rem 0'>
                        <b style='color:#e2e8f0'>🏷️ Tagged as:</b>
                        <span style='color:#60a5fa'> {CATEGORY_ICONS.get(data['category'],'')} {data['category']}</span><br>
                        <b style='color:#e2e8f0'>🏢 Sent to:</b>
                        <span style='color:#4ade80'> {data['department']}</span><br>
                        <b style='color:#e2e8f0'>📊 Status:</b>
                        <span style='color:#fbbf24'> 🔵 Submitted</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(confidence_bar(data['confidence']), unsafe_allow_html=True)
                else:
                    st.error(f"❌ Big yikes: {data.get('detail','Unknown error')}")

    with col2:
        st.subheader("📋 How it works")
        st.markdown("""
        1. **Complain** about whatever is broken.
        2. **Our AI scripts** figure out who needs to fix it.
        3. **It gets forwarded** to the right office.
        4. **You track it** so they can't ghost you.
        """)
        st.markdown("---")
        st.subheader("🏷️ Stuff we track")
        for cat, icon in CATEGORY_ICONS.items():
            st.markdown(f"{icon} {cat}")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — TRACK MY PROBLEM
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Track My Complaint":
    st.title("🔍 Where's my complaint at?")
    st.markdown("Paste your tracking ID here to see if anyone has actually looked at your issue.")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        tracking_input = st.text_input(
            "Tracking ID",
            placeholder="e.g. CPS-A1B2C3D4",
        ).strip().upper()
        search_btn = st.button("🔎 Search", use_container_width=False)

    if search_btn:
        if not tracking_input:
            st.warning("You gotta enter an ID first.")
        else:
            with st.spinner("Digging through the database..."):
                data, code = api_get(f"/track/{tracking_input}")

            if code == 200:
                status = data.get("status", "Unknown")
                icon   = STATUS_COLORS.get(status, "⚪")
                cat    = data.get("category", "Something Else")

                st.markdown(f"""
                <div class='tracking-card'>
                    <div style='display:flex;justify-content:space-between;align-items:start'>
                        <div>
                            <p style='color:#94a3b8;margin:0;font-size:0.85rem'>TRACKING ID</p>
                            <h2 style='color:white;font-family:monospace;margin:0'>{data['tracking_id']}</h2>
                        </div>
                        <div style='text-align:right'>
                            <p style='color:#94a3b8;margin:0;font-size:0.85rem'>CURRENT STATUS</p>
                            <h3 style='color:#fbbf24;margin:0'>{icon} {status}</h3>
                        </div>
                    </div>
                    <hr style='border-color:#334155;margin:1rem 0'>
                    <b style='color:#e2e8f0'>👤 Who:</b> <span style='color:#cbd5e1'>{data['student_name']}</span><br>
                    <b style='color:#e2e8f0'>🏷️ Type:</b> <span style='color:#60a5fa'>{CATEGORY_ICONS.get(cat,'')} {cat}</span><br>
                    <b style='color:#e2e8f0'>🏢 Handling it:</b> <span style='color:#4ade80'>{data.get('department','—')}</span><br>
                    <b style='color:#e2e8f0'>📅 Sent on:</b> <span style='color:#cbd5e1'>{str(data.get('created_at',''))[:19].replace('T',' ')}</span>
                </div>
                """, unsafe_allow_html=True)

                st.subheader("📄 What you said:")
                st.info(data.get("description", ""))

                if data.get("resolution"):
                    st.subheader("✅ What Admin said:")
                    st.success(data["resolution"])

                if data.get("updated_at") and data["updated_at"] != data.get("created_at"):
                    st.caption(f"Last updated: {str(data['updated_at'])[:19].replace('T',' ')}")

                st.subheader("📍 Progress")
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
                st.error(f"❌ Couldn't find **{tracking_input}**. Did you type it right?")
            else:
                st.error(f"❌ Server error: {data.get('detail', 'idk man')}")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — ADMIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🛠️ Admin Only":
    st.title("🛠️ Admin Zone")

    # Cheap auth for now
    if "admin_auth" not in st.session_state:
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        st.warning("Are you supposed to be here?")
        pwd = st.text_input("Password", type="password")
        if st.button("Hack In (Login)"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Nah, try again.")
        st.stop()

    st.success("✅ We're in.")
    if st.button("Logout"):
        st.session_state.admin_auth = False
        st.rerun()

    st.markdown("---")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filter_status = st.selectbox("Show me:", ["All", "Submitted", "In Progress", "Resolved", "Rejected"])
    with col_f2:
        filter_dept = st.selectbox("Department filter:", [
            "All", "Housekeeping", "Security",
            "Mess Committee", "Academics", "Maintenance", "General Admin"
        ])
    with col_f3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

    params = {}
    if filter_status != "All":
        params["status"] = filter_status
    if filter_dept != "All":
        params["department"] = filter_dept

    data, code = api_get("/admin/problems", params=params)

    if code != 200:
        st.error(f"API choked: {data.get('detail','')}")
        st.stop()

    problems = data.get("problems", [])
    total    = data.get("total", 0)

    c1, c2, c3, c4 = st.columns(4)
    status_counts = {}
    for p in problems:
        s = p.get("status","Unknown")
        status_counts[s] = status_counts.get(s, 0) + 1

    c1.metric("Total Headaches", total)
    c2.metric("🔵 New", status_counts.get("Submitted", 0))
    c3.metric("🟡 Doing it", status_counts.get("In Progress", 0))
    c4.metric("🟢 Done", status_counts.get("Resolved", 0))

    st.markdown("---")

    if not problems:
        st.info("Wow, an empty queue. Go take a nap.")
    else:
        for p in problems:
            status  = p.get("status", "Submitted")
            cat     = p.get("category", "Something Else")
            
            # Using st.expander for the accordian vibe
            with st.expander(
                f"{STATUS_COLORS.get(status,'⚪')} {p['tracking_id']} | "
                f"{CATEGORY_ICONS.get(cat,'')} {cat} | "
                f"{p['student_name']}"
            ):
                col_info, col_action = st.columns([3, 2])

                with col_info:
                    st.markdown(f"**👤 Student:** {p['student_name']} "
                                + (f"({p['student_email']})" if p.get('student_email') else ""))
                    st.markdown(f"**🏢 Department:** {p.get('department','—')}")
                    st.markdown(confidence_bar(p.get("confidence", 0.75)), unsafe_allow_html=True)
                    st.markdown(f"**📄 The Rant:**")
                    st.info(p.get("description", ""))
                    if p.get("reason"):
                        st.caption(f"Why AI picked this route: {p['reason']}")
                    if p.get("resolution"):
                        st.success(f"**Current Note:** {p['resolution']}")

                with col_action:
                    st.markdown("**✏️ Action Items**")
                    new_status = st.selectbox(
                        "Change Status",
                        ["Submitted", "In Progress", "Resolved", "Rejected"],
                        index=["Submitted","In Progress","Resolved","Rejected"].index(status),
                        key=f"status_{p['id']}",
                    )
                    resolution_text = st.text_area(
                        "Reply / Notes",
                        value=p.get("resolution", ""),
                        placeholder="Tell them it's fixed...",
                        height=100,
                        key=f"res_{p['id']}",
                    )
                    if st.button("💾 Save", key=f"save_{p['id']}", use_container_width=True):
                        resp, rcode = api_put(f"/admin/problem/{p['id']}", {
                            "status":     new_status,
                            "resolution": resolution_text,
                        })
                        if rcode == 200:
                            st.success("✅ Saved!")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed: {resp.get('detail','Bruh idk')}")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — STATISTICS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 The Damage (Stats)":
    st.title("📊 The Damage Report")
    st.markdown("Visualizing exactly how broken our campus is right now.")
    st.markdown("---")

    data, code = api_get("/admin/stats")
    if code != 200:
        st.error("API broke while fetching stats. Ironic.")
        st.stop()

    total       = data.get("total", 0)
    by_status   = data.get("by_status", {})
    by_category = data.get("by_category", {})
    by_dept     = data.get("by_department", {})

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Total Issues", total)
    c2.metric("🟢 Fixed", by_status.get("Resolved", 0))
    c3.metric("🟡 Working on it", by_status.get("In Progress", 0))
    c4.metric("🔵 Ignored (so far)", by_status.get("Submitted", 0))

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("What's breaking the most?")
        if by_category:
            for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
                pct = int(count / total * 100) if total else 0
                icon = CATEGORY_ICONS.get(cat, "📌")
                st.markdown(f"{icon} **{cat}**")
                st.progress(pct / 100, text=f"{count} complaints ({pct}%)")
        else:
            st.info("Nothing yet. Campus is perfect? Sus.")

    with col2:
        st.subheader("Who has the most work?")
        if by_dept:
            for dept, count in sorted(by_dept.items(), key=lambda x: -x[1]):
                pct = int(count / total * 100) if total else 0
                st.markdown(f"🏢 **{dept}**")
                st.progress(pct / 100, text=f"{count} tasks ({pct}%)")
        else:
            st.info("All depts are chilling right now.")

    st.markdown("---")
    
    if st.button("🔄 Refresh Data"):
        st.rerun()